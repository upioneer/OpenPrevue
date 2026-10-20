"""Mock event ingestion provider with realistic, calendar-anchored listings."""

from datetime import datetime, timedelta
from backend.app.core.timezone import resolve_app_timezone
from backend.app.providers.base import BaseProvider, GeoPoint, RawEvent


class MockEventProvider(BaseProvider):
    """Mock event provider generating realistic, calendar-anchored event listings dynamically matched to location."""

    provider_name: str = "mock"

    async def fetch_events(self, location: GeoPoint, radius_miles: float) -> list[RawEvent]:
        """Generate mock events anchored to explicit calendar dates in the declared timezone."""
        is_nyc = abs(location.latitude - 40.7128) < 1.0 and abs(location.longitude - (-74.0060)) < 1.0
        is_nola = abs(location.latitude - 29.9511) < 1.0 and abs(location.longitude - (-90.0715)) < 1.0

        tz = await resolve_app_timezone()
        today = datetime.now(tz).date()

        def cal_dt(day_offset: int, hour: int) -> tuple[str, datetime]:
            d = today + timedelta(days=day_offset)
            return d.isoformat(), datetime(d.year, d.month, d.day, hour, 0, tzinfo=tz)

        days_to_sunday = (6 - today.weekday()) % 7

        if is_nola:
            city = "New Orleans"
            state = "LA"
            postal = "70112"
            schedule = [
                # Today (day_offset = 0)
                ("Saenger Theatre", "1111 Canal St", 29.9548, -90.0722, "Wicked: Broadway Landmark Musical", "theater", 0, 14, 79.0, 245.0, 0, "https://www.saengernola.com/events"),
                ("Preservation Hall", "726 St Peter", 29.9584, -90.0655, "Preservation Hall Jazz All-Stars", "music", 0, 19, 30.0, 50.0, 0, "https://www.preservationhall.com"),
                ("The Fillmore New Orleans", "6 Canal St", 29.9502, -90.0638, "Khruangbin: A La Sala World Tour", "music", 0, 20, 65.0, 165.0, 1, "https://www.fillmorenola.com/events"),
                ("Tipitina's", "501 Napoleon Ave", 29.9182, -90.1011, "Galactic: Live Uptown Funk Showcase", "music", 0, 21, 35.0, 65.0, 1, "https://www.tipitinas.com"),
                # Tomorrow (day_offset = 1)
                ("Saenger Theatre", "1111 Canal St", 29.9548, -90.0722, "Wicked: Broadway Evening Performance", "theater", 1, 19, 79.0, 245.0, 0, "https://www.saengernola.com/events"),
                ("Preservation Hall", "726 St Peter", 29.9584, -90.0655, "Traditional Acoustic Brass Sessions", "music", 1, 19, 30.0, 50.0, 0, "https://www.preservationhall.com"),
                ("Joy Theater", "1200 Canal St", 29.9555, -90.0735, "French Quarter Comedy Showcase", "comedy", 1, 20, 25.0, 40.0, 0, "https://thejoytheater.com"),
                ("Tipitina's", "501 Napoleon Ave", 29.9182, -90.1011, "Rebirth Brass Band: Uptown Residency", "music", 1, 21, 30.0, 55.0, 1, "https://www.tipitinas.com"),
                # Day +2 (day_offset = 2)
                ("Joy Theater", "1200 Canal St", 29.9555, -90.0735, "Canal Street Late Night Standup", "comedy", 2, 20, 25.0, 40.0, 0, "https://thejoytheater.com"),
                ("The Fillmore New Orleans", "6 Canal St", 29.9502, -90.0638, "Trombone Shorty & Orleans Avenue", "music", 2, 20, 55.0, 145.0, 1, "https://www.fillmorenola.com/events"),
                # Upcoming Sunday NFL Anchor
                ("Caesars Superdome", "1500 Sugar Bowl Dr", 29.9511, -90.0812, "NFL: New Orleans Saints vs Atlanta Falcons", "sports", days_to_sunday, 12, 75.0, 420.0, 1, "https://www.neworleanssaints.com/tickets"),
            ]
        elif is_nyc:
            city = "New York"
            state = "NY"
            postal = "10001"
            schedule = [
                # Today (day_offset = 0)
                ("Gershwin Theatre", "222 W 51st St", 40.7624, -73.9851, "Wicked: Broadway Landmark Musical", "theater", 0, 14, 79.0, 245.0, 0, "https://wickedthemusical.com"),
                ("Blue Note Jazz Club", "131 W 3rd St", 40.7308, -74.0006, "Ron Carter Quintet: Greenwich Village Sets", "music", 0, 19, 30.0, 55.0, 0, "https://www.bluenotejazz.com/nyc"),
                ("Radio City Music Hall", "1260 6th Ave", 40.7599, -73.9799, "Khruangbin: A La Sala World Tour", "music", 0, 20, 65.0, 165.0, 1, "https://www.msg.com/radio-city-music-hall"),
                ("Brooklyn Steel", "319 Frost St", 40.7193, -73.9388, "Japanese Breakfast: Live in Williamsburg", "music", 0, 21, 35.0, 75.0, 1, "https://www.bowerypresents.com/brooklyn-steel"),
                # Tomorrow (day_offset = 1)
                ("Gershwin Theatre", "222 W 51st St", 40.7624, -73.9851, "Wicked: Broadway Evening Performance", "theater", 1, 19, 79.0, 245.0, 0, "https://wickedthemusical.com"),
                ("Beacon Theatre", "2124 Broadway", 40.7806, -73.9813, "Trey Anastasio: Solo Acoustic Residency", "music", 1, 20, 55.0, 140.0, 1, "https://www.msg.com/beacon-theatre"),
                ("Comedy Cellar", "117 MacDougal St", 40.7300, -74.0002, "MacDougal Street Standup Showcase", "comedy", 1, 20, 25.0, 35.0, 0, "https://www.comedycellar.com"),
                # Day +2 (day_offset = 2)
                ("Comedy Cellar", "117 MacDougal St", 40.7300, -74.0002, "Village Underground Late Night Showcase", "comedy", 2, 20, 25.0, 35.0, 0, "https://www.comedycellar.com"),
                # Upcoming Sunday NBA Anchor
                ("Madison Square Garden", "4 Pennsylvania Plaza", 40.7505, -73.9934, "NBA: New York Knicks vs Boston Celtics", "sports", days_to_sunday, 12, 85.0, 450.0, 1, "https://www.msg.com/madison-square-garden"),
            ]
        else:
            city = "Local Metro"
            state = "US"
            postal = "00000"
            lat = location.latitude
            lon = location.longitude
            schedule = [
                # Today (day_offset = 0)
                ("Civic Center Playhouse", "700 Civic Blvd", lat - 0.015, lon + 0.01, "Broadway Touring Musical", "theater", 0, 14, 65.0, 180.0, 0, "https://www.broadway.org"),
                ("Downtown Concert Hall", "500 Center Ave", lat + 0.015, lon - 0.01, "Symphony Orchestra Gala", "music", 0, 19, 40.0, 95.0, 1, "https://www.ticketmaster.com"),
                ("Grand City Theatre", "250 Main St", lat - 0.01, lon - 0.01, "Headliner Live Concert Tour", "music", 0, 20, 55.0, 150.0, 1, "https://www.ticketmaster.com"),
                # Tomorrow (day_offset = 1)
                ("Civic Center Playhouse", "700 Civic Blvd", lat - 0.015, lon + 0.01, "Broadway Touring Evening Show", "theater", 1, 19, 65.0, 180.0, 0, "https://www.broadway.org"),
                ("The Underground Club", "42 Arts District", lat + 0.005, lon - 0.005, "Standup Comedy Headliners", "comedy", 1, 20, 25.0, 45.0, 0, "https://www.ticketmaster.com"),
                ("Grand City Theatre", "250 Main St", lat - 0.01, lon - 0.01, "Indie Rock Showcase", "music", 1, 20, 45.0, 110.0, 1, "https://www.ticketmaster.com"),
                # Day +2 (day_offset = 2)
                ("The Underground Club", "42 Arts District", lat + 0.005, lon - 0.005, "Late Night Improv & Standup", "comedy", 2, 20, 25.0, 45.0, 0, "https://www.ticketmaster.com"),
                # Upcoming Sunday Sports Anchor
                ("Metro Arena", "100 Arena Way", lat + 0.01, lon + 0.01, "Pro Basketball: Home Showdown", "sports", days_to_sunday, 12, 45.0, 250.0, 1, "https://www.nba.com/tickets"),
            ]

        mock_raw_data: list[RawEvent] = []
        for v_name, v_addr, v_lat, v_lon, title, cat, day_off, hour, p_min, p_max, is_feat, t_url in schedule:
            date_key, st_time = cal_dt(day_off, hour)
            venue_slug = v_name.lower().replace("'", "").replace(" ", "-")
            mock_raw_data.append(
                RawEvent(
                    source="mock",
                    source_event_id=f"mock-{venue_slug}-{date_key}",
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
                    ticket_url=t_url or "https://openprevue.com",
                    is_featured=is_feat,
                )
            )

        return mock_raw_data
