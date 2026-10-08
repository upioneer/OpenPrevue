"""Declared application timezone resolution for local day boundaries."""

from zoneinfo import ZoneInfo

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import get_db


async def resolve_app_timezone() -> ZoneInfo:
    """Resolve the declared app timezone: settings `timezone`, TZ env, UTC.

    All relative day computations (fixture slotting, midnight rollover) anchor
    here so schedule days flip at local midnight. UTC remains the last-resort
    fallback and the storage convention for absolute instants.
    """
    name: str | None = None
    try:
        async with get_db() as db:
            async with db.execute(
                "SELECT value FROM settings WHERE key = 'timezone'"
            ) as cursor:
                row = await cursor.fetchone()
                if row and row["value"]:
                    name = str(row["value"]).strip()
    except Exception as exc:
        logger.debug("Timezone settings lookup failed, using fallback: %s", exc)
        name = None

    for candidate in (name, settings.TZ, "UTC"):
        if not candidate:
            continue
        try:
            return ZoneInfo(candidate)
        except Exception:
            logger.warning("Invalid timezone %r, trying next fallback.", candidate)
            continue
    return ZoneInfo("UTC")
