"""Unit tests for speech engine status, heartbeat monitoring, turnkey audio, and intent parsing."""

import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app
from backend.app.services.speech import speech_service


@pytest.mark.asyncio
async def test_speech_service_health():
    """Verify speech service reports heartbeat and operational status."""
    status = await speech_service.check_health()
    assert status["status"] == "operational"
    assert "mode" in status
    assert "stt_engine" in status
    assert "tts_engine" in status
    assert "last_heartbeat" in status
    assert status["latency_ms"] >= 0


@pytest.mark.asyncio
async def test_speech_diagnostic_probe():
    """Verify diagnostic probe runs and reports latency."""
    diag = await speech_service.run_diagnostic_probe()
    assert diag["status"] == "passed"
    assert diag["latency_ms"] >= 0
    assert "message" in diag


@pytest.mark.asyncio
async def test_speech_api_endpoints():
    """Verify speech REST API status and testing endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # GET /api/v1/speech/status
        status_res = await client.get("/api/v1/speech/status")
        assert status_res.status_code == 200
        data = status_res.json()
        assert data["status"] == "operational"
        assert "mode" in data

        # POST /api/v1/speech/test
        test_res = await client.post("/api/v1/speech/test")
        assert test_res.status_code == 200
        test_data = test_res.json()
        assert test_data["status"] == "passed"
        assert test_data["latency_ms"] >= 0


def test_spoken_intent_parser():
    """Verify natural spoken phrases map to deterministic bot commands."""
    cmd, args = speech_service.parse_spoken_intent("What is happening tonight?")
    assert cmd == "tonight"
    assert args == []

    cmd, args = speech_service.parse_spoken_intent("Show me the weekend schedule")
    assert cmd == "weekend"

    cmd, args = speech_service.parse_spoken_intent("What events are happening today?")
    assert cmd == "today"

    cmd, args = speech_service.parse_spoken_intent("Check system status and weather")
    assert cmd == "status"

    cmd, args = speech_service.parse_spoken_intent("Search Preservation Hall Jazz")
    assert cmd == "search"
    assert "Preservation" in args or "preservation" in args

    cmd, args = speech_service.parse_spoken_intent("Track New Orleans Saints")
    assert cmd == "watch"
    assert "saints" in [a.lower() for a in args]


@pytest.mark.asyncio
async def test_turnkey_audio_synthesis():
    """Verify turnkey audio generation produces a valid WAV audio buffer."""
    audio_bytes = await speech_service.synthesize_speech_bytes("Test announcement")
    assert len(audio_bytes) > 44  # Minimum valid WAV header size
    assert audio_bytes[:4] == b"RIFF"
    assert audio_bytes[8:12] == b"WAVE"
