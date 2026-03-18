from __future__ import annotations

import logging

import requests as http_requests
import stripe
from fastapi import APIRouter, HTTPException, Request

from app.config import settings
from app.models.events import EventIn, EventOut
from app.routes.events import _broadcast
from app.services.supabase_client import insert_event

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/api/checkout/create-session")
async def create_checkout_session(request: Request):
    body = await request.json()
    item_id = body.get("item_id")
    item_name = body.get("item_name")
    price = body.get("price")

    if item_id != "keep-the-lights-on":
        raise HTTPException(status_code=422, detail="Only keep-the-lights-on is available")
    if not isinstance(price, (int, float)) or price <= 0 or price > 999:
        raise HTTPException(status_code=422, detail="Price must be between $1 and $999")

    stripe.api_key = settings.stripe_secret_key

    # Build redirect URLs from the incoming request so they work on any domain
    origin = f"{request.url.scheme}://{request.url.netloc}"

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "usd",
                "unit_amount": int(round(price * 100)),
                "product_data": {
                    "name": item_name or "keep the lights on",
                },
            },
            "quantity": 1,
        }],
        success_url=f"{origin}/?checkout=success",
        cancel_url=f"{origin}/?checkout=cancel",
        metadata={
            "item_id": item_id,
            "item_name": item_name or "keep the lights on",
        },
    )

    return {"url": session.url}


@router.post("/api/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})
        item_id = metadata.get("item_id", "unknown")
        item_name = metadata.get("item_name", "unknown")
        amount_total = session.get("amount_total", 0)
        price_dollars = amount_total / 100

        # Insert purchase_complete event into Supabase
        ev_in = EventIn(
            event_type="purchase_complete",
            raw_properties={
                "item_id": item_id,
                "item_name": item_name,
                "price": price_dollars,
                "stripe_session_id": session.get("id", ""),
            },
        )
        saved: EventOut = insert_event(ev_in)

        # Broadcast to live stream
        await _broadcast(saved)

        # Send to PostHog so it flows through the BigQuery export pipeline
        try:
            http_requests.post(
                f"{settings.posthog_host}/capture/",
                json={
                    "api_key": settings.posthog_api_key,
                    "event": "purchase_complete",
                    "distinct_id": "stripe-webhook",
                    "properties": {
                        "item_id": item_id,
                        "item_name": item_name,
                        "price": price_dollars,
                        "stripe_session_id": session.get("id", ""),
                    },
                },
                timeout=5,
            )
        except Exception:
            logger.warning("Failed to send purchase_complete to PostHog")

        logger.info(
            "purchase_complete: %s $%.2f (session %s)",
            item_name, price_dollars, session.get("id"),
        )

    return {"status": "ok"}
