import asyncio
from datetime import datetime, timezone
import json
from typing import Any
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

    from backend.app.services.activity import log_activity

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

    # If travel wishlist URLs were updated, trigger immediate provider sync
    if key in ("tripadvisor_wishlist_url", "viator_wishlist_url") and payload.value.strip():
        try:
            await ingestion_service.sync_all_registered_providers()
            await connection_manager.broadcast("events_updated", {"trigger": f"{key}_updated"})
            await log_activity(
                component="SETTINGS",
                action="update_travel_url",
                status="success",
                details=f"Updated {key} and triggered immediate provider sync",
            )
        except Exception as exc:
            await log_activity(
                component="SETTINGS",
                action="update_travel_url",
                status="error",
                details=f"Failed sync after {key} update: {exc}",
            )

    # Persist updated settings to server disk backup asynchronously
    from backend.app.services.settings_backup import backup_settings_to_disk
    asyncio.create_task(backup_settings_to_disk())

    return SettingItem(key=key, value=payload.value, updated_at=now_iso)


class BackupImportPayload(BaseModel):
    settings: dict[str, Any]
    custom_venues: list[dict[str, Any]] = []


@router.get("/backup/status")
async def get_disk_backup_status() -> dict:
    """Check status, timestamp, and size of the automated persistent disk backup."""
    from backend.app.services.settings_backup import get_backup_status
    return get_backup_status()


@router.get("/backup/export")
async def export_settings_backup() -> dict:
    """Export complete system configuration and custom venues as a JSON-serializable backup."""
    from backend.app.core.config import settings as app_settings
    all_settings: dict[str, str] = {}
    venues_list: list[dict[str, Any]] = []

    async with get_db() as db:
        async with db.execute("SELECT key, value FROM settings") as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                all_settings[row["key"]] = row["value"]

        async with db.execute("SELECT id, name, address, city, state, postal_code, latitude, longitude, custom_order, is_active FROM venues WHERE id NOT LIKE 'mock-%'") as cursor:
            vrows = await cursor.fetchall()
            for vr in vrows:
                venues_list.append({
                    "id": vr["id"],
                    "name": vr["name"],
                    "address": vr["address"],
                    "city": vr["city"],
                    "state": vr["state"],
                    "postal_code": vr["postal_code"],
                    "latitude": vr["latitude"],
                    "longitude": vr["longitude"],
                    "custom_order": vr["custom_order"],
                    "is_active": vr["is_active"],
                })

    return {
        "version": getattr(app_settings, "VERSION", "0.24.0"),
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "settings": all_settings,
        "custom_venues": venues_list,
    }


@router.post("/backup/import")
async def import_settings_backup(payload: BackupImportPayload) -> dict:
    """Import and apply settings and custom venues from a backup payload."""
    from backend.app.services.activity import log_activity
    from backend.app.services.settings_backup import backup_settings_to_disk

    now_iso = datetime.now(timezone.utc).isoformat()
    imported_count = 0
    venue_count = 0

    async with get_db() as db:
        for k, v in payload.settings.items():
            await db.execute(
                """
                INSERT INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at
                """,
                (k, str(v), now_iso),
            )
            imported_count += 1

        for v in payload.custom_venues:
            if "id" in v and "name" in v:
                await db.execute(
                    """
                    INSERT OR REPLACE INTO venues (id, name, address, city, state, postal_code, latitude, longitude, custom_order, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        v["id"],
                        v["name"],
                        v.get("address", ""),
                        v.get("city", ""),
                        v.get("state", ""),
                        v.get("postal_code", ""),
                        v.get("latitude"),
                        v.get("longitude"),
                        v.get("custom_order", 999),
                        v.get("is_active", 1),
                    ),
                )
                venue_count += 1

        await db.commit()

    await backup_settings_to_disk()
    await connection_manager.broadcast("settings_updated", {"trigger": "backup_imported"})
    await log_activity(
        component="SETTINGS",
        action="import_backup",
        status="success",
        details=f"Imported {imported_count} settings and {venue_count} custom venues from backup",
    )

    return {
        "status": "success",
        "imported_settings": imported_count,
        "imported_venues": venue_count,
        "message": f"Successfully restored {imported_count} settings and {venue_count} venues.",
    }


@router.post("/backup/restore-disk")
async def restore_disk_backup_now() -> dict:
    """Trigger manual restore from openprevue_settings_backup.json on server disk."""
    from backend.app.services.activity import log_activity
    from backend.app.services.settings_backup import get_backup_path, backup_settings_to_disk

    backup_file = get_backup_path()
    if not backup_file.exists():
        return {"status": "error", "message": "No disk backup file found."}

    content = json.loads(backup_file.read_text(encoding="utf-8"))
    saved_settings = content.get("settings", {})
    saved_venues = content.get("custom_venues", [])

    now_iso = datetime.now(timezone.utc).isoformat()
    async with get_db() as db:
        for k, v in saved_settings.items():
            await db.execute(
                """
                INSERT INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at
                """,
                (k, str(v), now_iso),
            )
        for v in saved_venues:
            if "id" in v and "name" in v:
                await db.execute(
                    """
                    INSERT OR REPLACE INTO venues (id, name, address, city, state, postal_code, latitude, longitude, custom_order, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        v["id"],
                        v["name"],
                        v.get("address", ""),
                        v.get("city", ""),
                        v.get("state", ""),
                        v.get("postal_code", ""),
                        v.get("latitude"),
                        v.get("longitude"),
                        v.get("custom_order", 999),
                        v.get("is_active", 1),
                    ),
                )
        await db.commit()

    await backup_settings_to_disk()
    await connection_manager.broadcast("settings_updated", {"trigger": "disk_backup_restored"})
    await log_activity(
        component="SETTINGS",
        action="restore_disk_backup",
        status="success",
        details=f"Restored {len(saved_settings)} settings and {len(saved_venues)} venues from disk backup",
    )

    return {
        "status": "success",
        "restored_settings": len(saved_settings),
        "restored_venues": len(saved_venues),
        "message": f"Successfully restored {len(saved_settings)} settings from disk backup.",
    }
