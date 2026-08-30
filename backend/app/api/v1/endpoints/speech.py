"""Speech engine status, heartbeat monitoring, and diagnostic REST API endpoints."""

from fastapi import APIRouter
from backend.app.services.speech import speech_service

router = APIRouter()


@router.get("/speech/status")
async def get_speech_status() -> dict:
    """Retrieve speech engine operational status, active engine, and heartbeat telemetry."""
    return await speech_service.check_health()


@router.post("/speech/test")
async def test_speech_pipeline() -> dict:
    """Run an active speech round-trip test and measure pipeline latency."""
    return await speech_service.run_diagnostic_probe()
