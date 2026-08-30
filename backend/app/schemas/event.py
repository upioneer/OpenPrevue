"""Pydantic models for Events and Ticket Links."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class TicketLinkResponse(BaseModel):
    """Aggregated ticket purchasing link."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    url: str
    label: str | None = None
    created_at: str | datetime


class EventBase(BaseModel):
    """Base event attributes."""
    venue_id: str
    title: str
    description: str | None = None
    category: str = "other"
    start_time: str
    end_time: str | None = None
    price_min: float | None = None
    price_max: float | None = None
    currency: str = "USD"
    image_url: str | None = None
    ticket_url: str
    source: str
    source_event_id: str | None = None
    is_featured: int = 0
    has_ticket: int = 0
    status: str = "active"


class EventCreate(EventBase):
    """Payload for inserting an event."""
    id: str = Field(..., description="Unique event identifier")


class EventUpdate(BaseModel):
    """Payload for patching an existing event."""
    venue_id: str | None = None
    title: str | None = None
    description: str | None = None
    category: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    price_min: float | None = None
    price_max: float | None = None
    currency: str | None = None
    image_url: str | None = None
    ticket_url: str | None = None
    is_featured: int | None = None
    has_ticket: int | None = None
    status: str | None = None


class EventResponse(EventBase):
    """Complete event response including venue details and ticket links."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    venue_name: str | None = None
    venue_address: str | None = None
    venue_city: str | None = None
    venue_state: str | None = None
    last_seen_at: str | datetime
    created_at: str | datetime
    updated_at: str | datetime
    ticket_links: list[TicketLinkResponse] = Field(default_factory=list)
