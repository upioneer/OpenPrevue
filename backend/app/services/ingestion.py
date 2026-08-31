"""Ingestion orchestrator, normalization, circuit breaker protection, and deduplication engine."""

from datetime import datetime, timezone
import math
import re
import aiosqlite

from backend.app.core.circuit_breaker import circuit_registry
from backend.app.core.config import settings
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

    async def sync_all_registered_providers(self) -> dict[str, int | str]:
        """Trigger synchronization cycle across all registered providers using active system settings."""
        from backend.app.providers.registry import provider_registry

        async with get_db() as db:
            async with db.execute("SELECT key, value FROM settings") as cursor:
                rows = await cursor.fetchall()
                settings_map = {row["key"]: row["value"] for row in rows}

        lat = float(settings_map.get("latitude", settings.DEFAULT_LATITUDE))
        lon = float(settings_map.get("longitude", settings.DEFAULT_LONGITUDE))
        radius = float(settings_map.get("radius_miles", settings.DEFAULT_RADIUS_MILES))
        center = GeoPoint(latitude=lat, longitude=lon)

        # Configure dynamic provider parameters
        tm_prov = provider_registry.get("ticketmaster")
        if tm_prov and hasattr(tm_prov, "api_key"):
            tm_prov.api_key = settings_map.get("ticketmaster_api_key", "")

        sg_prov = provider_registry.get("seatgeek")
        if sg_prov and hasattr(sg_prov, "client_id"):
            sg_prov.client_id = settings_map.get("seatgeek_client_id", "")

        viator_prov = provider_registry.get("viator")
        if viator_prov and hasattr(viator_prov, "api_key"):
            viator_prov.api_key = settings_map.get("viator_api_key", "")

        travel_prov = provider_registry.get("travel_wishlist")
        if travel_prov and hasattr(travel_prov, "target_urls"):
            wishlist_urls = []
            if settings_map.get("tripadvisor_wishlist_url"):
                wishlist_urls.append(settings_map["tripadvisor_wishlist_url"].strip())
            if settings_map.get("viator_wishlist_url"):
                wishlist_urls.append(settings_map["viator_wishlist_url"].strip())
            travel_prov.target_urls = [u for u in wishlist_urls if u]

        total_inserted = 0
        total_updated = 0
        for provider in provider_registry.get_all():
            res = await self.sync_provider(provider, center, radius)
            total_inserted += int(res.get("events_inserted", 0))
            total_updated += int(res.get("events_updated", 0))

        return {
            "status": "completed",
            "events_inserted": total_inserted,
            "events_updated": total_updated,
        }

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
        return canonical_id

    async def _persist_event(self, db: aiosqlite.Connection, raw: RawEvent, venue_id: str) -> str:
        """Deduplicate and insert or update event record."""
        event_id = f"{raw.source}-{raw.source_event_id}"
        now_iso = datetime.now(timezone.utc).isoformat()

        # Check existing event by ID
        async with db.execute("SELECT id, updated_at FROM events WHERE id = ?", (event_id,)) as cursor:
            existing = await cursor.fetchone()

        # Fuzzy match title and venue within 24 hours to prevent cross-provider duplicates
        if not existing:
            async with db.execute(
                """
                SELECT id FROM events
                WHERE venue_id = ?
                AND lower(title) = lower(?)
                AND abs(strftime('%s', start_time) - strftime('%s', ?)) < 86400
                """,
                (venue_id, raw.title, raw.start_time),
            ) as cursor:
                fuzzy_match = await cursor.fetchone()
                if fuzzy_match:
                    event_id = fuzzy_match["id"]
                    existing = fuzzy_match

        if existing:
            # Update existing event record
            await db.execute(
                """
                UPDATE events SET
                    venue_id = ?,
                    title = ?,
                    description = COALESCE(?, description),
                    category = ?,
                    start_time = ?,
                    end_time = COALESCE(?, end_time),
                    price_min = COALESCE(?, price_min),
                    price_max = COALESCE(?, price_max),
                    image_url = COALESCE(?, image_url),
                    ticket_url = COALESCE(?, ticket_url),
                    is_featured = ?,
                    status = 'active',
                    last_seen_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    venue_id,
                    raw.title,
                    raw.description,
                    raw.category,
                    raw.start_time,
                    raw.end_time,
                    raw.price_min,
                    raw.price_max,
                    raw.image_url,
                    raw.ticket_url,
                    raw.is_featured,
                    now_iso,
                    now_iso,
                    event_id,
                ),
            )

            # Insert or update secondary ticket link
            await db.execute(
                """
                INSERT INTO ticket_links (event_id, source, url, label)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(event_id, source) DO UPDATE SET
                    url = excluded.url,
                    label = excluded.label
                """,
                (
                    event_id,
                    raw.source,
                    raw.ticket_url,
                    f"Official {raw.source.title()} Tickets",
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
