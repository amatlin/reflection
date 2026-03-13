from __future__ import annotations

from supabase import Client, create_client

from app.config import settings
from app.models.events import EventIn, EventOut

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key,
        )
    return _client


def insert_event(event: EventIn) -> EventOut:
    row = event.model_dump(mode="json")
    result = get_client().table("events").insert(row).execute()
    return EventOut(**result.data[0])


def recent_events(limit: int = 50) -> list[EventOut]:
    result = (
        get_client()
        .table("events")
        .select("*")
        .order("timestamp", desc=True)
        .limit(limit)
        .execute()
    )
    return [EventOut(**r) for r in result.data]
