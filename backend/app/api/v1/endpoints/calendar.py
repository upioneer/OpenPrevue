"""Outbound RFC 5545 iCalendar (.ics) subscription feeds and event pass exporter."""

from datetime import datetime, timezone
import re
from fastapi import APIRouter, HTTPException, Query, Response
import aiosqlite

from backend.app.core.logging import logger
from backend.app.db.session import get_db

router = APIRouter(prefix="/calendar")


def _format_ics_datetime(dt_str: str | None) -> str:
    """Convert ISO datetime string to RFC 5545 format (YYYYMMDDTHHMMSSZ)."""
    if not dt_str:
        return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    try:
        clean = dt_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean)
        # Convert to UTC
        if dt.tzinfo is not None:
            dt_utc = dt.astimezone(timezone.utc)
        else:
            dt_utc = dt
        return dt_utc.strftime("%Y%m%dT%H%M%SZ")
    except Exception:
        # Fallback to current time
        return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _escape_ics_text(text: str | None) -> str:
    """Escape special characters according to RFC 5545 specification."""
    if not text:
        return ""
    # Remove emojis and sanitize
    clean = re.sub(r"[^\x00-\x7F]+", " ", str(text))
    clean = clean.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n").replace("\r", "")
    return clean.strip()


def _build_ics_event_block(row_data: aiosqlite.Row | dict) -> str:
    """Build a single VEVENT block adhering to RFC 5545."""
    row = dict(row_data)
    event_id = row["id"]
    title = _escape_ics_text(row["title"])
    desc = _escape_ics_text(row.get("description") or "Local event listing from OpenPrevue.")
    venue_name = _escape_ics_text(row.get("venue_name") or "Local Venue")
    venue_address = _escape_ics_text(row.get("venue_address") or "")
    venue_city = _escape_ics_text(row.get("venue_city") or "")
    venue_state = _escape_ics_text(row.get("venue_state") or "")
    
    location_parts = [p for p in [venue_name, venue_address, venue_city, venue_state] if p]
    location_str = ", ".join(location_parts)

    dtstart = _format_ics_datetime(row.get("start_time"))
    dtend = _format_ics_datetime(row.get("end_time"))
    
    # If dtend matches dtstart or is missing, set default 2 hour duration
    if dtend == dtstart:
        try:
            start_dt = datetime.strptime(dtstart, "%Y%m%dT%H%M%SZ")
            from datetime import timedelta
            end_dt = start_dt + timedelta(hours=2)
            dtend = end_dt.strftime("%Y%m%dT%H%M%SZ")
        except Exception:
            pass

    dtstamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    ticket_url = row.get("ticket_url") or "http://localhost:8080"
    category = _escape_ics_text((row.get("category") or "EVENT").upper())

    p_min = row.get("price_min")
    p_max = row.get("price_max")
    price_info = ""
    if p_min is not None and p_max is not None:
        price_info = f"Price: ${p_min:.2f} - ${p_max:.2f}" if p_min != p_max else f"Price: ${p_min:.2f}"
    elif p_min is not None:
        price_info = f"Price: ${p_min:.2f}"

    full_description = desc
    if price_info:
        full_description += f"\\n\\n{price_info}"
    if ticket_url:
        full_description += f"\\nTickets: {ticket_url}"

    lines = [
        "BEGIN:VEVENT",
        f"UID:{event_id}@openprevue.local",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART:{dtstart}",
        f"DTEND:{dtend}",
        f"SUMMARY:{title}",
        f"LOCATION:{location_str}",
        f"DESCRIPTION:{full_description}",
        f"URL:{ticket_url}",
        f"CATEGORIES:{category}",
        "STATUS:CONFIRMED",
        "BEGIN:VALARM",
        "ACTION:DISPLAY",
        f"DESCRIPTION:Reminder for {title}",
        "TRIGGER:-PT2H",
        "END:VALARM",
        "END:VEVENT",
    ]
    return "\r\n".join(lines)


@router.get("/feed.ics")
async def get_ical_feed(
    filter: str = Query(default="committed", description="Filter events: committed (has_ticket=1), featured, or all"),
    limit: int = Query(default=200, ge=1, le=1000, description="Max calendar items to include"),
) -> Response:
    """Generate RFC 5545 iCalendar feed compatible with Apple Calendar, Google Calendar, and Outlook."""
    query = """
        SELECT
            e.id,
            e.title,
            e.description,
            e.category,
            e.start_time,
            e.end_time,
            e.price_min,
            e.price_max,
            e.currency,
            e.ticket_url,
            e.is_featured,
            e.has_ticket,
            v.name AS venue_name,
            v.address AS venue_address,
            v.city AS venue_city,
            v.state AS venue_state
        FROM events e
        JOIN venues v ON e.venue_id = v.id
        WHERE e.status = 'active'
    """
    params: list[str | int] = []

    filter_clean = filter.lower().strip()
    if filter_clean == "committed":
        query += " AND e.has_ticket = 1"
    elif filter_clean == "featured":
        query += " AND e.is_featured = 1"
    elif filter_clean != "all":
        query += " AND e.has_ticket = 1"

    query += " ORDER BY e.start_time ASC LIMIT ?"
    params.append(limit)

    metro_label = "Local Guide"
    async with get_db() as db:
        try:
            async with db.execute("SELECT value FROM settings WHERE key = 'metro_label'") as cursor:
                row = await cursor.fetchone()
                if row and row["value"]:
                    metro_label = row["value"].strip()
        except Exception:
            pass

        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()

    vevent_blocks = [_build_ics_event_block(row) for row in rows]

    cal_name = f"OpenPrevue - {metro_label}"
    if filter_clean == "committed":
        cal_name += " (My Tickets)"
    elif filter_clean == "featured":
        cal_name += " (Spotlight Events)"

    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//OpenPrevue//Event Aggregator 1.0//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{_escape_ics_text(cal_name)}",
        f"X-WR-CALDESC:Synchronized local events from OpenPrevue.",
        "X-PUBLISHED-TTL:PT1H",
        "REFRESH-INTERVAL;VALUE=DURATION:PT1H",
    ]

    if vevent_blocks:
        ics_lines.extend(vevent_blocks)

    ics_lines.append("END:VCALENDAR")
    ics_content = "\r\n".join(ics_lines) + "\r\n"

    filename = f"openprevue-{filter_clean}.ics"
    return Response(
        content=ics_content,
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": f'inline; filename="{filename}"',
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )


@router.get("/events/{event_id}.ics")
async def get_single_event_ics(event_id: str) -> Response:
    """Download single event as an .ics file for 1-click import to mobile / desktop calendar."""
    query = """
        SELECT
            e.id,
            e.title,
            e.description,
            e.category,
            e.start_time,
            e.end_time,
            e.price_min,
            e.price_max,
            e.currency,
            e.ticket_url,
            e.is_featured,
            e.has_ticket,
            v.name AS venue_name,
            v.address AS venue_address,
            v.city AS venue_city,
            v.state AS venue_state
        FROM events e
        JOIN venues v ON e.venue_id = v.id
        WHERE e.id = ?
    """
    async with get_db() as db:
        async with db.execute(query, (event_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Event not found")

    event_block = _build_ics_event_block(row)
    title_slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", row["title"])[:30].strip("_")

    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//OpenPrevue//Event Aggregator 1.0//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{_escape_ics_text(row['title'])}",
        event_block,
        "END:VCALENDAR",
    ]
    ics_content = "\r\n".join(ics_lines) + "\r\n"

    return Response(
        content=ics_content,
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="openprevue-{title_slug}.ics"',
        },
    )


@router.get("/subscribe-urls")
async def get_subscription_urls() -> dict:
    """Retrieve formatted webcal:// and https:// calendar subscription endpoints."""
    return {
        "committed": {
            "name": "Committed Tickets ([TICKET] events)",
            "path": "/api/v1/calendar/feed.ics?filter=committed",
            "description": "Events you marked with a ticket commitment.",
        },
        "featured": {
            "name": "Spotlight Events",
            "path": "/api/v1/calendar/feed.ics?filter=featured",
            "description": "Curated headline concerts, games, and theater.",
        },
        "all": {
            "name": "All Active Metro Listings",
            "path": "/api/v1/calendar/feed.ics?filter=all",
            "description": "Entire aggregated community schedule.",
        },
    }
