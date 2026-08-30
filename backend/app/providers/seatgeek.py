"""SeatGeek Platform API event ingestion adapter."""

from datetime import datetime, timezone
import httpx

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.providers.base import BaseProvider, GeoPoint, ProviderStatus, RateLimitConfig, RawEvent


def map_seatgeek_category(event_type: str | None, taxonomies: list[dict] | None) -> str:
    """Map SeatGeek event taxonomy to canonical category."""
    etype = (event_type or "").lower()

    if any(k in etype for k in ("concert", "music", "festival", "band")):
        return "music"
    if any(k in etype for k in (
        "nba", "nfl", "mlb", "mls", "nhl", "soccer", "football", "basketball", "baseball",
        "sports", "boxing", "mma", "formula 1", "f1", "nascar", "indy", "indycar", "motogp",
        "racing", "motorsport", "auto racing"
    )):
        return "sports"
    if any(k in etype for k in ("theater", "theatre", "broadway", "musical", "play", "ballet")):
        return "theater"
    if "comedy" in etype:
        return "comedy"
    if any(k in etype for k in ("family", "community", "festival")):
        return "community"

    if taxonomies:
        for tax in taxonomies:
            name = tax.get("name", "").lower()
            if any(k in name for k in ("concert", "music")):
                return "music"
            if any(k in name for k in ("sports", "racing", "auto racing", "football", "basketball", "baseball", "soccer", "motorsport")):
                return "sports"
            if any(k in name for k in ("theater", "theatre")):
                return "theater"
            if "comedy" in name:
                return "comedy"

    return "other"


class SeatGeekProvider(BaseProvider):
    """Ingestion provider connecting to SeatGeek Platform API."""

    provider_name: str = "seatgeek"
    rate_limit: RateLimitConfig = RateLimitConfig(requests_per_minute=60, max_retries=3)

    def __init__(self, client_id: str | None = None, client_secret: str | None = None) -> None:
        self.client_id = client_id or settings.SEATGEEK_CLIENT_ID
        self.client_secret = client_secret or settings.SEATGEEK_CLIENT_SECRET
        self.base_url = "https://api.seatgeek.com/2/events"

    async def fetch_events(self, location: GeoPoint, radius_miles: float) -> list[RawEvent]:
        """Query SeatGeek API for events within geographical radius."""
        if not self.client_id:
            logger.info("SeatGeek Client ID not configured. Skipping fetch.")
            return []

        params = {
            "client_id": self.client_id,
            "lat": location.latitude,
            "lon": location.longitude,
            "range": f"{int(radius_miles)}mi",
            "per_page": 50,
            "sort": "datetime_local.asc",
        }
        if self.client_secret:
            params["client_secret"] = self.client_secret

        raw_events: list[RawEvent] = []

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

        event_list = data.get("events", [])

        for item in event_list:
            try:
                event_id = item.get("id")
                title = item.get("title")
                if not event_id or not title:
                    continue

                # Venue extraction
                venue_data = item.get("venue") or {}
                venue_name = venue_data.get("name", "Local Venue")
                venue_address = venue_data.get("address")
                venue_city = venue_data.get("city")
                venue_state = venue_data.get("state")
                venue_postal = venue_data.get("postal_code")

                v_lat = None
                v_lon = None
                loc = venue_data.get("location") or {}
                if "lat" in loc and "lon" in loc:
                    try:
                        v_lat = float(loc["lat"])
                        v_lon = float(loc["lon"])
                    except (ValueError, TypeError):
                        pass

                # Date parsing
                start_iso = item.get("datetime_local") or item.get("datetime_utc")
                if not start_iso:
                    continue

                # Price range from stats
                stats = item.get("stats") or {}
                price_min = stats.get("lowest_price")
                price_max = stats.get("highest_price")

                # Image from performers
                image_url = None
                performers = item.get("performers", [])
                if performers:
                    image_url = performers[0].get("image")

                ticket_url = item.get("url", "")
                category = map_seatgeek_category(item.get("type"), item.get("taxonomies"))

                score = item.get("score", 0.0)
                is_featured = 1 if (score and score > 0.65) or category == "sports" else 0

                raw_events.append(
                    RawEvent(
                        source="seatgeek",
                        source_event_id=str(event_id),
                        venue_name=venue_name,
                        venue_address=venue_address,
                        venue_city=venue_city,
                        venue_state=venue_state,
                        venue_postal_code=venue_postal,
                        venue_latitude=v_lat,
                        venue_longitude=v_lon,
                        title=title,
                        description=f"SeatGeek Score: {round(score * 100)}%" if score else None,
                        category=category,
                        start_time=start_iso,
                        price_min=float(price_min) if price_min is not None else None,
                        price_max=float(price_max) if price_max is not None else None,
                        currency="USD",
                        image_url=image_url,
                        ticket_url=ticket_url,
                        is_featured=is_featured,
                    )
                )
            except Exception as exc:
                logger.warning("Error parsing SeatGeek event item: %s", exc)

        return raw_events

    async def healthcheck(self) -> ProviderStatus:
        """Verify client credentials against SeatGeek API."""
        if not self.client_id:
            return ProviderStatus(
                provider_name=self.provider_name,
                status="disabled",
                is_healthy=False,
                error_message="Missing SEATGEEK_CLIENT_ID",
            )

        params = {"client_id": self.client_id, "per_page": 1}
        if self.client_secret:
            params["client_secret"] = self.client_secret

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(self.base_url, params=params)
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
