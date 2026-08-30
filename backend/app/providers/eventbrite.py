"""Eventbrite API event ingestion adapter."""

from datetime import datetime, timezone
import httpx

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.providers.base import BaseProvider, GeoPoint, ProviderStatus, RateLimitConfig, RawEvent


def map_eventbrite_category(category_id: str | None) -> str:
    """Map Eventbrite category identifiers to canonical category."""
    # Standard Eventbrite Category IDs
    # 103 = Music, 108 = Sports & Fitness, 105 = Performing & Visual Arts, 110 = Food & Drink
    cat_map = {
        "103": "music",
        "108": "sports",
        "105": "theater",
        "110": "community",
        "113": "community",
        "115": "community",
    }
    return cat_map.get(str(category_id), "other")


class EventbriteProvider(BaseProvider):
    """Ingestion provider connecting to Eventbrite API."""

    provider_name: str = "eventbrite"
    rate_limit: RateLimitConfig = RateLimitConfig(requests_per_minute=30, max_retries=3)

    def __init__(self, api_token: str | None = None) -> None:
        self.api_token = api_token or settings.EVENTBRITE_API_TOKEN
        self.base_url = "https://www.eventbriteapi.com/v3/events/search/"

    async def fetch_events(self, location: GeoPoint, radius_miles: float) -> list[RawEvent]:
        """Query Eventbrite API for events within geographical coordinate radius."""
        if not self.api_token:
            logger.info("Eventbrite API token not configured. Skipping fetch.")
            return []

        headers = {"Authorization": f"Bearer {self.api_token}"}
        params = {
            "location.latitude": str(location.latitude),
            "location.longitude": str(location.longitude),
            "location.within": f"{int(radius_miles)}mi",
            "expand": "venue,logo,ticket_availability",
        }

        raw_events: list[RawEvent] = []

        try:
            async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
                response = await client.get(self.base_url, params=params)
                if response.status_code != 200:
                    logger.warning("Eventbrite search returned HTTP %d: %s", response.status_code, response.text[:100])
                    return []
                data = response.json()

            for item in data.get("events", []):
                event_id = item.get("id")
                name_obj = item.get("name") or {}
                title = name_obj.get("text")
                if not event_id or not title:
                    continue

                start_obj = item.get("start") or {}
                start_iso = start_obj.get("utc") or start_obj.get("local")
                if not start_iso:
                    continue

                venue_data = item.get("venue") or {}
                venue_name = venue_data.get("name", "Local Venue")
                venue_address = venue_data.get("address", {}).get("address_1")
                venue_city = venue_data.get("address", {}).get("city")
                venue_state = venue_data.get("address", {}).get("region")
                venue_postal = venue_data.get("address", {}).get("postal_code")
                v_lat = venue_data.get("latitude")
                v_lon = venue_data.get("longitude")

                logo_obj = item.get("logo") or {}
                image_url = logo_obj.get("original", {}).get("url") or logo_obj.get("url")

                ticket_url = item.get("url", "")
                cat_id = item.get("category_id")

                raw_events.append(
                    RawEvent(
                        source="eventbrite",
                        source_event_id=str(event_id),
                        venue_name=venue_name,
                        venue_address=venue_address,
                        venue_city=venue_city,
                        venue_state=venue_state,
                        venue_postal_code=venue_postal,
                        venue_latitude=float(v_lat) if v_lat else None,
                        venue_longitude=float(v_lon) if v_lon else None,
                        title=title,
                        description=item.get("description", {}).get("text"),
                        category=map_eventbrite_category(cat_id),
                        start_time=start_iso,
                        price_min=0.0 if item.get("is_free") else None,
                        price_max=None,
                        currency=item.get("currency", "USD"),
                        image_url=image_url,
                        ticket_url=ticket_url,
                        is_featured=0,
                    )
                )
        except Exception as exc:
            logger.warning("Error fetching Eventbrite events: %s", exc)

        return raw_events

    async def healthcheck(self) -> ProviderStatus:
        """Verify token against Eventbrite API."""
        if not self.api_token:
            return ProviderStatus(
                provider_name=self.provider_name,
                status="disabled",
                is_healthy=False,
                error_message="Missing EVENTBRITE_API_TOKEN",
            )

        try:
            async with httpx.AsyncClient(timeout=5.0, headers={"Authorization": f"Bearer {self.api_token}"}) as client:
                res = await client.get("https://www.eventbriteapi.com/v3/users/me/")
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
                    error_message=f"HTTP {res.status_code}",
                )
        except Exception as exc:
            return ProviderStatus(
                provider_name=self.provider_name,
                status="unreachable",
                is_healthy=False,
                error_message=str(exc),
            )
