"""API endpoints for checking OpenPrevue system updates and applying in-place upgrades."""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from backend.app.services.updater import update_service

router = APIRouter(prefix="/updates", tags=["updates"])


class ApplyUpdateRequest(BaseModel):
    """Payload for initiating or dry-running an in-place upgrade."""

    target_version: str | None = Field(default=None, description="Target version string, e.g. '0.22.0' or 'latest'")
    dry_run: bool = Field(default=False, description="Simulate upgrade steps without executing destructive container/service changes")
    method: str | None = Field(default=None, description="Optional override strategy: 'docker_socket', 'git', or 'trigger_file'")


@router.get("/status")
async def get_update_status() -> dict:
    """Fetch current system version, latest release version, and update status."""
    return await update_service.get_status()


@router.post("/check")
async def trigger_update_check() -> dict:
    """Force an immediate live update check against GitHub Releases."""
    return await update_service.check_for_updates(force=True)


@router.get("/capability")
async def get_update_capability() -> dict:
    """Probe runtime environment to report supported in-place update strategies."""
    return await update_service.get_update_capability()


@router.post("/apply")
async def apply_system_update(payload: ApplyUpdateRequest) -> dict:
    """Execute or dry-run an in-place system upgrade."""
    return await update_service.apply_update(
        target_version=payload.target_version,
        dry_run=payload.dry_run,
        method=payload.method,
    )
