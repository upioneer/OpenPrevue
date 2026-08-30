"""System settings management API endpoints."""

from datetime import datetime, timezone
from fastapi import APIRouter
from backend.app.db.session import get_db
from backend.app.schemas.setting import SettingItem, SettingUpdate

router = APIRouter()


@router.get("/settings", response_model=dict[str, str])
async def get_all_settings() -> dict[str, str]:
    """Retrieve all configuration settings."""
    async with get_db() as db:
        async with db.execute("SELECT key, value FROM settings") as cursor:
            rows = await cursor.fetchall()
            return {row["key"]: row["value"] for row in rows}


@router.put("/settings/{key}", response_model=SettingItem)
async def update_setting(key: str, payload: SettingUpdate) -> SettingItem:
    """Create or update a single configuration setting."""
    now_iso = datetime.now(timezone.utc).isoformat()
    async with get_db() as db:
        await db.execute(
            """
            INSERT INTO settings (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
            """,
            (key, payload.value, now_iso),
        )
        await db.commit()

    return SettingItem(key=key, value=payload.value, updated_at=now_iso)
