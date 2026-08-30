"""Pydantic models for Health and Ingestion Status."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ProviderHealth(BaseModel):
    """Health and metric summary for a single ingestion provider."""
    status: str
    last_sync: str | datetime | None = None
    events_cached: int = 0
    error: str | None = None
    reason: str | None = None


class HealthResponse(BaseModel):
    """System-wide composite health check response."""
    status: str
    uptime_seconds: float
    database: str
    scheduler: str
    providers: dict[str, ProviderHealth]
    telegram_bot: str
    next_sync: str | datetime | None = None


class IngestionLogEntry(BaseModel):
    """Audit log record for an ingestion execution."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider: str
    started_at: str | datetime
    completed_at: str | datetime | None = None
    status: str
    events_fetched: int
    events_inserted: int
    events_updated: int
    events_skipped: int
    error_message: str | None = None


class SyncTriggerResponse(BaseModel):
    """Response returned when triggering an immediate synchronization."""
    status: str
    message: str
    started_at: str
