"""Test ingestion service logic: Haversine distance, slug generation, and deduplication."""

import pytest
from backend.app.providers.base import GeoPoint, RawEvent
from backend.app.services.ingestion import (
    calculate_haversine_distance,
    generate_canonical_id,
    ingestion_service,
)
from backend.app.db.session import init_db


def test_haversine_distance():
    """Verify distance calculation between known coordinates."""
    # Superdome (29.9511, -90.0812) to Saenger Theatre (29.9556, -90.0725) ~0.6 miles
    dist = calculate_haversine_distance(29.9511, -90.0812, 29.9556, -90.0725)
    assert 0.4 < dist < 1.0


def test_generate_canonical_id():
    """Verify canonical slug generation removes punctuation and handles spacing."""
    assert generate_canonical_id("House of Blues New Orleans") == "house-of-blues-new-orleans"
    assert generate_canonical_id("Tipitina's!") == "tipitinas"
    assert generate_canonical_id("The   Fillmore  ") == "the-fillmore"


@pytest.mark.asyncio
async def test_resolve_or_create_venue():
    """Verify venue insertion and canonical alias resolution."""
    await init_db()
    from backend.app.db.session import get_db

    raw = RawEvent(
        source="test",
        source_event_id="test-1",
        venue_name="The Saenger Theatre",
        venue_address="1111 Canal St",
        venue_city="New Orleans",
        venue_state="LA",
        venue_postal_code="70112",
        venue_latitude=29.9556,
        venue_longitude=-90.0725,
        title="Test Musical",
        start_time="2026-09-01T20:00:00Z",
        ticket_url="https://tickets.example.com",
    )

    async with get_db() as db:
        venue_id_1 = await ingestion_service._resolve_or_create_venue(db, raw)
        await db.commit()

        # Second resolution with same alias
        venue_id_2 = await ingestion_service._resolve_or_create_venue(db, raw)
        assert venue_id_1 == venue_id_2 == "the-saenger-theatre"
