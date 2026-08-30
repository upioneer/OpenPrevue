"""Test settings API endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app
from backend.app.db.session import init_db
from backend.app.services.seeder import seed_initial_data


@pytest.fixture(autouse=True)
async def setup_database():
    """Initialize database and default settings."""
    await init_db()
    await seed_initial_data()


@pytest.mark.asyncio
async def test_get_settings():
    """Verify settings retrieval returns dictionary of configuration parameters."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/settings")
        assert response.status_code == 200
        data = response.json()
        assert "postal_code" in data
        assert "radius_miles" in data
        assert "autoscroll_speed" in data


@pytest.mark.asyncio
async def test_update_setting():
    """Verify updating a setting persists in the datastore."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(
            "/api/v1/settings/autoscroll_speed",
            json={"value": "95"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "autoscroll_speed"
        assert data["value"] == "95"

        # Verify on get
        get_res = await client.get("/api/v1/settings")
        assert get_res.json()["autoscroll_speed"] == "95"
