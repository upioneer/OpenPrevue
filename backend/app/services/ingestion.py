"""Ingestion orchestrator, normalization, circuit breaker protection, and deduplication engine."""

from datetime import datetime, timezone
import math
import re
import aiosqlite

from backend.app.core.circuit_breaker import circuit_registry
from backend.app.core.logging import logger
from backend.app.db.session import get_db
from backend.app.providers.base import BaseProvider, GeoPoint, RawEvent
from backend.app.services.telegram.bot import telegram_service


def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points in miles using Haversine formula."""
    radius_earth_miles = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius_earth_miles * c


def generate_canonical_id(name: str) -> str:
    """Generate a sanitized canonical slug from a venue name."""
    clean = re.sub(r"[^\w\s-]", "", name.lower())
    return re.sub(r"[-\s]+", "-", clean).strip("-")


class IngestionService:
    """Orchestrates event fetching, normalization, deduplication, and database persistence."""

    async def sync_provider(
        self,
        provider: BaseProvider,
        center: GeoPoint,
        radius_miles: float,
    ) -> dict[str, int | str]:
        """Execute a full synchronization cycle for a specific provider with circuit breaker protection."""
        started_at = datetime.now(timezone.utc).isoformat()
        breaker = circuit_registry.get_breaker(provider.provider_name)

        if not breaker.can_execute():
            logger.warning(
                "Circuit breaker for [%s] is currently %s. Skipping synchronization run.",
                provider.provider_name,
                breaker.state.value.upper(),
            )
            return {
                "provider": provider.provider_name,
                "status": f"circuit_{breaker.state.value}",
                "events_fetched": 0,
                "events_inserted": 0,
                "events_updated": 0,
                "events_skipped": 0,
                "error": breaker.last_error,
            }

        logger.info("Starting sync for provider: %s", provider.provider_name)

        events_fetched = 0
        events_inserted = 0
        events_updated = 0
        events_skipped = 0
        error_message = None
        status = "success"

        try:
            raw_events = await provider.fetch_events(center, radius_miles)
            events_fetched = len(raw_events)

            async with get_db() as db:
                for raw in raw_events:
                    # Geo-filter if coordinates are provided
                    if raw.venue_latitude is not None and raw.venue_longitude is not None:
                        dist = calculate_haversine_distance(
                            center.latitude,
                            center.longitude,
                            raw.venue_latitude,
                            raw.venue_longitude,
                        )
                        if dist > radius_miles:
                            events_skipped += 1
                            continue

                    venue_id = await self._resolve_or_create_venue(db, raw)
                    result = await self._persist_event(db, raw, venue_id)

                    if result == "inserted":
                        events_inserted += 1
                    elif result == "updated":
                        events_updated += 1
                    else:
                        events_skipped += 1

                await db.commit()

            breaker.record_success()

            # Scan new events against active user watchlists for push notifications
            try:
                await telegram_service.scan_watchlist_and_alert(raw_events)
            except Exception as exc:
                logger.debug("Watchlist scan error during ingestion: %s", exc)

        except Exception as exc:
            status = "failed"
            error_message = str(exc)
            breaker.record_failure(exc)
            logger.error("Ingestion failed for %s: %s", provider.provider_name, exc, exc_info=True)

        completed_at = datetime.now(timezone.utc).isoformat()

        # Record ingestion audit log
        async with get_db() as db:
            await db.execute(
                """
                INSERT INTO ingestion_log
                (provider, started_at, completed_at, status, events_fetched, events_inserted, events_updated, events_skipped, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    provider.provider_name,
                    started_at,
                    completed_at,
                    status,
                    events_fetched,
                    events_inserted,
                    events_updated,
                    events_skipped,
                    error_message,
                ),
            )
            await db.commit()

        return {
            "provider": provider.provider_name,
            "status": status,
            "events_fetched": events_fetched,
            "events_inserted": events_inserted,
            "events_updated": events_updated,
            "events_skipped": events_skipped,
        }

    async def _resolve_or_create_venue(self, db: aiosqlite.Connection, raw: RawEvent) -> str:
        """Resolve canonical venue ID or insert new venue registry entry."""
        canonical_id = generate_canonical_id(raw.venue_name)

        # Check existing alias or venue
        async with db.execute("SELECT venue_id FROM venue_aliases WHERE alias = ?", (raw.venue_name.lower(),)) as cursor:
            alias_row = await cursor.fetchone()
            if alias_row:
                return alias_row["venue_id"]

        async with db.execute("SELECT id FROM venues WHERE id = ?", (canonical_id,)) as cursor:
            venue_row = await cursor.fetchone()
            if venue_row:
                return venue_row["id"]

        # Insert new canonical venue
        await db.execute(
            """
            INSERT INTO venues (id, name, address, city, state, postal_code, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                latitude = COALESCE(venues.latitude, excluded.latitude),
                longitude = COALESCE(venues.longitude, excluded.longitude)
            """,
            (
                canonical_id,
                raw.venue_name,
                raw.venue_address,
                raw.venue_city,
                raw.venue_state,
                raw.venue_postal_code,
                raw.venue_latitude,
                raw.venue_longitude,
            ),
        )

        # Map alias
        await db.execute(
            "INSERT OR IGNORE INTO venue_aliases (alias, venue_id, source) VALUES (?, ?, ?)",
            (raw.venue_name.lower(), canonical_id, raw.source),
        )

        return canonical_id

    async def _persist_event(self, db: aiosqlite.Connection, raw: RawEvent, venue_id: str) -> str:
        """Persist or fuse incoming event into datastore."""
        event_id = f"{raw.source}-{raw.source_event_id}"
        now_iso = datetime.now(timezone.utc).isoformat()

        # Check existing event
        async with db.execute("SELECT id, price_min, price_max FROM events WHERE id = ?", (event_id,)) as cursor:
            existing = await cursor.fetchone()

        if existing:
            # Data fusion: preserve lowest min price, highest max price, update last_seen_at
            new_price_min = min(filter(None, [existing["price_min"], raw.price_min])) if (existing["price_min"] or raw.price_min) else None
            new_price_max = max(filter(None, [existing["price_max"], raw.price_max])) if (existing["price_max"] or raw.price_max) else None

            await db.execute(
                """
                UPDATE events SET
                    title = ?,
                    description = COALESCE(?, description),
                    category = ?,
                    start_time = ?,
                    end_time = ?,
                    price_min = ?,
                    price_max = ?,
                    image_url = COALESCE(?, image_url),
                    ticket_url = ?,
                    is_featured = MAX(is_featured, ?),
                    last_seen_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    raw.title,
                    raw.description,
                    raw.category,
                    raw.start_time,
                    raw.end_time,
                    new_price_min,
                    new_price_max,
                    raw.image_url,
                    raw.ticket_url,
                    raw.is_featured,
                    now_iso,
                    now_iso,
                    event_id,
                ),
            )

            return "updated"

        # Insert new event
        await db.execute(
            """
            INSERT INTO events
            (id, venue_id, title, description, category, start_time, end_time, price_min, price_max, currency, image_url, ticket_url, source, source_event_id, is_featured, status, last_seen_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?)
            """,
            (
                event_id,
                venue_id,
                raw.title,
                raw.description,
                raw.category,
                raw.start_time,
                raw.end_time,
                raw.price_min,
                raw.price_max,
                raw.currency,
                raw.image_url,
                raw.ticket_url,
                raw.source,
                raw.source_event_id,
                raw.is_featured,
                now_iso,
            ),
        )

        # Add ticket link
        await db.execute(
            "INSERT INTO ticket_links (event_id, source, url, label) VALUES (?, ?, ?, ?)",
            (event_id, raw.source, raw.ticket_url, f"Official {raw.source.title()} Tickets"),
        )

        return "inserted"


ingestion_service = IngestionService()
