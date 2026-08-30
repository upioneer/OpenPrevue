"""Event management and retrieval API endpoints."""

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
import aiosqlite

from backend.app.db.session import get_db
from backend.app.schemas.event import EventResponse, EventUpdate, TicketLinkResponse

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
    status: str | None = Query("active", description="Filter by event status (active, stale, archived, all)"),
    search: str | None = Query(None, description="Search term in title or description"),
    limit: int = Query(200, ge=1, le=500),
) -> list[EventResponse]:
    """Retrieve normalized event listings with venue metadata and ticket links."""
    query = """
        SELECT
            e.*,
            v.name AS venue_name,
            v.address AS venue_address,
            v.city AS venue_city,
            v.state AS venue_state
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

    if search:
        query += " AND (e.title LIKE ? OR e.description LIKE ? OR v.name LIKE ?)"
        pattern = f"%{search}%"
        params.extend([pattern, pattern, pattern])

    query += " ORDER BY e.start_time ASC LIMIT ?"
    params.append(limit)

    results: list[EventResponse] = []
    async with get_db() as db:
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                event_dict = dict(row)
                links = await _fetch_ticket_links(db, row["id"])
                event_dict["ticket_links"] = links
                results.append(EventResponse(**event_dict))

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
    """Update specific fields of an event."""
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
