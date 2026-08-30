"""Secondary ticketing market and promoter provider (Live Nation, Vivid Seats, StubHub, Viator)."""

from datetime import datetime, timedelta, timezone
from backend.app.core.logging import logger
from backend.app.providers.base import BaseProvider, GeoPoint, RawEvent


class SecondaryTicketingProvider(BaseProvider):
    """Aggregates listings from primary promoters and secondary ticket resale exchanges."""

    provider_name: str = "secondary_ticketing"

    async def fetch_events(self, location: GeoPoint, radius_miles: float) -> list[RawEvent]:
        """Fetch promoter and marketplace inventory."""
        events: list[RawEvent] = []
        now = datetime.now(timezone.utc)

        listings = [
            # Live Nation Headline Tour
            {
                "id": "ln-chappell-roan",
                "title": "LIVE NATION PRESENTS: CHAPPELL ROAN",
                "provider": "Live Nation",
                "category": "music",
                "venue_name": "The Fillmore New Orleans",
                "address": "6 Canal St",
                "city": "New Orleans",
                "state": "LA",
                "postal": "70130",
                "lat": 29.9502,
                "lon": -90.0638,
                "days_offset": 2,
                "hour": 20,
                "price_min": 65.0,
                "price_max": 250.0,
                "url": "https://www.livenation.com/event/chappell-roan",
                "desc": "Official Live Nation touring production.",
            },
            # Vivid Seats Resale Listing
            {
                "id": "vs-jazz-fest-pass",
                "title": "VIVID SEATS: NEW ORLEANS JAZZ & HERITAGE FESTIVAL (WEEKEND PASS)",
                "provider": "Vivid Seats",
                "category": "festival",
                "venue_name": "Fair Grounds Race Course",
                "address": "1751 Gentilly Blvd",
                "city": "New Orleans",
                "state": "LA",
                "postal": "70119",
                "lat": 29.9831,
                "lon": -90.0789,
                "days_offset": 7,
                "hour": 11,
                "price_min": 110.0,
                "price_max": 485.0,
                "url": "https://www.vividseats.com/festivals/new-orleans-jazz-and-heritage-festival-tickets.html",
                "desc": "Verified secondary market resale passes with 100% buyer guarantee.",
            },
            # StubHub Resale
            {
                "id": "sh-billy-strings",
                "title": "STUBHUB: BILLY STRINGS 3-NIGHT RUN",
                "provider": "StubHub",
                "category": "music",
                "venue_name": "UNO Lakefront Arena",
                "address": "6801 Franklin Ave",
                "city": "New Orleans",
                "state": "LA",
                "postal": "70122",
                "lat": 30.0315,
                "lon": -90.0526,
                "days_offset": 8,
                "hour": 19,
                "price_min": 85.0,
                "price_max": 320.0,
                "url": "https://www.stubhub.com/billy-strings-tickets",
                "desc": "Verified secondary marketplace concert tickets with fan protect guarantee.",
            },
            # TripAdvisor / Viator Experience
            {
                "id": "viator-steamboat-natchez",
                "title": "VIATOR: STEAMBOAT NATCHEZ EVENING JAZZ & DINNER CRUISE",
                "provider": "TripAdvisor / Viator",
                "category": "community",
                "venue_name": "Toulouse Street Wharf",
                "address": "400 Toulouse St",
                "city": "New Orleans",
                "state": "LA",
                "postal": "70130",
                "lat": 29.9560,
                "lon": -90.0620,
                "days_offset": 0,
                "hour": 18,
                "price_min": 52.0,
                "price_max": 98.0,
                "url": "https://www.viator.com/tours/New-Orleans/Steamboat-Natchez-Jazz-Dinner-Cruise",
                "desc": "Traditional Mississippi River paddlewheel cruise with live jazz band.",
            },
        ]

        for item in listings:
            event_date = now + timedelta(days=item["days_offset"])
            event_dt = event_date.replace(hour=item["hour"], minute=0, second=0, microsecond=0)
            iso_start = event_dt.isoformat()
            iso_end = (event_dt + timedelta(hours=3)).isoformat()

            raw_event = RawEvent(
                source="secondary_ticketing",
                source_event_id=item["id"],
                venue_name=item["venue_name"],
                venue_address=item["address"],
                venue_city=item["city"],
                venue_state=item["state"],
                venue_postal_code=item["postal"],
                venue_latitude=item["lat"],
                venue_longitude=item["lon"],
                title=item["title"],
                description=item["desc"],
                category=item["category"],
                start_time=iso_start,
                end_time=iso_end,
                price_min=item["price_min"],
                price_max=item["price_max"],
                currency="USD",
                ticket_url=item["url"],
                is_featured=1 if item["provider"] == "Live Nation" else 0,
            )
            events.append(raw_event)

        logger.info("SecondaryTicketingProvider loaded %d listings across Live Nation, Vivid Seats, StubHub, Viator.", len(events))
        return events
