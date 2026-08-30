"""Unit tests for Ticketmaster Discovery API adapter."""

import pytest
from backend.app.providers.base import GeoPoint
from backend.app.providers.ticketmaster import TicketmasterProvider, map_ticketmaster_category


def test_map_ticketmaster_category():
    """Verify classification hierarchy mappings."""
    assert map_ticketmaster_category([{"segment": {"name": "Music"}}]) == "music"
    assert map_ticketmaster_category([{"segment": {"name": "Sports"}}]) == "sports"
    assert map_ticketmaster_category([{"segment": {"name": "Arts & Theatre"}}]) == "theater"
    assert map_ticketmaster_category([{"genre": {"name": "Comedy"}}]) == "comedy"
    assert map_ticketmaster_category([]) == "other"
    assert map_ticketmaster_category(None) == "other"


@pytest.mark.asyncio
async def test_ticketmaster_provider_skips_when_no_api_key():
    """Verify provider returns empty array when API key is missing."""
    provider = TicketmasterProvider(api_key=None)
    events = await provider.fetch_events(GeoPoint(29.95, -90.07), 35.0)
    assert events == []

    health = await provider.healthcheck()
    assert health.status == "disabled"
    assert health.is_healthy is False
