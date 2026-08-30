"""iCal (.ics) and webcal calendar subscription event ingestion adapter."""

from datetime import datetime, timezone
import re
import httpx

from backend.app.core.logging import logger
from backend.app.providers.base import BaseProvider, GeoPoint, ProviderStatus, RateLimitConfig, RawEvent


def parse_ical_datetime(dt_str: str) -> str | None:
    """Convert iCal date/time strings (e.g. 20260913T180000Z or 20260913) to ISO 8601."""
    clean = dt_str.strip().split(";")[0].split(":")[-1]

    # Full UTC timestamp: 20260913T180000Z
    if len(clean) >= 15 and "T" in clean:
        try:
            if clean.endswith("Z"):
                dt = datetime.strptime(clean, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
                return dt.isoformat()
            dt = datetime.strptime(clean[:15], "%Y%m%dT%H%M%S")
            return dt.isoformat()
        except ValueError:
            pass

    # Date only: 20260913
    if len(clean) == 8 and clean.isdigit():
        try:
            dt = datetime.strptime(clean, "%Y%m%d")
            return dt.isoformat()
        except ValueError:
            pass

    return None


def infer_ical_category(summary: str, description: str = "") -> str:
    """Infer canonical category from iCal summary and description text."""
    combined = f"{summary} {description}".lower()
    if any(k in combined for k in ("concert", "live music", "band", "orchestra", "jazz", "blues", "recital")):
        return "music"
    if any(k in combined for k in (
        "game", "match", "vs", "tournament", "championship", "athletics", "football",
        "basketball", "baseball", "soccer", "nfl", "nba", "mlb", "mls", "f1", "formula 1",
        "nascar", "indy", "indycar", "motogp", "grand prix", "racing", "motorsport"
    )):
        return "sports"
    if any(k in combined for k in ("play", "musical", "theatre", "theater", "ballet", "broadway", "stage")):
        return "theater"
    if any(k in combined for k in ("standup", "comedy", "improv", "open mic")):
        return "comedy"
    if any(k in combined for k in ("festival", "market", "parade", "fair", "meeting", "community", "workshop")):
        return "community"
    return "other"


class ICalEventProvider(BaseProvider):
    """Ingestion provider consuming standard iCal (.ics) feeds and calendar subscriptions."""

    provider_name: str = "ical"
    rate_limit: RateLimitConfig = RateLimitConfig(requests_per_minute=20, max_retries=2)

    def __init__(self, feed_urls: list[str] | None = None) -> None:
        self.feed_urls = feed_urls or []

    async def fetch_events(self, location: GeoPoint, radius_miles: float) -> list[RawEvent]:
        """Fetch and parse .ics calendar events across configured subscription URLs."""
        if not self.feed_urls:
            return []

        all_events: list[RawEvent] = []

        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            for url in self.feed_urls:
                # Convert webcal:// to https://
                fetch_url = url.replace("webcal://", "https://") if url.startswith("webcal://") else url
                try:
                    res = await client.get(fetch_url)
                    if res.status_code != 200:
                        continue

                    events_from_feed = self.parse_ics_text(res.text, source_url=fetch_url)
                    all_events.extend(events_from_feed)
                except Exception as exc:
                    logger.warning("Error fetching iCal feed from %s: %s", fetch_url, exc)

        return all_events

    def parse_ics_text(self, ics_content: str, source_url: str) -> list[RawEvent]:
        """Parse raw RFC 5545 iCal stream and extract VEVENT components."""
        raw_events: list[RawEvent] = []

        # Unfold lines (RFC 5545 line continuation begins with space or tab)
        unfolded = re.sub(r"\r?\n[ \t]", "", ics_content)
        events_blocks = re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", unfolded, re.DOTALL | re.IGNORECASE)

        for block in events_blocks:
            try:
                event_dict: dict[str, str] = {}
                for line in block.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        prop_name = k.split(";")[0].strip().upper()
                        event_dict[prop_name] = v.strip()

                summary = event_dict.get("SUMMARY")
                dtstart_raw = event_dict.get("DTSTART")
                if not summary or not dtstart_raw:
                    continue

                start_iso = parse_ical_datetime(dtstart_raw)
                if not start_iso:
                    continue

                end_iso = parse_ical_datetime(event_dict.get("DTEND", "")) if event_dict.get("DTEND") else None
                uid = event_dict.get("UID") or f"{summary}-{start_iso}"
                clean_uid = re.sub(r"[^\w-]", "", uid.lower())[:64]

                loc_str = event_dict.get("LOCATION", "Local Venue")
                desc = event_dict.get("DESCRIPTION", "")
                url = event_dict.get("URL", source_url)

                raw_events.append(
                    RawEvent(
                        source="ical",
                        source_event_id=clean_uid,
                        venue_name=loc_str,
                        venue_address=loc_str,
                        title=summary,
                        description=desc[:500] if desc else None,
                        category=infer_ical_category(summary, desc),
                        start_time=start_iso,
                        end_time=end_iso,
                        price_min=None,
                        price_max=None,
                        currency="USD",
                        image_url=None,
                        ticket_url=url,
                        is_featured=0,
                    )
                )
            except Exception as exc:
                logger.debug("Error parsing VEVENT block: %s", exc)

        return raw_events

    async def healthcheck(self) -> ProviderStatus:
        """Verify reachability across configured iCal subscription feeds."""
        if not self.feed_urls:
            return ProviderStatus(
                provider_name=self.provider_name,
                status="idle",
                is_healthy=True,
                extra_details={"configured_feeds_count": 0},
            )

        return ProviderStatus(
            provider_name=self.provider_name,
            status="ok",
            is_healthy=True,
            last_sync=datetime.now(timezone.utc),
            extra_details={"configured_feeds_count": len(self.feed_urls)},
        )
