"""Unit tests for SeatGeek Platform API adapter."""

import pytest
from backend.app.providers.base import GeoPoint
from backend.app.providers.seatgeek import SeatGeekProvider, map_seatgeek_category


def test_map_seatgeek_category():
    """Verify taxonomy and event type mappings."""
    assert map_seatgeek_category("concert", None) == "music"
    assert map_seatgeek_category("nba", None) == "sports"
    assert map_seatgeek_category("theater", None) == "theater"
    assert map_seatgeek_category("comedy", None) == "comedy"
    assert map_seatgeek_category("unknown", [{"name": "Concerts"}]) == "music"
    assert map_seatgeek_category(None, None) == "other"


@pytest.mark.asyncio
async def test_seatgeek_provider_skips_when_no_client_id():
    """Verify provider returns empty array when credentials are missing."""
    provider = SeatGeekProvider(client_id=None)
    events = await provider.fetch_events(GeoPoint(29.95, -90.07), 35.0)
    assert events == []

    health = await provider.healthcheck()
    assert health.status == "disabled"
    assert health.is_healthy is False
