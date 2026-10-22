"""Tests for startup ingestion cadence, rolling calendar coverage, and self-healing tomorrow replenishment."""

from datetime import datetime, timedelta
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.core.config import settings
from backend.app.core.timezone import resolve_app_timezone
from backend.app.db.session import get_db
from backend.app.main import app
from backend.app.providers.base import GeoPoint
from backend.app.providers.mock import MockEventProvider
from backend.app.services.seeder import seed_initial_data


@pytest.mark.asyncio
async def test_mock_provider_covers_full_seven_day_window():
    """Verify MockEventProvider generates full programming across all 7 days of the calendar window."""
    provider = MockEventProvider()
    center_nola = GeoPoint(latitude=29.9511, longitude=-90.0715)
    events = await provider.fetch_events(center_nola, radius_miles=50.0)

    tz = await resolve_app_timezone()
    today = datetime.now(tz).date()

    # Check each day offset 0 through 6 has active events
    for day_offset in range(7):
        target_date = (today + timedelta(days=day_offset)).isoformat()
        matching = [e for e in events if e.start_time.startswith(target_date)]
        assert len(matching) >= 3, f"Expected at least 3 events for date {target_date} (day offset {day_offset}), got {len(matching)}"


@pytest.mark.asyncio
async def test_seeder_replenishes_when_tomorrow_is_empty():
    """Verify seeder detects when tomorrow is unpopulated and triggers ingestion."""
    tz = await resolve_app_timezone()
    today = datetime.now(tz).date()
    tomorrow = today + timedelta(days=1)

    async with get_db() as db:
        # Delete tomorrow events specifically
        await db.execute("DELETE FROM events WHERE start_time LIKE ?", (f"{tomorrow.isoformat()}%",))
        await db.commit()

    # Run seed_initial_data
    await seed_initial_data()

    # Verify tomorrow now has fixtures
    async with get_db() as db:
        async with db.execute("SELECT COUNT(*) AS count FROM events WHERE start_time LIKE ?", (f"{tomorrow.isoformat()}%",)) as cursor:
            row = await cursor.fetchone()
            assert row is not None and row["count"] > 0, "Expected tomorrow to be replenished with events"


@pytest.mark.asyncio
async def test_events_api_self_healing_trigger():
    """Verify list_events returns populated active events for today and tomorrow."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/events?status=active")
        assert res.status_code == 200
        items = res.json()
        assert len(items) > 0

        tz = await resolve_app_timezone()
        today_str = datetime.now(tz).date().isoformat()
        tomorrow_str = (datetime.now(tz).date() + timedelta(days=1)).isoformat()

        today_items = [i for i in items if i["start_time"].startswith(today_str)]
        tomorrow_items = [i for i in items if i["start_time"].startswith(tomorrow_str)]

        assert len(today_items) > 0, f"Expected today events for {today_str}"
        assert len(tomorrow_items) > 0, f"Expected tomorrow events for {tomorrow_str}"
