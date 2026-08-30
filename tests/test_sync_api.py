"""Test sync and ingestion audit log endpoints."""

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
async def test_trigger_sync():
    """Verify manual sync triggers and completes successfully."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/sync")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

        # Verify logs endpoint
        logs_res = await client.get("/api/v1/sync/logs")
        assert logs_res.status_code == 200
        logs = logs_res.json()
        assert len(logs) > 0
        assert logs[0]["provider"] == "mock"
