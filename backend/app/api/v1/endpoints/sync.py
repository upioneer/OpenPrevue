"""Data synchronization and audit log API endpoints."""

from datetime import datetime, timezone
from fastapi import APIRouter, Query
from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.providers.base import GeoPoint
from backend.app.providers.registry import provider_registry
from backend.app.schemas.health import IngestionLogEntry, SyncTriggerResponse
from backend.app.services.ingestion import ingestion_service

router = APIRouter()


@router.post("/sync", response_model=SyncTriggerResponse)
async def trigger_sync() -> SyncTriggerResponse:
    """Trigger an immediate ingestion synchronization cycle across all registered providers."""
    started_at = datetime.now(timezone.utc).isoformat()

    # Read active location coordinates from settings
    async with get_db() as db:
        async with db.execute("SELECT key, value FROM settings WHERE key IN ('latitude', 'longitude', 'radius_miles')") as cursor:
            rows = await cursor.fetchall()
            settings_map = {row["key"]: row["value"] for row in rows}

    lat = float(settings_map.get("latitude", settings.DEFAULT_LATITUDE))
    lon = float(settings_map.get("longitude", settings.DEFAULT_LONGITUDE))
    radius = float(settings_map.get("radius_miles", settings.DEFAULT_RADIUS_MILES))

    center = GeoPoint(latitude=lat, longitude=lon)

    # Sync each registered provider
    for provider in provider_registry.get_all():
        await ingestion_service.sync_provider(provider, center, radius)

    return SyncTriggerResponse(
        status="completed",
        message="Manual synchronization cycle finished",
        started_at=started_at,
    )


@router.get("/sync/logs", response_model=list[IngestionLogEntry])
async def list_ingestion_logs(
    limit: int = Query(50, ge=1, le=200),
) -> list[IngestionLogEntry]:
    """Retrieve historical ingestion audit log entries."""
    query = "SELECT * FROM ingestion_log ORDER BY id DESC LIMIT ?"
    async with get_db() as db:
        async with db.execute(query, (limit,)) as cursor:
            rows = await cursor.fetchall()
            return [IngestionLogEntry(**dict(row)) for row in rows]
