"""Database seeder for default settings and initial mock data."""

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import get_db
from backend.app.providers.base import GeoPoint
from backend.app.providers.registry import provider_registry
from backend.app.services.ingestion import ingestion_service


DEFAULT_SETTINGS: dict[str, str] = {
    "postal_code": settings.DEFAULT_POSTAL_CODE,
    "metro_label": settings.DEFAULT_METRO_LABEL,
    "latitude": str(settings.DEFAULT_LATITUDE),
    "longitude": str(settings.DEFAULT_LONGITUDE),
    "radius_miles": str(settings.DEFAULT_RADIUS_MILES),
    "autoscroll_speed": "30",
    "grid_density": "balanced",
    "scroll_pause_duration": "4",
    "scroll_page_interval": "6",
    "marquee_rotation_seconds": "20",
    "scanline_intensity": "12",
    "phosphor_glow": "1",
    "crt_curvature": "0",
    "vhs_tracking_noise": "0",
    "time_format": "12h",
    "sync_interval_hours": "6",
    "initial_setup_completed": "0",
    "update_check_interval": "disabled",
    "auto_update_notifs": "0",
    "tripadvisor_wishlist_url": "",
    "viator_wishlist_url": "",
    "viator_api_key": "",
    "audio_source": "spotify",
    "spotify_playlist_url": "https://open.spotify.com/playlist/3jiPmIT4RugR8TPhli5Obk",
    "icecast_stream_preset": "weatherscan",
    "icecast_custom_url": "",
    "screen_wake_lock_enabled": "1",
    "display_sleep_schedule": "disabled",
    "display_sleep_time": "23:00",
    "display_wake_time": "07:00",
    "ha_mqtt_enabled": "0",
    "ha_mqtt_broker": "localhost",
    "ha_mqtt_port": "1883",
    "ha_mqtt_username": "",
    "ha_mqtt_password": "",
    "ha_mqtt_topic_prefix": "homeassistant",
}


async def seed_initial_data() -> None:
    """Seed initial system settings and mock listings if datastore is empty."""
    logger.info("Checking datastore seed status...")

    async with get_db() as db:
        # Seed default settings if missing
        for key, value in DEFAULT_SETTINGS.items():
            await db.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                (key, value),
            )
        await db.commit()

        # Check existing events count
        async with db.execute("SELECT COUNT(*) AS count FROM events") as cursor:
            row = await cursor.fetchone()
            event_count = row["count"] if row else 0

    if event_count == 0:
        logger.info("Datastore has 0 events. Executing initial mock ingestion...")
        mock_provider = provider_registry.get("mock")
        if mock_provider:
            center = GeoPoint(
                latitude=settings.DEFAULT_LATITUDE,
                longitude=settings.DEFAULT_LONGITUDE,
            )
            result = await ingestion_service.sync_provider(
                mock_provider,
                center,
                settings.DEFAULT_RADIUS_MILES,
            )
            logger.info("Initial seed completed: %s", result)
