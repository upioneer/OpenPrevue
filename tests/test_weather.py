"""Unit tests for live weather service and endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app
from backend.app.services.weather import WMO_WEATHER_CODE_MAP, weather_service


def test_wmo_code_mapping():
    """Verify standard WMO weather codes map to clean retro conditions."""
    assert WMO_WEATHER_CODE_MAP[0] == "CLEAR SKY"
    assert WMO_WEATHER_CODE_MAP[3] == "OVERCAST"
    assert WMO_WEATHER_CODE_MAP[61] == "SLIGHT RAIN"
    assert WMO_WEATHER_CODE_MAP[95] == "THUNDERSTORM"


@pytest.mark.asyncio
async def test_get_current_weather():
    """Verify weather service returns formatted weather data."""
    weather = await weather_service.get_current_weather()
    assert weather.temperature is not None
    assert weather.condition != ""
    assert weather.temperature_unit == "F"
    assert weather.humidity >= 0


@pytest.mark.asyncio
async def test_weather_endpoints():
    """Verify GET and POST weather API endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/weather")
        assert res.status_code == 200
        data = res.json()
        assert "temperature" in data
        assert "condition" in data
        assert "humidity" in data

        # Force refresh endpoint
        refresh_res = await client.post("/api/v1/weather/refresh")
        assert refresh_res.status_code == 200
        refreshed = refresh_res.json()
        assert "temperature" in refreshed
