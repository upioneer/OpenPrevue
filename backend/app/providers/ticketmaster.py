"""Ticketmaster Discovery API v2 event ingestion adapter."""

from datetime import datetime, timezone
import httpx

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.providers.base import BaseProvider, GeoPoint, ProviderStatus, RateLimitConfig, RawEvent


def map_ticketmaster_category(classifications: list[dict] | None) -> str:
    """Map Ticketmaster classification hierarchy to canonical category."""
    if not classifications:
        return "other"

    primary = classifications[0]
    segment = primary.get("segment", {}).get("name", "").lower()
    genre = primary.get("genre", {}).get("name", "").lower()
    subgenre = primary.get("subGenre", {}).get("name", "").lower()
    combined = f"{segment} {genre} {subgenre}"

    if "music" in combined:
        return "music"
    if any(k in combined for k in (
        "sports", "motorsports", "racing", "formula 1", "f1", "nascar", "indycar", "motogp",
        "nfl", "nba", "mlb", "mls", "football", "basketball", "baseball", "soccer", "hockey"
    )):
        return "sports"
    if any(k in combined for k in ("arts", "theatre", "theater", "broadway", "play", "ballet")):
        return "theater"
    if "comedy" in combined:
        return "comedy"
    if any(k in combined for k in ("community", "family", "cultural", "festival")):
        return "community"

    return "other"


class TicketmasterProvider(BaseProvider):
    """Ingestion provider connecting to Ticketmaster Discovery API."""

    provider_name: str = "ticketmaster"
    rate_limit: RateLimitConfig = RateLimitConfig(requests_per_minute=30, max_retries=3)

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or settings.TICKETMASTER_API_KEY
        self.base_url = "https://app.ticketmaster.com/discovery/v2/events.json"

    async def fetch_events(self, location: GeoPoint, radius_miles: float) -> list[RawEvent]:
        """Query Ticketmaster Discovery API for events within geographical radius."""
        if not self.api_key:
            logger.info("Ticketmaster API key not configured. Skipping fetch.")
            return []

        params = {
            "apikey": self.api_key,
            "latlong": f"{location.latitude},{location.longitude}",
            "radius": str(int(radius_miles)),
            "unit": "miles",
            "size": 50,
            "sort": "date,asc",
        }

        raw_events: list[RawEvent] = []

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

        embedded = data.get("_embedded", {})
        event_list = embedded.get("events", [])

        for item in event_list:
            try:
                event_id = item.get("id")
                title = item.get("name")
                if not event_id or not title:
                    continue

                # Venue extraction
                venues = item.get("_embedded", {}).get("venues", [])
                venue_data = venues[0] if venues else {}
                venue_name = venue_data.get("name", "Local Venue")
                venue_address = venue_data.get("address", {}).get("line1")
                venue_city = venue_data.get("city", {}).get("name")
                venue_state = venue_data.get("state", {}).get("stateCode")
                venue_postal = venue_data.get("postalCode")

                v_lat = None
                v_lon = None
                loc = venue_data.get("location", {})
                if "latitude" in loc and "longitude" in loc:
                    try:
                        v_lat = float(loc["latitude"])
                        v_lon = float(loc["longitude"])
                    except (ValueError, TypeError):
                        pass

                # Date parsing
                start_data = item.get("dates", {}).get("start", {})
                start_iso = start_data.get("dateTime")
                if not start_iso:
                    local_date = start_data.get("localDate")
                    local_time = start_data.get("localTime", "00:00:00")
                    if local_date:
                        start_iso = f"{local_date}T{local_time}"
                    else:
                        continue

                # Price range
                price_min = None
                price_max = None
                currency = "USD"
                price_ranges = item.get("priceRanges", [])
                if price_ranges:
                    price_min = price_ranges[0].get("min")
                    price_max = price_ranges[0].get("max")
                    currency = price_ranges[0].get("currency", "USD")

                # Select highest resolution image
                image_url = None
                images = item.get("images", [])
                if images:
                    best_img = max(images, key=lambda img: img.get("width", 0) * img.get("height", 0))
                    image_url = best_img.get("url")

                ticket_url = item.get("url", "")
                category = map_ticketmaster_category(item.get("classifications"))

                # Featured heuristic: high prominence or major event
                is_featured = 1 if (item.get("promoter") or category in ("sports", "theater") or (price_max and price_max > 80)) else 0

                raw_events.append(
                    RawEvent(
                        source="ticketmaster",
                        source_event_id=str(event_id),
                        venue_name=venue_name,
                        venue_address=venue_address,
                        venue_city=venue_city,
                        venue_state=venue_state,
                        venue_postal_code=venue_postal,
                        venue_latitude=v_lat,
                        venue_longitude=v_lon,
                        title=title,
                        description=item.get("info") or item.get("pleaseNote"),
                        category=category,
                        start_time=start_iso,
                        price_min=float(price_min) if price_min is not None else None,
                        price_max=float(price_max) if price_max is not None else None,
                        currency=currency,
                        image_url=image_url,
                        ticket_url=ticket_url,
                        is_featured=is_featured,
                    )
                )
            except Exception as exc:
                logger.warning("Error parsing Ticketmaster event item: %s", exc)

        return raw_events

    async def healthcheck(self) -> ProviderStatus:
        """Verify API key validity against Discovery API."""
        if not self.api_key:
            return ProviderStatus(
                provider_name=self.provider_name,
                status="disabled",
                is_healthy=False,
                error_message="Missing TICKETMASTER_API_KEY",
            )

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(
                    self.base_url,
                    params={"apikey": self.api_key, "size": 1},
                )
                if res.status_code == 200:
                    return ProviderStatus(
                        provider_name=self.provider_name,
                        status="ok",
                        is_healthy=True,
                        last_sync=datetime.now(timezone.utc),
                    )
                return ProviderStatus(
                    provider_name=self.provider_name,
                    status="degraded",
                    is_healthy=False,
                    error_message=f"HTTP {res.status_code}: {res.text[:100]}",
                )
        except Exception as exc:
            return ProviderStatus(
                provider_name=self.provider_name,
                status="unreachable",
                is_healthy=False,
                error_message=str(exc),
            )
