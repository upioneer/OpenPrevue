"""Unit and integration tests for Sports Leagues and Secondary Ticketing providers."""

import pytest
from backend.app.providers.base import GeoPoint
from backend.app.providers.sports import SportsLeagueProvider
from backend.app.providers.ticketing import SecondaryTicketingProvider
from backend.app.services.ingestion import ingestion_service


@pytest.mark.asyncio
async def test_sports_leagues_provider_fixtures():
    """Verify SportsLeagueProvider returns F1, NASCAR, IndyCar, MotoGP, NFL, NBA, MLB, MLS fixtures."""
    provider = SportsLeagueProvider()
    center = GeoPoint(latitude=29.9511, longitude=-90.0715)
    events = await provider.fetch_events(center, 50.0)

    assert len(events) >= 8
    titles = [e.title for e in events]
    assert any("FORMULA 1" in t for t in titles)
    assert any("NASCAR" in t for t in titles)
    assert any("INDYCAR" in t for t in titles)
    assert any("MOTOGP" in t for t in titles)
    assert any("SAINTS" in t for t in titles)
    assert any("PELICANS" in t for t in titles)

    for event in events:
        assert event.category == "sports"
        assert event.price_min is not None
        assert bool(event.ticket_url)


@pytest.mark.asyncio
async def test_secondary_ticketing_provider_listings():
    """Verify SecondaryTicketingProvider returns Live Nation, Vivid Seats, StubHub, and Viator events."""
    provider = SecondaryTicketingProvider()
    center = GeoPoint(latitude=29.9511, longitude=-90.0715)
    events = await provider.fetch_events(center, 50.0)

    assert len(events) >= 4
    titles = [e.title for e in events]
    assert any("LIVE NATION" in t for t in titles)
    assert any("VIVID SEATS" in t for t in titles)
    assert any("STUBHUB" in t for t in titles)
    assert any("VIATOR" in t for t in titles)


@pytest.mark.asyncio
async def test_sports_and_ticketing_ingestion_sync():
    """Verify ingestion pipeline syncs sports and ticketing providers into SQLite."""
    center = GeoPoint(latitude=29.9511, longitude=-90.0715)

    sports_prov = SportsLeagueProvider()
    sports_res = await ingestion_service.sync_provider(sports_prov, center, 100.0)
    assert sports_res["status"] == "success"
    assert sports_res["events_fetched"] >= 8

    ticket_prov = SecondaryTicketingProvider()
    ticket_res = await ingestion_service.sync_provider(ticket_prov, center, 50.0)
    assert ticket_res["status"] == "success"
    assert ticket_res["events_fetched"] >= 4
