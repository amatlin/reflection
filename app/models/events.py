from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EventIn(BaseModel):
    event_type: str
    page_path: str | None = None
    element_id: str | None = None
    element_tag: str | None = None
    element_text: str | None = None
    visitor_id: str | None = None
    raw_properties: dict[str, Any] = Field(default_factory=dict)


class EventOut(BaseModel):
    id: int
    timestamp: datetime
    event_type: str
    page_path: str | None = None
    element_id: str | None = None
    element_tag: str | None = None
    element_text: str | None = None
    visitor_id: str | None = None
    raw_properties: dict[str, Any] = Field(default_factory=dict)
