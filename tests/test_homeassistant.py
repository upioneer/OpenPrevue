"""Unit tests for Home Assistant integration, display power, and audio presets endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app
from backend.app.services.homeassistant import homeassistant_service


@pytest.mark.asyncio
async def test_homeassistant_sensors_payload():
    """Verify GET /api/v1/integrations/homeassistant/sensors returns valid entity state."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/integrations/homeassistant/sensors")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "operational"
        assert "counts" in data
        assert "active_events" in data["counts"]
        assert "committed_tickets" in data["counts"]
        assert "today_events_count" in data["counts"]
        assert "spotlight" in data
        assert "weather" in data
        assert "eas" in data


@pytest.mark.asyncio
async def test_homeassistant_yaml_config():
    """Verify GET /api/v1/integrations/homeassistant/yaml-config generates valid YAML."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/integrations/homeassistant/yaml-config")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert "yaml" in data
        yaml_str = data["yaml"]
        assert "rest:" in yaml_str
        assert "OpenPrevue Today Events Count" in yaml_str
        assert "OpenPrevue Active Spotlight" in yaml_str
        assert "OpenPrevue EAS Alert Active" in yaml_str


@pytest.mark.asyncio
async def test_display_power_endpoint():
    """Verify POST /api/v1/integrations/display/power commands display states."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Valid on command
        res_on = await client.post("/api/v1/integrations/display/power", json={"state": "on"})
        assert res_on.status_code == 200
        assert res_on.json()["requested_state"] == "on"

        # Valid off command
        res_off = await client.post("/api/v1/integrations/display/power", json={"state": "off"})
        assert res_off.status_code == 200
        assert res_off.json()["requested_state"] == "off"

        # Invalid state rejects with 400
        res_invalid = await client.post("/api/v1/integrations/display/power", json={"state": "hibernate"})
        assert res_invalid.status_code == 400


@pytest.mark.asyncio
async def test_audio_presets_endpoint():
    """Verify GET /api/v1/audio/presets includes Spotify as default and Icecast streams."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/audio/presets")
        assert res.status_code == 200
        presets = res.json()
        assert isinstance(presets, list)
        assert len(presets) >= 4

        # Verify Spotify is present and configured as default
        spotify_preset = next((p for p in presets if p["id"] == "spotify"), None)
        assert spotify_preset is not None
        assert spotify_preset["is_default"] is True
        assert "3jiPmIT4RugR8TPhli5Obk" in spotify_preset["default_url"]

        # Verify Icecast presets
        weatherscan = next((p for p in presets if p["id"] == "weatherscan"), None)
        assert weatherscan is not None
        assert weatherscan["type"] == "icecast"
