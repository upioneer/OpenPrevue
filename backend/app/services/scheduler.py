"""Async background task scheduler for recurring event ingestion."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import get_db
from backend.app.providers.base import GeoPoint
from backend.app.providers.registry import provider_registry
from backend.app.services.ingestion import ingestion_service

scheduler = AsyncIOScheduler()
JOB_ID_SYNC = "recurring_provider_sync"


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
            except Exception as exc:
                logger.error("Error during scheduled sync for [%s]: %s", provider.provider_name, exc)

    except Exception as exc:
        logger.error("Scheduled sync job failed: %s", exc, exc_info=True)


async def start_scheduler() -> None:
    """Start the APScheduler engine with configured sync interval from database."""
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

    logger.info("Starting background APScheduler with %d-hour interval trigger.", interval_hours)
    scheduler.add_job(
        execute_scheduled_sync,
        trigger=IntervalTrigger(hours=interval_hours),
        id=JOB_ID_SYNC,
        replace_existing=True,
    )
    scheduler.start()


def reschedule_sync_interval(interval_hours: int) -> None:
    """Dynamically reschedule the recurring ingestion job when settings update."""
    if scheduler.running and scheduler.get_job(JOB_ID_SYNC):
        logger.info("Rescheduling recurring sync job to %d hours.", interval_hours)
        scheduler.reschedule_job(
            JOB_ID_SYNC,
            trigger=IntervalTrigger(hours=interval_hours),
        )


async def shutdown_scheduler() -> None:
    """Gracefully terminate background scheduler."""
    if scheduler.running:
        logger.info("Shutting down background APScheduler...")
        scheduler.shutdown(wait=False)
