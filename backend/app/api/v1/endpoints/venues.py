"""Venue registry and metadata API endpoints."""

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from backend.app.db.session import get_db
from backend.app.schemas.venue import VenueCreate, VenueResponse, VenueUpdate

router = APIRouter()


@router.get("/venues", response_model=list[VenueResponse])
async def list_venues() -> list[VenueResponse]:
    """List all canonical venues in display priority order."""
    query = "SELECT * FROM venues WHERE is_active = 1 ORDER BY custom_order ASC, name ASC"
    async with get_db() as db:
        async with db.execute(query) as cursor:
            rows = await cursor.fetchall()
            return [VenueResponse(**dict(row)) for row in rows]


@router.post("/venues", response_model=VenueResponse, status_code=201)
async def create_venue(payload: VenueCreate) -> VenueResponse:
    """Register a new canonical venue."""
    now_iso = datetime.now(timezone.utc).isoformat()
    async with get_db() as db:
        async with db.execute("SELECT id FROM venues WHERE id = ?", (payload.id,)) as cursor:
            if await cursor.fetchone():
                raise HTTPException(status_code=409, detail=f"Venue with id '{payload.id}' already exists")

        await db.execute(
            """
            INSERT INTO venues
            (id, name, address, city, state, postal_code, latitude, longitude, timezone, custom_order, is_active, needs_review, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.id,
                payload.name,
                payload.address,
                payload.city,
                payload.state,
                payload.postal_code,
                payload.latitude,
                payload.longitude,
                payload.timezone,
                payload.custom_order,
                payload.is_active,
                payload.needs_review,
                now_iso,
                now_iso,
            ),
        )
        await db.commit()

    return await get_venue(payload.id)


@router.get("/venues/{venue_id}", response_model=VenueResponse)
async def get_venue(venue_id: str) -> VenueResponse:
    """Retrieve details for a specific canonical venue."""
    async with get_db() as db:
        async with db.execute("SELECT * FROM venues WHERE id = ?", (venue_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Venue not found")
            return VenueResponse(**dict(row))


@router.patch("/venues/{venue_id}", response_model=VenueResponse)
async def update_venue(venue_id: str, payload: VenueUpdate) -> VenueResponse:
    """Update metadata or display ordering for a venue."""
    async with get_db() as db:
        async with db.execute("SELECT id FROM venues WHERE id = ?", (venue_id,)) as cursor:
            if not await cursor.fetchone():
                raise HTTPException(status_code=404, detail="Venue not found")

        update_fields: list[str] = []
        params: list[str | int | float | None] = []

        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            update_fields.append(f"{key} = ?")
            params.append(value)

        if update_fields:
            update_fields.append("updated_at = ?")
            params.append(datetime.now(timezone.utc).isoformat())
            params.append(venue_id)

            sql = f"UPDATE venues SET {', '.join(update_fields)} WHERE id = ?"
            await db.execute(sql, params)
            await db.commit()

    return await get_venue(venue_id)
