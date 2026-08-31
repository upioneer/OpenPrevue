"""TripAdvisor and Viator public trip/wishlist URL ingestion adapter."""

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any
import httpx

from backend.app.core.logging import logger
from backend.app.providers.base import BaseProvider, GeoPoint, ProviderStatus, RateLimitConfig, RawEvent

JSON_LD_SCRIPT_REGEX = re.compile(
    r'<script[^>]*type=[\'"]application/ld\+json[\'"][^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)

OG_TAG_REGEX = re.compile(
    r'<meta[^>]+(?:property|name)=[\'"](og:[a-zA-Z0-9_:]+|twitter:[a-zA-Z0-9_:]+|description)[\'"][^>]+content=[\'"]([^\'"]*)[\'"]',
    re.IGNORECASE,
)

PRICE_REGEX = re.compile(r'\$([0-9]+(?:\.[0-9]{2})?)')


def extract_opengraph_meta(html: str) -> dict[str, str]:
    """Extract standard OpenGraph and Twitter meta tags from HTML."""
    tags: dict[str, str] = {}
    matches = OG_TAG_REGEX.findall(html)
    for key, val in matches:
        tags[key.lower()] = val.strip()
    return tags


def map_travel_category(title: str, description: str = "") -> str:
    """Map travel activity or tour to canonical OpenPrevue category."""
    text = (title + " " + description).lower()
    if any(k in text for k in ["comedy", "standup", "improv"]):
        return "comedy"
    if any(k in text for k in ["theater", "theatre", "broadway", "musical", "play", "cabaret", "ballet"]):
        return "theater"
    if any(k in text for k in ["concert", "live band", "jazz", "opera", "orchestra", "symphony", "music"]):
        return "music"
    if any(k in text for k in ["game", "stadium", "sports", "match", "race", "arena", "ballpark"]):
        return "sports"
    if any(k in text for k in ["food", "tasting", "wine", "brewery", "dinner", "culinary", "market", "festival", "tour", "cruise", "sightseeing"]):
        return "community"
    return "community"


class TravelWishlistProvider(BaseProvider):
    """Ingestion provider scraping public TripAdvisor & Viator wishlist and trip URLs."""

    provider_name: str = "travel_wishlist"
    rate_limit: RateLimitConfig = RateLimitConfig(requests_per_minute=30, max_retries=2)

    def __init__(self, target_urls: list[str] | None = None) -> None:
        self.target_urls = [u.strip() for u in (target_urls or []) if u and u.strip()]
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    async def fetch_events(self, location: GeoPoint, radius_miles: float) -> list[RawEvent]:
        """Fetch and parse events across configured TripAdvisor and Viator wishlist URLs."""
        if not self.target_urls:
            return []

        all_events: list[RawEvent] = []

        async with httpx.AsyncClient(timeout=20.0, headers=self.headers, follow_redirects=True) as client:
            for url in self.target_urls:
                try:
                    res = await client.get(url)
                    if res.status_code != 200:
                        logger.warning("Travel wishlist fetch status %d for %s", res.status_code, url)
                        continue

                    events_from_page = self.parse_html_page(res.text, source_url=url)
                    all_events.extend(events_from_page)
                except Exception as exc:
                    logger.warning("Error fetching travel wishlist from %s: %s", url, exc)

        return all_events

    def parse_html_page(self, html: str, source_url: str) -> list[RawEvent]:
        """Parse TripAdvisor or Viator page using JSON-LD, ItemList, or OpenGraph fallbacks."""
        events: list[RawEvent] = []
        is_tripadvisor = "tripadvisor" in source_url.lower()
        is_viator = "viator" in source_url.lower()
        source_tag = "tripadvisor" if is_tripadvisor else ("viator" if is_viator else "travel_wishlist")

        # 1. Parse Schema.org JSON-LD scripts
        matches = JSON_LD_SCRIPT_REGEX.findall(html)
        for raw_json in matches:
            try:
                data = json.loads(raw_json.strip())
                items: list[dict[str, Any]] = []

                if isinstance(data, list):
                    items = [x for x in data if isinstance(x, dict)]
                elif isinstance(data, dict):
                    if "@graph" in data and isinstance(data["@graph"], list):
                        items = [x for x in data["@graph"] if isinstance(x, dict)]
                    elif "itemListElement" in data and isinstance(data["itemListElement"], list):
                        for el in data["itemListElement"]:
                            if isinstance(el, dict):
                                item_obj = el.get("item") or el
                                if isinstance(item_obj, dict):
                                    items.append(item_obj)
                    else:
                        items = [data]

                for item in items:
                    parsed = self._extract_event_from_json_ld(item, source_url, source_tag)
                    if parsed:
                        events.append(parsed)
            except Exception as exc:
                logger.debug("Failed parsing JSON-LD in travel wishlist: %s", exc)

        # 2. Fallback to OpenGraph / Meta scraping if no JSON-LD items were found
        if not events:
            og = extract_opengraph_meta(html)
            title = og.get("og:title") or og.get("twitter:title")
            if title and "page not found" not in title.lower():
                desc = og.get("og:description") or og.get("description") or ""
                img = og.get("og:image") or og.get("twitter:image")
                
                # Check for price in text
                price_min = None
                p_match = PRICE_REGEX.search(desc)
                if p_match:
                    try:
                        price_min = float(p_match.group(1))
                    except ValueError:
                        pass

                url_hash = hashlib.md5(source_url.encode("utf-8")).hexdigest()[:12]
                now_iso = datetime.now(timezone.utc).isoformat()
                
                venue_candidate = "TripAdvisor Experience" if is_tripadvisor else ("Viator Tour" if is_viator else "Travel Experience")
                clean_title = re.sub(r'\s*\|\s*(Tripadvisor|Viator).*$', '', title, flags=re.IGNORECASE).strip()

                events.append(
                    RawEvent(
                        source=source_tag,
                        source_event_id=f"wishlist_{url_hash}",
                        venue_name=venue_candidate,
                        venue_address=None,
                        venue_city=None,
                        venue_state=None,
                        venue_postal_code=None,
                        venue_latitude=None,
                        venue_longitude=None,
                        title=clean_title,
                        description=desc,
                        category=map_travel_category(clean_title, desc),
                        start_time=now_iso,
                        end_time=None,
                        price_min=price_min,
                        price_max=price_min,
                        currency="USD",
                        image_url=img,
                        ticket_url=source_url,
                        is_featured=1,
                    )
                )

        return events

    def _extract_event_from_json_ld(self, item: dict[str, Any], source_url: str, source_tag: str) -> RawEvent | None:
        """Extract RawEvent from Schema.org item dict."""
        type_val = item.get("@type", "")
        if isinstance(type_val, list):
            type_str = " ".join(str(t) for t in type_val)
        else:
            type_str = str(type_val)

        valid_types = [
            "event", "touristattraction", "touristtrip", "tripplan",
            "product", "itempage", "localbusiness", "place"
        ]
        
        if not any(vt in type_str.lower() for vt in valid_types):
            return None

        title = item.get("name") or item.get("headline")
        if not title or not isinstance(title, str):
            return None

        title = re.sub(r'\s*\|\s*(Tripadvisor|Viator).*$', '', title, flags=re.IGNORECASE).strip()
        desc = item.get("description") or ""
        if isinstance(desc, dict):
            desc = desc.get("text", "")

        # Extract start time
        start_time = item.get("startDate") or item.get("validFrom")
        if not start_time or not isinstance(start_time, str):
            start_time = datetime.now(timezone.utc).isoformat()

        end_time = item.get("endDate")
        if end_time and not isinstance(end_time, str):
            end_time = None

        # Extract venue / location
        venue_name = "Experience Box Office"
        venue_city = None
        venue_state = None
        lat = None
        lon = None

        loc = item.get("location") or item.get("geo") or item.get("address")
        if isinstance(loc, dict):
            venue_name = loc.get("name") or venue_name
            addr = loc.get("address")
            if isinstance(addr, dict):
                venue_city = addr.get("addressLocality")
                venue_state = addr.get("addressRegion")
            geo = loc.get("geo") if isinstance(loc.get("geo"), dict) else loc
            if isinstance(geo, dict):
                try:
                    lat = float(geo.get("latitude")) if geo.get("latitude") else None
                    lon = float(geo.get("longitude")) if geo.get("longitude") else None
                except (ValueError, TypeError):
                    pass

        # Extract image
        image_url = None
        raw_img = item.get("image")
        if isinstance(raw_img, str):
            image_url = raw_img
        elif isinstance(raw_img, list) and len(raw_img) > 0:
            first = raw_img[0]
            image_url = first if isinstance(first, str) else first.get("url")
        elif isinstance(raw_img, dict):
            image_url = raw_img.get("url")

        # Extract pricing
        price_min = None
        price_max = None
        currency = "USD"
        offers = item.get("offers")
        if isinstance(offers, dict):
            currency = offers.get("priceCurrency", "USD")
            try:
                p = offers.get("price") or offers.get("lowPrice")
                if p is not None:
                    price_min = float(p)
                hp = offers.get("highPrice")
                if hp is not None:
                    price_max = float(hp)
            except (ValueError, TypeError):
                pass
        elif isinstance(offers, list) and len(offers) > 0:
            first_offer = offers[0]
            if isinstance(first_offer, dict):
                currency = first_offer.get("priceCurrency", "USD")
                try:
                    p = first_offer.get("price")
                    if p is not None:
                        price_min = float(p)
                except (ValueError, TypeError):
                    pass

        # Deterministic ID
        item_id = item.get("url") or item.get("@id") or f"{title}_{venue_name}"
        event_id = hashlib.md5(str(item_id).encode("utf-8")).hexdigest()[:12]
        ticket_url = item.get("url") or source_url

        return RawEvent(
            source=source_tag,
            source_event_id=f"wishlist_{event_id}",
            venue_name=venue_name,
            venue_address=None,
            venue_city=venue_city,
            venue_state=venue_state,
            venue_postal_code=None,
            venue_latitude=lat,
            venue_longitude=lon,
            title=title,
            description=desc,
            category=map_travel_category(title, desc),
            start_time=start_time,
            end_time=end_time,
            price_min=price_min,
            price_max=price_max or price_min,
            currency=currency,
            image_url=image_url,
            ticket_url=ticket_url,
            is_featured=1,
        )
