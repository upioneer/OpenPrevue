"""Pydantic models for Venues."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class VenueBase(BaseModel):
    """Base venue attributes."""
    name: str
    address: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timezone: str = "America/Chicago"
    custom_order: int = 999
    is_active: int = 1
    needs_review: int = 0


class VenueCreate(VenueBase):
    """Payload for creating a new venue."""
    id: str = Field(..., description="Canonical unique identifier e.g. saenger-theatre")


class VenueUpdate(BaseModel):
    """Payload for updating venue fields."""
    name: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timezone: str | None = None
    custom_order: int | None = None
    is_active: int | None = None
    needs_review: int | None = None


class VenueResponse(VenueBase):
    """Complete venue response model."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: str | datetime
    updated_at: str | datetime
