"""Configuration backup, automated disk persistence, and settings restoration service."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import get_db

BACKUP_FILENAME = "openprevue_settings_backup.json"


def get_backup_path() -> Path:
    """Return absolute path to settings backup file."""
    data_dir = Path(settings.DATA_DIR)
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / BACKUP_FILENAME


async def backup_settings_to_disk() -> bool:
    """Export current SQLite settings and custom venues to persistent JSON file on disk."""
    try:
        backup_file = get_backup_path()
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

        payload = {
            "version": getattr(settings, "VERSION", "0.24.0"),
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "settings": all_settings,
            "custom_venues": venues_list,
        }

        temp_file = backup_file.with_suffix(".tmp")
        temp_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temp_file.replace(backup_file)
        logger.debug("Successfully backed up settings to %s", backup_file)
        return True
    except Exception as exc:
        logger.error("Failed backing up settings to disk: %s", exc)
        return False


async def restore_settings_from_backup_if_needed() -> bool:
    """Check if database has default/empty settings and restore from backup file if available."""
    backup_file = get_backup_path()
    if not backup_file.exists():
        return False

    try:
        content = json.loads(backup_file.read_text(encoding="utf-8"))
        saved_settings = content.get("settings", {})
        saved_venues = content.get("custom_venues", [])

        if not saved_settings:
            return False

        async with get_db() as db:
            # Check if user has already configured the instance
            async with db.execute("SELECT value FROM settings WHERE key = 'initial_setup_completed'") as cursor:
                row = await cursor.fetchone()
                initial_setup_done = row and row["value"] == "1"

            # If setup was already completed in the current DB, don't overwrite
            if initial_setup_done:
                return False

            # If backup has a completed setup or custom AI settings, restore them!
            backup_has_custom = (
                saved_settings.get("initial_setup_completed") == "1"
                or saved_settings.get("ai_ollama_url")
                or saved_settings.get("metro_label") != settings.DEFAULT_METRO_LABEL
            )

            if not backup_has_custom:
                return False

            logger.info("Restoring previous settings from disk backup (%s)...", backup_file)
            now_iso = datetime.now(timezone.utc).isoformat()
            for key, val in saved_settings.items():
                await db.execute(
                    """
                    INSERT INTO settings (key, value, updated_at)
                    VALUES (?, ?, ?)
                    ON CONFLICT(key) DO UPDATE SET
                        value = excluded.value,
                        updated_at = excluded.updated_at
                    """,
                    (key, str(val), now_iso),
                )

            # Restore custom venues
            for v in saved_venues:
                await db.execute(
                    """
                    INSERT OR IGNORE INTO venues (id, name, address, city, state, postal_code, latitude, longitude, custom_order, is_active)
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
            logger.info("Restored %d settings and %d custom venues from disk backup.", len(saved_settings), len(saved_venues))
            return True
    except Exception as exc:
        logger.error("Error restoring settings from backup: %s", exc)
        return False


def get_backup_status() -> dict[str, Any]:
    """Return status and file metadata for the disk backup."""
    backup_file = get_backup_path()
    if not backup_file.exists():
        return {
            "exists": False,
            "path": str(backup_file),
            "size_bytes": 0,
            "last_modified": None,
            "settings_count": 0,
        }

    try:
        stat = backup_file.stat()
        content = json.loads(backup_file.read_text(encoding="utf-8"))
        return {
            "exists": True,
            "path": str(backup_file),
            "size_bytes": stat.st_size,
            "last_modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            "settings_count": len(content.get("settings", {})),
            "version": content.get("version", "unknown"),
        }
    except Exception as exc:
        return {
            "exists": True,
            "path": str(backup_file),
            "error": str(exc),
            "last_modified": None,
            "settings_count": 0,
        }
