from __future__ import annotations

import json
import logging

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from app.models.events import EventIn, EventOut
from app.services.supabase_client import insert_event, recent_events

logger = logging.getLogger(__name__)
router = APIRouter()

# In-process WebSocket broadcast set
_connections: set[WebSocket] = set()


async def _broadcast_raw(payload: str) -> None:
    stale: list[WebSocket] = []
    for ws in _connections:
        try:
            await ws.send_text(payload)
        except Exception:
            stale.append(ws)
    for ws in stale:
        _connections.discard(ws)


async def _broadcast(event: EventOut) -> None:
    await _broadcast_raw(event.model_dump_json())


async def _broadcast_presence() -> None:
    msg = json.dumps({"type": "presence", "count": len(_connections)})
    await _broadcast_raw(msg)


@router.post("/api/events")
async def receive_event(event: EventIn):
    # Validate questionnaire_response events
    if event.event_type == "questionnaire_response":
        text = event.raw_properties.get("response_text")
        if not text or not isinstance(text, str) or not text.strip():
            raise HTTPException(status_code=422, detail="response_text is required")
        if len(text) > 500:
            raise HTTPException(status_code=422, detail="response_text must be 500 characters or fewer")

    saved = insert_event(event)
    await _broadcast(saved)
    return {"status": "ok", "id": saved.id}


@router.websocket("/ws/events")
async def event_stream(ws: WebSocket):
    await ws.accept()
    _connections.add(ws)
    await _broadcast_presence()
    try:
        # Backfill last 50 events so the stream isn't blank
        history = recent_events(limit=50)
        # Send oldest-first so newest ends up on top in the UI
        for ev in reversed(history):
            await ws.send_text(ev.model_dump_json())
        # Keep connection alive; we only send from broadcast
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        _connections.discard(ws)
        await _broadcast_presence()
