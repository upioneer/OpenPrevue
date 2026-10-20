"""Tests for declared-timezone resolution and local-midnight fixture anchoring."""

from zoneinfo import ZoneInfo

import pytest
from backend.app.core.config import settings
from backend.app.core.timezone import resolve_app_timezone
from backend.app.db.session import get_db, init_db
from backend.app.providers.base import GeoPoint
from backend.app.providers.sports import SportsLeagueProvider
from backend.app.providers.ticketing import SecondaryTicketingProvider

CHICAGO_OFFSETS = ("-05:00", "-06:00")


async def _set_timezone(value: str | None) -> None:
    async with get_db() as db:
        if value is None:
            await db.execute("DELETE FROM settings WHERE key = 'timezone'")
        else:
            await db.execute(
                "INSERT INTO settings (key, value) VALUES ('timezone', ?)"
                " ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (value,),
            )
        await db.commit()


@pytest.mark.asyncio
async def test_resolve_prefers_settings_then_env_then_utc():
    """Settings timezone wins; invalid values fall back without raising."""
    await init_db()

    await _set_timezone("America/Chicago")
    assert await resolve_app_timezone() == ZoneInfo("America/Chicago")

    await _set_timezone("Not/AZone")
    assert await resolve_app_timezone() == ZoneInfo(settings.TZ)

    await _set_timezone(None)
    assert await resolve_app_timezone() == ZoneInfo(settings.TZ)

    await _set_timezone(settings.TZ)


@pytest.mark.asyncio
async def test_ticketing_fixtures_anchor_to_declared_zone():
    """Secondary ticketing relative days carry the declared zone offset."""
    await init_db()
    await _set_timezone("America/Chicago")
    try:
        provider = SecondaryTicketingProvider()
        center = GeoPoint(latitude=29.9511, longitude=-90.0715)
        events = await provider.fetch_events(center, 50.0)
        assert len(events) >= 4
        for event in events:
            assert event.start_time[-6:] in CHICAGO_OFFSETS, (
                f"Fixture {event.source_event_id} not Chicago-anchored: {event.start_time}"
            )
    finally:
        await _set_timezone(settings.TZ)


@pytest.mark.asyncio
async def test_sports_fixtures_anchor_to_declared_zone():
    """Sports fixture days carry the declared zone offset (ESPN absolutes exempt)."""
    await init_db()
    await _set_timezone("America/Chicago")
    try:
        provider = SportsLeagueProvider()
        provider.coverage_mode = "national_broadcasts"
        center = GeoPoint(latitude=29.9511, longitude=-90.0715)
        events = await provider.fetch_events(center, 50.0)
        fixtures = [e for e in events if not e.source_event_id.startswith("espn-")]
        assert len(fixtures) >= 1
        for event in fixtures:
            assert event.start_time[-6:] in CHICAGO_OFFSETS, (
                f"Fixture {event.source_event_id} not Chicago-anchored: {event.start_time}"
            )
    finally:
        await _set_timezone(settings.TZ)


@pytest.mark.asyncio
async def test_calendar_based_today_and_tomorrow_coverage():
    """Verify calendar-based providers populate both Today and Tomorrow in the declared timezone."""
    from datetime import datetime, timedelta
    from backend.app.providers.mock import MockEventProvider

    await init_db()
    await _set_timezone("America/Chicago")
    try:
        tz = await resolve_app_timezone()
        today_str = datetime.now(tz).date().isoformat()
        tomorrow_str = (datetime.now(tz).date() + timedelta(days=1)).isoformat()

        slidell_center = GeoPoint(latitude=30.2784, longitude=-89.7712)
        mock_events = await MockEventProvider().fetch_events(slidell_center, 100.0)
        ticketing_events = await SecondaryTicketingProvider().fetch_events(slidell_center, 100.0)

        mock_dates = {e.start_time[:10] for e in mock_events}
        ticketing_dates = {e.start_time[:10] for e in ticketing_events}

        assert today_str in mock_dates
        assert tomorrow_str in mock_dates
        assert today_str in ticketing_dates
        assert tomorrow_str in ticketing_dates

        for e in mock_events:
            assert e.source_event_id.endswith(e.start_time[:10])
        for e in ticketing_events:
            assert e.source_event_id.endswith(e.start_time[:10])
    finally:
        await _set_timezone(settings.TZ)
