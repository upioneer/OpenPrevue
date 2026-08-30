"""Test events and venues API endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app
from backend.app.db.session import init_db
from backend.app.services.seeder import seed_initial_data


@pytest.fixture(autouse=True)
async def setup_database():
    """Ensure database is initialized and seeded before tests."""
    await init_db()
    await seed_initial_data()


@pytest.mark.asyncio
async def test_list_events():
    """Verify events API returns list of seeded mock events."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/events")
        assert response.status_code == 200
        events = response.json()
        assert isinstance(events, list)
        assert len(events) > 0

        first_event = events[0]
        assert "id" in first_event
        assert "title" in first_event
        assert "venue_name" in first_event
        assert "ticket_links" in first_event


@pytest.mark.asyncio
async def test_list_venues():
    """Verify venues API returns canonical venues."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/venues")
        assert response.status_code == 200
        venues = response.json()
        assert isinstance(venues, list)
        assert len(venues) > 0
