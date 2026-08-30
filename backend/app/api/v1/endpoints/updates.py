"""API endpoints for checking OpenPrevue system updates."""

from fastapi import APIRouter
from backend.app.services.updater import update_service

router = APIRouter(prefix="/updates", tags=["updates"])


@router.get("/status")
async def get_update_status() -> dict:
    """Fetch current system version, latest release version, and update status."""
    return await update_service.get_status()


@router.post("/check")
async def trigger_update_check() -> dict:
    """Force an immediate live update check against GitHub Releases."""
    return await update_service.check_for_updates(force=True)
