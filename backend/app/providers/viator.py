"""Native Viator Partner / Merchant API ingestion adapter."""

from datetime import datetime, timezone
from typing import Any
import httpx

from backend.app.core.logging import logger
from backend.app.providers.base import BaseProvider, GeoPoint, ProviderStatus, RateLimitConfig, RawEvent
from backend.app.providers.travel_wishlist import map_travel_category


class ViatorPartnerProvider(BaseProvider):
    """Ingestion provider connecting to the official Viator Partner API v2.0."""

    provider_name: str = "viator"
    rate_limit: RateLimitConfig = RateLimitConfig(requests_per_minute=60, max_retries=3)

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = (api_key or "").strip()
        self.base_url = "https://api.viator.com/partner"

    async def fetch_events(self, location: GeoPoint, radius_miles: float) -> list[RawEvent]:
        """Fetch top-rated local tours, experiences, and activities from Viator Partner API."""
        if not self.api_key:
            logger.info("Viator API key not configured, skipping native API query.")
            return []

        headers = {
            "Accept": "application/json;version=2.0",
            "Content-Type": "application/json",
            "exp-api-key": self.api_key,
            "User-Agent": "OpenPrevue-Headend/0.16.1",
        }

        # Search products near destination coordinates
        payload = {
            "filtering": {
                "destination": f"{location.latitude},{location.longitude}",
            },
            "pagination": {
                "start": 1,
                "count": 25,
            },
            "currency": "USD",
        }

        async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
            try:
                res = await client.post(f"{self.base_url}/products/search", json=payload)
                if res.status_code == 401 or res.status_code == 403:
                    logger.warning("Viator API authentication failed (HTTP %d). Check API key.", res.status_code)
                    return []
                if res.status_code != 200:
                    logger.warning("Viator API search returned HTTP %d: %s", res.status_code, res.text[:200])
                    return []

                data = res.json()
                products = data.get("products", [])
                return self._parse_products(products, location)
            except Exception as exc:
                logger.error("Error querying Viator Partner API: %s", exc)
                return []

    def _parse_products(self, products: list[dict[str, Any]], location: GeoPoint) -> list[RawEvent]:
        """Convert Viator API product search results to canonical RawEvent items."""
        events: list[RawEvent] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for item in products:
            try:
                product_code = item.get("productCode") or str(item.get("id", ""))
                title = item.get("title")
                if not product_code or not title:
                    continue

                desc = item.get("description") or ""
                ticket_url = item.get("productUrl") or f"https://www.viator.com/tours/{product_code}"

                # Pricing extraction
                pricing = item.get("pricing", {})
                summary = pricing.get("summary", {})
                from_price = summary.get("fromPrice")
                try:
                    price_min = float(from_price) if from_price is not None else None
                except (ValueError, TypeError):
                    price_min = None

                # Image extraction
                image_url = None
                images = item.get("images", [])
                if images and isinstance(images, list):
                    first_img = images[0]
                    variants = first_img.get("variants", [])
                    if variants and isinstance(variants, list):
                        # Pick highest resolution variant
                        image_url = variants[-1].get("url")
                    else:
                        image_url = first_img.get("url")

                events.append(
                    RawEvent(
                        source="viator",
                        source_event_id=f"viator_{product_code}",
                        venue_name="Viator Local Experience",
                        venue_address=None,
                        venue_city=None,
                        venue_state=None,
                        venue_postal_code=None,
                        venue_latitude=location.latitude,
                        venue_longitude=location.longitude,
                        title=title,
                        description=desc,
                        category=map_travel_category(title, desc),
                        start_time=now_iso,
                        end_time=None,
                        price_min=price_min,
                        price_max=price_min,
                        currency=pricing.get("currency", "USD"),
                        image_url=image_url,
                        ticket_url=ticket_url,
                        is_featured=1,
                    )
                )
            except Exception as exc:
                logger.debug("Failed parsing individual Viator product: %s", exc)

        return events
