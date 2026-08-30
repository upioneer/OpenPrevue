"""Async background task scheduler for recurring event ingestion, weather refresh, and EAS alerts."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.base import STATE_RUNNING, STATE_STOPPED
from apscheduler.triggers.interval import IntervalTrigger

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import get_db
from backend.app.providers.base import GeoPoint
from backend.app.providers.registry import provider_registry
from backend.app.services.eas import eas_service
from backend.app.services.ingestion import ingestion_service
from backend.app.services.weather import weather_service
from backend.app.services.websocket import connection_manager

scheduler = AsyncIOScheduler()
JOB_ID_SYNC = "recurring_provider_sync"
JOB_ID_WEATHER = "recurring_weather_refresh"
JOB_ID_EAS = "recurring_eas_poll"


async def execute_scheduled_sync() -> None:
    """Execute recurring synchronization pass across all enabled providers."""
    logger.info("Executing scheduled recurring ingestion synchronization...")

    try:
        async with get_db() as db:
            async with db.execute("SELECT key, value FROM settings WHERE key IN ('latitude', 'longitude', 'radius_miles')") as cursor:
                rows = await cursor.fetchall()
                settings_map = {row["key"]: row["value"] for row in rows}

        lat = float(settings_map.get("latitude", settings.DEFAULT_LATITUDE))
        lon = float(settings_map.get("longitude", settings.DEFAULT_LONGITUDE))
        radius = float(settings_map.get("radius_miles", settings.DEFAULT_RADIUS_MILES))

        center = GeoPoint(latitude=lat, longitude=lon)

        for provider in provider_registry.get_all():
            try:
                res = await ingestion_service.sync_provider(provider, center, radius)
                logger.info("Scheduled sync result for [%s]: %s", provider.provider_name, res.get("status"))
                await connection_manager.broadcast("events_updated", {"provider": provider.provider_name, "status": res.get("status")})
            except Exception as exc:
                logger.error("Error during scheduled sync for [%s]: %s", provider.provider_name, exc)

    except Exception as exc:
        logger.error("Scheduled sync job failed: %s", exc, exc_info=True)


async def execute_scheduled_weather_refresh() -> None:
    """Execute 15-minute weather refresh and broadcast to dashboard displays."""
    try:
        logger.info("Executing scheduled weather refresh...")
        weather = await weather_service.get_current_weather(force_refresh=True)
        await connection_manager.broadcast("weather_updated", weather.to_dict())
    except Exception as exc:
        logger.debug("Scheduled weather refresh error: %s", exc)


async def execute_scheduled_eas_poll() -> None:
    """Execute 5-minute emergency alert polling pass."""
    try:
        await eas_service.poll_and_broadcast_alerts()
    except Exception as exc:
        logger.debug("Scheduled EAS poll error: %s", exc)


async def start_scheduler() -> None:
    """Start the APScheduler engine with configured sync interval, weather refresh, and EAS polling."""
    global scheduler

    if scheduler.state == STATE_STOPPED:
        scheduler = AsyncIOScheduler()

    if scheduler.running:
        return

    interval_hours = 6
    try:
        async with get_db() as db:
            async with db.execute("SELECT value FROM settings WHERE key = 'sync_interval_hours'") as cursor:
                row = await cursor.fetchone()
                if row:
                    interval_hours = int(row["value"])
    except Exception:
        pass

    logger.info("Starting background APScheduler with %d-hour sync, 15-min weather, and 5-min EAS triggers.", interval_hours)

    scheduler.add_job(
        execute_scheduled_sync,
        trigger=IntervalTrigger(hours=interval_hours),
        id=JOB_ID_SYNC,
        replace_existing=True,
    )

    scheduler.add_job(
        execute_scheduled_weather_refresh,
        trigger=IntervalTrigger(minutes=15),
        id=JOB_ID_WEATHER,
        replace_existing=True,
    )

    scheduler.add_job(
        execute_scheduled_eas_poll,
        trigger=IntervalTrigger(minutes=5),
        id=JOB_ID_EAS,
        replace_existing=True,
    )

    scheduler.start()


def reschedule_sync_interval(interval_hours: int) -> None:
    """Dynamically reschedule the recurring ingestion job when settings update."""
    global scheduler
    if scheduler.running and scheduler.get_job(JOB_ID_SYNC):
        logger.info("Rescheduling recurring sync job to %d hours.", interval_hours)
        scheduler.reschedule_job(
            JOB_ID_SYNC,
            trigger=IntervalTrigger(hours=interval_hours),
        )


async def shutdown_scheduler() -> None:
    """Gracefully terminate background scheduler."""
    global scheduler
    if scheduler.running:
        logger.info("Shutting down background APScheduler...")
        scheduler.shutdown(wait=False)
