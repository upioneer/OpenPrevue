"""Pydantic schemas for Emergency Alert System (EAS) and public safety bulletins."""

from datetime import datetime
from pydantic import BaseModel, Field


class EmergencyAlert(BaseModel):
    """Normalized emergency alert entity representing meteorological, geophysical, or civil threats."""

    id: str
    sender: str
    headline: str
    severity: str = "Severe"  # Extreme, Severe, Moderate, Minor
    urgency: str = "Immediate"  # Immediate, Expected, Future
    event_type: str  # TORNADO WARNING, FLASH FLOOD WARNING, EARTHQUAKE, CIVIL EMERGENCY, AMBER ALERT
    area_description: str
    instruction: str | None = None
    effective_at: str | datetime
    expires_at: str | datetime
    is_active: bool = True


class EASTestRequest(BaseModel):
    """Payload to trigger a simulated emergency broadcast test."""

    event_type: str = "CIVIL EMERGENCY"
    headline: str = "EMERGENCY BROADCAST SYSTEM TEST - LOCAL AREA"
    severity: str = "Severe"
    area_description: str = "LOCAL RECEPTION AREA"
    instruction: str = "This is a test of the OpenPrevue Emergency Alert System. No action is required."
    duration_seconds: int = 30
