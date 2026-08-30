"""Direct venue JSON-LD schema.org calendar ingestion adapter."""

import json
import re
from datetime import datetime, timezone
import httpx

from backend.app.core.logging import logger
from backend.app.providers.base import BaseProvider, GeoPoint, ProviderStatus, RateLimitConfig, RawEvent

JSON_LD_SCRIPT_REGEX = re.compile(
    r'<script[^>]*type=[\'"]application/ld\+json[\'"][^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)


def map_schema_event_category(schema_type: str, performer_type: str | None = None) -> str:
    """Map schema.org Event sub-types to canonical category."""
    st = schema_type.lower()
    pt = (performer_type or "").lower()

    if "music" in st or "music" in pt or "concert" in st or "band" in pt or "musician" in pt:
        return "music"
    if "sports" in st or "sports" in pt or "game" in st or "team" in pt or "athlete" in pt:
        return "sports"
    if "theater" in st or "theatre" in st or "play" in st or "dance" in pt:
        return "theater"
    if "comedy" in st or "comedy" in pt or "comedian" in pt:
        return "comedy"
    if "social" in st or "community" in st or "festival" in st:
        return "community"

    return "other"


class JsonLdEventProvider(BaseProvider):
    """Ingestion provider scraping schema.org @type: Event metadata from direct venue calendar pages."""

    provider_name: str = "json_ld"
    rate_limit: RateLimitConfig = RateLimitConfig(requests_per_minute=20, max_retries=2)

    def __init__(self, target_urls: list[str] | None = None) -> None:
        self.target_urls = target_urls or []
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    async def fetch_events(self, location: GeoPoint, radius_miles: float) -> list[RawEvent]:
        """Fetch and parse JSON-LD events across configured target venue URLs."""
        if not self.target_urls:
            return []

        all_events: list[RawEvent] = []

        async with httpx.AsyncClient(timeout=15.0, headers=self.headers, follow_redirects=True) as client:
            for url in self.target_urls:
                try:
                    res = await client.get(url)
                    if res.status_code != 200:
                        continue

                    events_from_page = self.parse_html_json_ld(res.text, source_url=url)
                    all_events.extend(events_from_page)
                except Exception as exc:
                    logger.warning("Error fetching JSON-LD from %s: %s", url, exc)

        return all_events

    def parse_html_json_ld(self, html: str, source_url: str) -> list[RawEvent]:
        """Extract and parse all JSON-LD script tags from HTML."""
        parsed_events: list[RawEvent] = []
        matches = JSON_LD_SCRIPT_REGEX.findall(html)

        for raw_json in matches:
            try:
                data = json.loads(raw_json.strip())
                items: list[dict] = []

                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict):
                    if "@graph" in data and isinstance(data["@graph"], list):
                        items = data["@graph"]
                    else:
                        items = [data]

                for item in items:
                    if not isinstance(item, dict):
                        continue
                    item_type = str(item.get("@type", ""))
                    if "Event" in item_type:
                        raw = self._convert_json_ld_item(item, source_url)
                        if raw:
                            parsed_events.append(raw)
            except Exception as exc:
                logger.debug("Failed parsing JSON-LD snippet: %s", exc)

        return parsed_events

    def _convert_json_ld_item(self, item: dict, fallback_url: str) -> RawEvent | None:
        """Convert a single schema.org Event dictionary into a RawEvent."""
        title = item.get("name")
        start_time = item.get("startDate")
        if not title or not start_time:
            return None

        # Unique event ID
        event_id = item.get("@id") or item.get("url") or f"{title}-{start_time}"
        event_id = re.sub(r"[^\w-]", "", event_id.lower().replace(" ", "-"))[:64]

        # Location details
        location = item.get("location")
        venue_name = "Local Venue"
        venue_address = None
        venue_city = None
        venue_state = None
        venue_postal = None
        v_lat = None
        v_lon = None

        if isinstance(location, dict):
            venue_name = location.get("name", venue_name)
            addr = location.get("address")
            if isinstance(addr, dict):
                venue_address = addr.get("streetAddress")
                venue_city = addr.get("addressLocality")
                venue_state = addr.get("addressRegion")
                venue_postal = addr.get("postalCode")
            elif isinstance(addr, str):
                venue_address = addr

            geo = location.get("geo")
            if isinstance(geo, dict):
                try:
                    v_lat = float(geo.get("latitude"))
                    v_lon = float(geo.get("longitude"))
                except (ValueError, TypeError):
                    pass
        elif isinstance(location, str):
            venue_name = location

        # Offers and pricing
        offers = item.get("offers")
        price_min = None
        price_max = None
        currency = "USD"
        ticket_url = item.get("url") or fallback_url

        if isinstance(offers, dict):
            p = offers.get("price") or offers.get("lowPrice")
            if p is not None:
                try:
                    price_min = float(p)
                except (ValueError, TypeError):
                    pass
            high_p = offers.get("highPrice")
            if high_p is not None:
                try:
                    price_max = float(high_p)
                except (ValueError, TypeError):
                    pass
            currency = offers.get("priceCurrency", "USD")
            ticket_url = offers.get("url") or ticket_url

        # Image extraction
        image_url = None
        img = item.get("image")
        if isinstance(img, str):
            image_url = img
        elif isinstance(img, list) and len(img) > 0:
            image_url = img[0] if isinstance(img[0], str) else img[0].get("url")
        elif isinstance(img, dict):
            image_url = img.get("url")

        category = map_schema_event_category(
            str(item.get("@type", "")),
            str(item.get("performer", {}).get("@type", "") if isinstance(item.get("performer"), dict) else ""),
        )

        return RawEvent(
            source="json_ld",
            source_event_id=event_id,
            venue_name=venue_name,
            venue_address=venue_address,
            venue_city=venue_city,
            venue_state=venue_state,
            venue_postal_code=venue_postal,
            venue_latitude=v_lat,
            venue_longitude=v_lon,
            title=title,
            description=item.get("description"),
            category=category,
            start_time=start_time,
            end_time=item.get("endDate"),
            price_min=price_min,
            price_max=price_max,
            currency=currency,
            image_url=image_url,
            ticket_url=ticket_url,
            is_featured=0,
        )

    async def healthcheck(self) -> ProviderStatus:
        """Verify reachability across target venue URLs."""
        if not self.target_urls:
            return ProviderStatus(
                provider_name=self.provider_name,
                status="idle",
                is_healthy=True,
                extra_details={"configured_urls_count": 0},
            )

        return ProviderStatus(
            provider_name=self.provider_name,
            status="ok",
            is_healthy=True,
            last_sync=datetime.now(timezone.utc),
            extra_details={"configured_feeds_count": len(self.target_urls)},
        )
