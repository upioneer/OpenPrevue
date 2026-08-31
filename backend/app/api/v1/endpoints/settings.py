"""System settings API endpoints."""

from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.db.session import get_db
from backend.app.services.ingestion import ingestion_service
from backend.app.services.scheduler import reschedule_sync_interval
from backend.app.services.weather import weather_service
from backend.app.services.websocket import connection_manager

router = APIRouter(prefix="/settings")


class SettingItem(BaseModel):
    key: str
    value: str
    updated_at: str | None = None


class SettingUpdate(BaseModel):
    value: str


@router.get("", response_model=dict[str, str])
async def get_settings() -> dict[str, str]:
    """Retrieve all system settings as key-value pairs."""
    settings: dict[str, str] = {}
    async with get_db() as db:
        async with db.execute("SELECT key, value FROM settings") as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                settings[row["key"]] = row["value"]
    return settings


@router.put("/{key}", response_model=SettingItem)
async def update_setting(key: str, payload: SettingUpdate) -> SettingItem:
    """Update a specific system setting by key."""
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

    # Dynamic scheduler rescheduling if sync_interval_hours was updated
    if key == "sync_interval_hours":
        try:
            reschedule_sync_interval(int(payload.value))
        except ValueError:
            pass

    # Broadcast settings update to all active dashboard displays
    await connection_manager.broadcast("settings_updated", {"key": key, "value": payload.value})

    # If location coordinate changed, refresh weather & re-sync events immediately
    if key in ("latitude", "longitude", "metro_label", "postal_code", "radius_miles"):
        try:
            weather = await weather_service.get_current_weather(force_refresh=True)
            await connection_manager.broadcast("weather_updated", weather.to_dict())
        except Exception:
            pass

        try:
            await ingestion_service.sync_all_registered_providers()
            await connection_manager.broadcast("events_updated", {"trigger": "location_changed"})
        except Exception:
            pass

    return SettingItem(key=key, value=payload.value, updated_at=now_iso)
