"""Tests for Location Geocoding API and coordinate resolution."""

import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app
from backend.app.services.geocoding import resolve_location_query


@pytest.mark.asyncio
async def test_resolve_location_city_name():
    """Verify city name resolution to valid coordinates."""
    results = await resolve_location_query("Austin")
    assert len(results) > 0
    assert any("AUSTIN" in r.metro_label for r in results)
    assert any(29.0 < r.latitude < 31.0 for r in results)
    assert any(-99.0 < r.longitude < -96.0 for r in results)


@pytest.mark.asyncio
async def test_resolve_location_zip_code():
    """Verify US ZIP code resolution to coordinates."""
    results = await resolve_location_query("60601")
    assert len(results) > 0
    match = results[0]
    assert "CHICAGO" in match.metro_label or "60601" in match.display_label
    assert 40.0 < match.latitude < 43.0


@pytest.mark.asyncio
async def test_weather_geocode_endpoint():
    """Verify GET /api/v1/weather/geocode endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/weather/geocode?query=Seattle")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert any("SEATTLE" in item["metro_label"] for item in data)
