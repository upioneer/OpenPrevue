"""Emergency Alert System (EAS) REST API endpoints."""

from fastapi import APIRouter
from backend.app.schemas.eas import EASTestRequest, EmergencyAlert
from backend.app.services.eas import eas_service

router = APIRouter()


@router.get("/eas/alerts", response_model=list[EmergencyAlert])
async def get_active_emergency_alerts() -> list[EmergencyAlert]:
    """Retrieve all currently active emergency alerts."""
    return await eas_service.poll_and_broadcast_alerts()


@router.post("/eas/test", response_model=EmergencyAlert)
async def dispatch_test_emergency_alert(payload: EASTestRequest) -> EmergencyAlert:
    """Dispatch a simulated EAS emergency alert broadcast to all active dashboard displays."""
    return await eas_service.create_test_alert(
        event_type=payload.event_type,
        headline=payload.headline,
        severity=payload.severity,
        area_description=payload.area_description,
        instruction=payload.instruction,
        duration_seconds=payload.duration_seconds,
    )
