"""Test ingestion service logic: Haversine distance, slug generation, and deduplication."""

from datetime import datetime, timedelta, timezone

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


async def _insert_purge_probe(db, event_id, start, end=None, has_ticket=0):
    """Insert a minimal event row with controlled timestamps."""
    await db.execute(
        "INSERT OR IGNORE INTO venues (id, name, city, state, is_active)"
        " VALUES ('purge-venue', 'Purge Hall', 'Testville', 'TS', 1)"
    )
    await db.execute(
        "INSERT OR REPLACE INTO events"
        " (id, venue_id, title, category, start_time, end_time, status,"
        " has_ticket, ticket_url, source)"
        " VALUES (?, 'purge-venue', ?, 'music', ?, ?, 'active', ?,"
        " 'https://example.com/tix', 'purge-probe')",
        (event_id, f"Probe {event_id}", start, end, has_ticket),
    )


async def _purge_probe_ids(db):
    """Return the ids of surviving probe rows."""
    async with db.execute("SELECT id FROM events WHERE id LIKE 'purge-%'") as cur:
        return {row["id"] for row in await cur.fetchall()}


@pytest.mark.asyncio
async def test_purge_expired_events_keeps_displayable_listings():
    """Purge removes only events past every listing window plus grace."""
    await init_db()
    from backend.app.db.session import get_db

    now = datetime.now(timezone.utc)
    iso = lambda dt: dt.isoformat()
    old = iso(now - timedelta(hours=72))
    old_end = iso(now - timedelta(hours=72))

    async with get_db() as db:
        try:
            await _insert_purge_probe(db, "purge-future", iso(now + timedelta(hours=48)), iso(now + timedelta(hours=51)))
            await _insert_purge_probe(db, "purge-ongoing", iso(now - timedelta(hours=2)), iso(now + timedelta(hours=1)))
            await _insert_purge_probe(db, "purge-multiday", iso(now - timedelta(hours=48)), iso(now + timedelta(hours=24)))
            await _insert_purge_probe(db, "purge-recent-end", iso(now - timedelta(hours=5)), iso(now - timedelta(hours=2)))
            await _insert_purge_probe(db, "purge-recent-start", iso(now - timedelta(hours=2)))
            await _insert_purge_probe(db, "purge-ticketed", old, old_end, has_ticket=1)
            await _insert_purge_probe(db, "purge-badtime", "not-a-time")
            await _insert_purge_probe(db, "purge-old-end", old, old_end)
            await _insert_purge_probe(db, "purge-old-start", old)
            await db.execute(
                "INSERT INTO ticket_links (event_id, source, url, label)"
                " VALUES ('purge-old-end', 'boxoffice', 'https://example.com/tix', 'Tickets')"
            )
            await db.commit()

            purged = await ingestion_service.purge_expired_events()

            survivors = await _purge_probe_ids(db)
            for kept in (
                "purge-future", "purge-ongoing", "purge-multiday",
                "purge-recent-end", "purge-recent-start",
                "purge-ticketed", "purge-badtime",
            ):
                assert kept in survivors, f"{kept} must survive the purge"
            assert "purge-old-end" not in survivors
            assert "purge-old-start" not in survivors
            assert purged >= 2

            async with db.execute(
                "SELECT COUNT(*) AS n FROM ticket_links WHERE event_id = 'purge-old-end'"
            ) as cur:
                assert (await cur.fetchone())["n"] == 0
        finally:
            await db.execute("DELETE FROM ticket_links WHERE event_id LIKE 'purge-%'")
            await db.execute("DELETE FROM events WHERE id LIKE 'purge-%'")
            await db.commit()
