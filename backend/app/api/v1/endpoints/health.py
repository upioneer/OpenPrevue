"""Health and system observability API endpoints."""

import os
import time
from datetime import datetime, timezone
from fastapi import APIRouter
import aiosqlite

from backend.app.core.circuit_breaker import circuit_registry
from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.schemas.health import HealthResponse, ProviderHealth
from backend.app.services.speech import speech_service
from backend.app.services.websocket import connection_manager

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

    # Collect circuit breaker states
    circuit_breakers_map = {
        name: breaker.state.value for name, breaker in circuit_registry._breakers.items()
    }

    # Inspect Docker socket mount
    docker_mounted = os.path.exists("/var/run/docker.sock")

    # Compile dynamic issue ledger
    issues: list[str] = []
    if db_status != "ok":
        issues.append("CRITICAL: SQLite database connection unhealthy or read-only")

    for name, breaker in circuit_registry._breakers.items():
        if breaker.state.value == "open":
            issues.append(f"WARNING: Circuit breaker for '{name}' is OPEN ({breaker.last_error or 'Too many failures'})")

    for prov_name, p_health in provider_health_map.items():
        if p_health.status in ("failed", "circuit_open") and p_health.error:
            issues.append(f"ERROR: Provider '{prov_name}' sync failure: {p_health.error}")

    if speech_health and speech_health.get("status") == "error":
        issues.append(f"WARNING: Speech synthesis engine error: {speech_health.get('error')}")

    overall_status = "healthy" if db_status == "ok" and not any("CRITICAL" in i for i in issues) else "degraded"

    # Active websocket client count
    ws_count = len(connection_manager.active_connections)

    return HealthResponse(
        status=overall_status,
        version=getattr(settings, "VERSION", "0.23.0"),
        uptime_seconds=round(uptime, 2),
        database=db_status,
        scheduler="ok",
        providers=provider_health_map,
        telegram_bot=telegram_status,
        speech=speech_health,
        next_sync=None,
        websocket_clients=ws_count,
        docker_socket_mounted=docker_mounted,
        circuit_breakers=circuit_breakers_map,
        issues=issues,
    )
