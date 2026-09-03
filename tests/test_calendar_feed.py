"""Unit tests for RFC 5545 iCalendar (.ics) subscription feeds and event exporter."""

import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.api.v1.endpoints.calendar import _escape_ics_text, _format_ics_datetime
from backend.app.main import app


def test_format_ics_datetime():
    """Verify ISO datetime string converts to standard RFC 5545 UTC timestamp."""
    assert _format_ics_datetime("2026-09-15T20:00:00Z") == "20260915T200000Z"
    assert _format_ics_datetime("2026-09-15T20:00:00+00:00") == "20260915T200000Z"
    # None or empty string fallback
    res_none = _format_ics_datetime(None)
    assert len(res_none) == 16
    assert res_none.endswith("Z")


def test_escape_ics_text():
    """Verify special characters and non-ASCII glyphs are sanitized."""
    assert _escape_ics_text("Concert, Live; Show\nNext Line") == "Concert\\, Live\\; Show\\nNext Line"
    assert _escape_ics_text("Standard Event Title") == "Standard Event Title"


@pytest.mark.asyncio
async def test_ical_feed_all_events():
    """Verify GET /api/v1/calendar/feed.ics returns valid VCALENDAR with VEVENT items."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/calendar/feed.ics?filter=all")
        assert res.status_code == 200
        assert "text/calendar" in res.headers["content-type"]
        body = res.text
        assert "BEGIN:VCALENDAR" in body
        assert "VERSION:2.0" in body
        assert "PRODID:-//OpenPrevue//Event Aggregator 1.0//EN" in body
        assert "BEGIN:VEVENT" in body
        assert "UID:" in body
        assert "SUMMARY:" in body
        assert "LOCATION:" in body
        assert "BEGIN:VALARM" in body
        assert "TRIGGER:-PT2H" in body
        assert "END:VCALENDAR" in body


@pytest.mark.asyncio
async def test_ical_feed_committed_filter():
    """Verify GET /api/v1/calendar/feed.ics?filter=committed filters by has_ticket=1."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # First ensure at least one ticket is committed
        events_res = await client.get("/api/v1/events")
        events = events_res.json()
        assert len(events) > 0
        first_id = events[0]["id"]

        await client.patch(f"/api/v1/events/{first_id}", json={"has_ticket": 1})

        # Query committed feed
        res = await client.get("/api/v1/calendar/feed.ics?filter=committed")
        assert res.status_code == 200
        body = res.text
        assert "BEGIN:VCALENDAR" in body
        assert f"UID:{first_id}@openprevue.local" in body


@pytest.mark.asyncio
async def test_single_event_ics_download():
    """Verify GET /api/v1/calendar/events/{event_id}.ics downloads a standalone .ics calendar file."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        events_res = await client.get("/api/v1/events")
        events = events_res.json()
        first_id = events[0]["id"]

        res = await client.get(f"/api/v1/calendar/events/{first_id}.ics")
        assert res.status_code == 200
        assert "text/calendar" in res.headers["content-type"]
        assert "attachment; filename=" in res.headers["content-disposition"]
        body = res.text
        assert "BEGIN:VCALENDAR" in body
        assert f"UID:{first_id}@openprevue.local" in body
        assert "END:VCALENDAR" in body


@pytest.mark.asyncio
async def test_calendar_subscribe_urls_endpoint():
    """Verify GET /api/v1/calendar/subscribe-urls returns dictionary of subscription links."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/calendar/subscribe-urls")
        assert res.status_code == 200
        data = res.json()
        assert "committed" in data
        assert "featured" in data
        assert "all" in data
        assert "feed.ics" in data["committed"]["path"]
