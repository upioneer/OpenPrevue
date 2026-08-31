"""Event management and retrieval API endpoints with geographic radius enforcement."""

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
import aiosqlite

from backend.app.db.session import get_db
from backend.app.providers.base import GeoPoint
from backend.app.schemas.event import EventResponse, EventUpdate, TicketLinkResponse
from backend.app.services.ingestion import calculate_haversine_distance

router = APIRouter()


async def _fetch_ticket_links(db: aiosqlite.Connection, event_id: str) -> list[TicketLinkResponse]:
    """Fetch all ticket purchase links for an event."""
    async with db.execute("SELECT * FROM ticket_links WHERE event_id = ?", (event_id,)) as cursor:
        rows = await cursor.fetchall()
        return [
            TicketLinkResponse(
                id=row["id"],
                source=row["source"],
                url=row["url"],
                label=row["label"],
                created_at=row["created_at"],
            )
            for row in rows
        ]


@router.get("/events", response_model=list[EventResponse])
async def list_events(
    category: str | None = Query(None, description="Filter by event category"),
    venue_id: str | None = Query(None, description="Filter by canonical venue ID"),
    is_featured: int | None = Query(None, description="Filter featured events (1 or 0)"),
    has_ticket: int | None = Query(None, description="Filter committed/ticketed events (1 or 0)"),
    status: str | None = Query("active", description="Filter by event status (active, stale, archived, all)"),
    search: str | None = Query(None, description="Search term in title or description"),
    enforce_radius: bool = Query(True, description="Strictly filter events within active broadcast radius"),
    limit: int = Query(200, ge=1, le=500),
) -> list[EventResponse]:
    """Retrieve normalized event listings with venue metadata, ticket links, and geographic filtering."""
    query = """
        SELECT
            e.*,
            v.name AS venue_name,
            v.address AS venue_address,
            v.city AS venue_city,
            v.state AS venue_state,
            v.latitude AS venue_latitude,
            v.longitude AS venue_longitude
        FROM events e
        LEFT JOIN venues v ON e.venue_id = v.id
        WHERE 1=1
    """
    params: list[str | int | float] = []

    if status and status != "all":
        query += " AND e.status = ?"
        params.append(status)

    if category:
        query += " AND e.category = ?"
        params.append(category)

    if venue_id:
        query += " AND e.venue_id = ?"
        params.append(venue_id)

    if is_featured is not None:
        query += " AND e.is_featured = ?"
        params.append(is_featured)

    if has_ticket is not None:
        query += " AND e.has_ticket = ?"
        params.append(has_ticket)

    if search:
        query += " AND (e.title LIKE ? OR e.description LIKE ? OR v.name LIKE ?)"
        pattern = f"%{search}%"
        params.extend([pattern, pattern, pattern])

    query += " ORDER BY e.start_time ASC"

    results: list[EventResponse] = []
    async with get_db() as db:
        # Load user geographic settings for proximity enforcement
        center_lat = 40.7128
        center_lon = -74.0060
        radius_miles = 25.0

        if enforce_radius:
            try:
                async with db.execute("SELECT key, value FROM settings WHERE key IN ('latitude', 'longitude', 'radius_miles')") as cursor:
                    settings_rows = await cursor.fetchall()
                    settings_map = {row["key"]: row["value"] for row in settings_rows}
                    if "latitude" in settings_map:
                        center_lat = float(settings_map["latitude"])
                    if "longitude" in settings_map:
                        center_lon = float(settings_map["longitude"])
                    if "radius_miles" in settings_map:
                        radius_miles = float(settings_map["radius_miles"])
            except Exception:
                pass

        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                row_dict = dict(row)
                v_lat = row_dict.get("venue_latitude")
                v_lon = row_dict.get("venue_longitude")

                # Filter out of radius events
                if enforce_radius and v_lat is not None and v_lon is not None:
                    dist = calculate_haversine_distance(center_lat, center_lon, float(v_lat), float(v_lon))
                    if dist > radius_miles:
                        continue

                # Remove raw lat/lon not part of EventResponse model
                row_dict.pop("venue_latitude", None)
                row_dict.pop("venue_longitude", None)

                links = await _fetch_ticket_links(db, row["id"])
                row_dict["ticket_links"] = links
                results.append(EventResponse(**row_dict))

                if len(results) >= limit:
                    break

    return results


@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(event_id: str) -> EventResponse:
    """Retrieve a single event by unique identifier."""
    query = """
        SELECT
            e.*,
            v.name AS venue_name,
            v.address AS venue_address,
            v.city AS venue_city,
            v.state AS venue_state
        FROM events e
        LEFT JOIN venues v ON e.venue_id = v.id
        WHERE e.id = ?
    """
    async with get_db() as db:
        async with db.execute(query, (event_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Event not found")
            event_dict = dict(row)
            links = await _fetch_ticket_links(db, event_id)
            event_dict["ticket_links"] = links
            return EventResponse(**event_dict)


@router.patch("/events/{event_id}", response_model=EventResponse)
async def update_event(event_id: str, payload: EventUpdate) -> EventResponse:
    """Update specific fields of an event, including has_ticket commitment toggle."""
    async with get_db() as db:
        async with db.execute("SELECT id FROM events WHERE id = ?", (event_id,)) as cursor:
            existing = await cursor.fetchone()
            if not existing:
                raise HTTPException(status_code=404, detail="Event not found")

        update_fields: list[str] = []
        params: list[str | int | float | None] = []

        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            update_fields.append(f"{key} = ?")
            params.append(value)

        if update_fields:
            update_fields.append("updated_at = ?")
            params.append(datetime.now(timezone.utc).isoformat())
            params.append(event_id)

            sql = f"UPDATE events SET {', '.join(update_fields)} WHERE id = ?"
            await db.execute(sql, params)
            await db.commit()

    return await get_event(event_id)


class UrlIngestRequest(EventUpdate):
    """Payload for 1-click URL ingestion."""
    url: str
    is_featured: int = 1
    has_ticket: int = 0


@router.post("/events/ingest-url", response_model=dict)
async def ingest_url(payload: UrlIngestRequest) -> dict:
    """Ingest, parse, and persist an event directly from a TripAdvisor, Viator, or generic event URL."""
    from backend.app.providers.travel_wishlist import TravelWishlistProvider
    from backend.app.providers.json_ld import JsonLdEventProvider
    from backend.app.services.ingestion import ingestion_service
    from backend.app.services.websocket import connection_manager

    url = payload.url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        raise HTTPException(status_code=400, detail="Invalid URL format. Must start with http:// or https://")

    # 1. Fetch using TravelWishlistProvider or JsonLdEventProvider
    travel_prov = TravelWishlistProvider(target_urls=[url])
    raw_events = await travel_prov.fetch_events(GeoPoint(latitude=0, longitude=0), 10000)

    if not raw_events:
        jsonld_prov = JsonLdEventProvider(target_urls=[url])
        raw_events = await jsonld_prov.fetch_events(GeoPoint(latitude=0, longitude=0), 10000)

    if not raw_events:
        raise HTTPException(status_code=422, detail="Unable to extract structured event or experience metadata from the provided URL.")

    raw = raw_events[0]
    raw.is_featured = payload.is_featured

    async with get_db() as db:
        venue_id = await ingestion_service._resolve_or_create_venue(db, raw)
        persist_status = await ingestion_service._persist_event(db, raw, venue_id)
        canonical_id = ingestion_service._generate_canonical_event_id(raw, venue_id)

        if payload.has_ticket:
            await db.execute("UPDATE events SET has_ticket = ? WHERE id = ?", (payload.has_ticket, canonical_id))

        await db.commit()

    # Broadcast real-time schedule update to all connected CRT clients
    await connection_manager.broadcast("events_updated", {
        "action": "ingest_url",
        "event_id": canonical_id,
        "title": raw.title,
        "source": raw.source,
    })

    return {
        "status": "success",
        "action": persist_status,
        "event_id": canonical_id,
        "title": raw.title,
        "venue_name": raw.venue_name,
        "start_time": raw.start_time,
        "source": raw.source,
        "ticket_url": raw.ticket_url,
    }

