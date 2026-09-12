"""System activity logging service for recording audit and diagnostic events."""

from datetime import datetime, timezone
from backend.app.core.logging import logger
from backend.app.db.session import get_db


async def log_activity(component: str, action: str, status: str, details: str = "") -> None:
    """Record an operational, AI, or data event into activity_log."""
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        async with get_db() as db:
            await db.execute(
                """
                INSERT INTO activity_log (timestamp, component, action, status, details)
                VALUES (?, ?, ?, ?, ?)
                """,
                (now_iso, component.upper(), action, status.lower(), details),
            )
            await db.commit()
    except Exception as exc:
        logger.warning("Failed to record activity log entry (%s:%s): %s", component, action, exc)
