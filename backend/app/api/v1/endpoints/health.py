"""Health and system observability API endpoints."""

import time
from datetime import datetime, timezone
from fastapi import APIRouter
import aiosqlite

from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.schemas.health import HealthResponse, ProviderHealth
from backend.app.services.speech import speech_service

router = APIRouter()
START_TIME = time.time()


@router.get("/health", response_model=HealthResponse)
async def get_system_health() -> HealthResponse:
    """Return composite operational health status across database, providers, bot, and speech."""
    uptime = time.time() - START_TIME
    db_status = "ok"

    # Verify database connection
    try:
        async with get_db() as db:
            async with db.execute("SELECT 1") as cursor:
                await cursor.fetchone()
    except Exception:
        db_status = "unhealthy"

    # Query last sync and event count from SQLite
    provider_health_map: dict[str, ProviderHealth] = {}
    try:
        async with get_db() as db:
            async with db.execute("SELECT COUNT(*) AS count FROM events WHERE status = 'active'") as cursor:
                row = await cursor.fetchone()
                active_events = row["count"] if row else 0

            async with db.execute(
                """
                SELECT provider, started_at, status, error_message
                FROM ingestion_log
                ORDER BY id DESC
                LIMIT 10
                """
            ) as cursor:
                logs = await cursor.fetchall()
                for log in logs:
                    prov = log["provider"]
                    if prov not in provider_health_map:
                        provider_health_map[prov] = ProviderHealth(
                            status=log["status"],
                            last_sync=log["started_at"],
                            events_cached=active_events if prov == "mock" else 0,
                            error=log["error_message"],
                        )
    except Exception:
        pass

    if "mock" not in provider_health_map:
        provider_health_map["mock"] = ProviderHealth(
            status="ok",
            last_sync=datetime.now(timezone.utc).isoformat(),
            events_cached=0,
        )

    # Check external providers configured state
    if not settings.TICKETMASTER_API_KEY:
        provider_health_map["ticketmaster"] = ProviderHealth(
            status="disabled",
            reason="no_api_key",
        )
    if not settings.SEATGEEK_CLIENT_ID:
        provider_health_map["seatgeek"] = ProviderHealth(
            status="disabled",
            reason="no_api_key",
        )

    telegram_status = "connected" if settings.TELEGRAM_BOT_TOKEN else "disabled (no_token)"
    speech_health = await speech_service.check_health()

    overall_status = "healthy" if db_status == "ok" else "degraded"

    return HealthResponse(
        status=overall_status,
        uptime_seconds=round(uptime, 2),
        database=db_status,
        scheduler="ok",
        providers=provider_health_map,
        telegram_bot=telegram_status,
        speech=speech_health,
        next_sync=None,
    )
