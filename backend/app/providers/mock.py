"""Mock event ingestion provider with realistic, dynamically location-anchored listings."""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from backend.app.providers.base import BaseProvider, GeoPoint, RawEvent


class MockEventProvider(BaseProvider):
    """Mock event provider generating realistic, time-anchored event listings dynamically matched to location."""

    provider_name: str = "mock"

    async def fetch_events(self, location: GeoPoint, radius_miles: float) -> list[RawEvent]:
        """Generate mock events relative to current timestamp and target coordinates."""
        tz = ZoneInfo("America/New_York")
        now = datetime.now(timezone.utc)
        today = now.date()

        # Build dates relative to today
        t_today_2pm = datetime(today.year, today.month, today.day, 14, 0, tzinfo=tz)
        t_today_7pm = datetime(today.year, today.month, today.day, 19, 0, tzinfo=tz)
        t_today_8pm = datetime(today.year, today.month, today.day, 20, 0, tzinfo=tz)
        t_today_9pm = datetime(today.year, today.month, today.day, 21, 0, tzinfo=tz)

        d_tomorrow = today + timedelta(days=1)
        t_tom_8pm = datetime(d_tomorrow.year, d_tomorrow.month, d_tomorrow.day, 20, 0, tzinfo=tz)

        d_in2days = today + timedelta(days=2)
        t_in2_8pm = datetime(d_in2days.year, d_in2days.month, d_in2days.day, 20, 0, tzinfo=tz)

        d_sunday = today + timedelta(days=(6 - today.weekday()) % 7)
        if d_sunday == today:
            d_sunday = today + timedelta(days=7)
        t_sun_12pm = datetime(d_sunday.year, d_sunday.month, d_sunday.day, 12, 0, tzinfo=tz)

        # Determine if target coordinates match New York City or another metro
        is_nyc = abs(location.latitude - 40.7128) < 1.0 and abs(location.longitude - (-74.0060)) < 1.0
        is_nola = abs(location.latitude - 29.9511) < 1.0 and abs(location.longitude - (-90.0715)) < 1.0

        if is_nola:
            city = "New Orleans"
            state = "LA"
            postal = "70112"
            venues = [
                ("Caesars Superdome", "1500 Sugar Bowl Dr", 29.9511, -90.0812, "NFL: New Orleans Saints vs Atlanta Falcons", "sports", t_sun_12pm, 75.0, 420.0, 1),
                ("The Fillmore New Orleans", "6 Canal St", 29.9502, -90.0638, "Khruangbin: A La Sala World Tour", "music", t_today_8pm, 65.0, 165.0, 1),
                ("Tipitina's", "501 Napoleon Ave", 29.9182, -90.1011, "Galactic: Live Uptown Funk Showcase", "music", t_today_9pm, 35.0, 65.0, 1),
                ("Saenger Theatre", "1111 Canal St", 29.9548, -90.0722, "Wicked: Broadway Landmark Musical", "theater", t_today_2pm, 79.0, 245.0, 0),
                ("Preservation Hall", "726 St Peter", 29.9584, -90.0655, "Preservation Hall Jazz All-Stars", "music", t_today_7pm, 30.0, 50.0, 0),
                ("Joy Theater", "1200 Canal St", 29.9555, -90.0735, "French Quarter Comedy Showcase", "comedy", t_in2_8pm, 25.0, 40.0, 0),
            ]
        elif is_nyc:
            city = "New York"
            state = "NY"
            postal = "10001"
            venues = [
                ("Madison Square Garden", "4 Pennsylvania Plaza", 40.7505, -73.9934, "NBA: New York Knicks vs Boston Celtics", "sports", t_sun_12pm, 85.0, 450.0, 1),
                ("Radio City Music Hall", "1260 6th Ave", 40.7599, -73.9799, "Khruangbin: A La Sala World Tour", "music", t_today_8pm, 65.0, 165.0, 1),
                ("Brooklyn Steel", "319 Frost St", 40.7193, -73.9388, "Japanese Breakfast: Live in Williamsburg", "music", t_today_9pm, 35.0, 75.0, 1),
                ("Beacon Theatre", "2124 Broadway", 40.7806, -73.9813, "Trey Anastasio: Solo Acoustic Residency", "music", t_tom_8pm, 55.0, 140.0, 0),
                ("Gershwin Theatre", "222 W 51st St", 40.7624, -73.9851, "Wicked: Broadway Landmark Musical", "theater", t_today_2pm, 79.0, 245.0, 0),
                ("Blue Note Jazz Club", "131 W 3rd St", 40.7308, -74.0006, "Ron Carter Quintet: Greenwich Village Sets", "music", t_today_7pm, 30.0, 55.0, 0),
                ("Comedy Cellar", "117 MacDougal St", 40.7300, -74.0002, "MacDougal Street Standup Showcase", "comedy", t_in2_8pm, 25.0, 35.0, 0),
            ]
        else:
            # Generic local anchoring around target lat/lon
            city = "Local Metro"
            state = "US"
            postal = "00000"
            lat = location.latitude
            lon = location.longitude
            venues = [
                ("Metro Arena", "100 Arena Way", lat + 0.01, lon + 0.01, "Pro Basketball: Home Showdown", "sports", t_sun_12pm, 45.0, 250.0, 1),
                ("Grand City Theatre", "250 Main St", lat - 0.01, lon - 0.01, "Headliner Live Concert Tour", "music", t_today_8pm, 55.0, 150.0, 1),
                ("Downtown Concert Hall", "500 Center Ave", lat + 0.015, lon - 0.01, "Symphony Orchestra Gala", "music", t_today_7pm, 40.0, 95.0, 1),
                ("Civic Center Playhouse", "700 Civic Blvd", lat - 0.015, lon + 0.01, "Broadway Touring Musical", "theater", t_today_2pm, 65.0, 180.0, 0),
                ("The Underground Club", "42 Arts District", lat + 0.005, lon - 0.005, "Standup Comedy Headliners", "comedy", t_in2_8pm, 25.0, 45.0, 0),
            ]

        mock_raw_data: list[RawEvent] = []
        for v_name, v_addr, v_lat, v_lon, title, cat, st_time, p_min, p_max, is_feat in venues:
            mock_raw_data.append(
                RawEvent(
                    source="mock",
                    source_event_id=f"mock-{v_name.lower().replace(' ', '-')}",
                    venue_name=v_name,
                    venue_address=v_addr,
                    venue_city=city,
                    venue_state=state,
                    venue_postal_code=postal,
                    venue_latitude=v_lat,
                    venue_longitude=v_lon,
                    title=title,
                    description=f"Live local performance and showcase at {v_name}.",
                    category=cat,
                    start_time=st_time.isoformat(),
                    end_time=(st_time + timedelta(hours=3)).isoformat(),
                    price_min=p_min,
                    price_max=p_max,
                    currency="USD",
                    ticket_url="https://openprevue.tv",
                    is_featured=is_feat,
                )
            )

        return mock_raw_data
