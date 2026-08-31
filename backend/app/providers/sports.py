"""Motorsport and major sports league event provider (Formula 1, NASCAR, IndyCar, MotoGP, NFL, NBA, MLB, MLS)."""

from datetime import datetime, timedelta, timezone
from backend.app.core.logging import logger
from backend.app.providers.base import BaseProvider, GeoPoint, RawEvent
from backend.app.services.ingestion import calculate_haversine_distance


class SportsLeagueProvider(BaseProvider):
    """Aggregates schedule feeds from major motorsport and professional sports leagues."""

    provider_name: str = "sports_leagues"

    async def fetch_events(self, location: GeoPoint, radius_miles: float) -> list[RawEvent]:
        """Fetch sports events filtered by radial geographic proximity or national broadcast status."""
        events: list[RawEvent] = []
        now = datetime.now(timezone.utc)

        # Motorsport & League Calendar Database
        fixtures = [
            # National Motorsport Broadcasts
            {
                "id": "f1-cota-usgp",
                "title": "FORMULA 1 UNITED STATES GRAND PRIX",
                "league": "Formula 1",
                "venue_name": "Circuit of the Americas",
                "address": "9201 Circuit of The Americas Blvd",
                "city": "Austin",
                "state": "TX",
                "postal": "78617",
                "lat": 30.1346,
                "lon": -97.6359,
                "days_offset": 5,
                "hour": 14,
                "price_min": 175.0,
                "price_max": 850.0,
                "url": "https://www.formula1.com/en/racing/2026/United_States.html",
                "desc": "Official Formula 1 World Championship Sunday Grand Prix race session.",
                "is_national": True,
            },
            {
                "id": "nascar-talladega-500",
                "title": "NASCAR CUP SERIES: GEICO 500",
                "league": "NASCAR",
                "venue_name": "Talladega Superspeedway",
                "address": "3366 Speedway Blvd",
                "city": "Lincoln",
                "state": "AL",
                "postal": "35096",
                "lat": 33.5670,
                "lon": -86.0660,
                "days_offset": 6,
                "hour": 13,
                "price_min": 65.0,
                "price_max": 240.0,
                "url": "https://www.nascar.com/schedule",
                "desc": "High banks superspeedway pack racing in the NASCAR Cup Series.",
                "is_national": True,
            },
            {
                "id": "indycar-barber-gp",
                "title": "INDYCAR: CHILDREN'S OF ALABAMA INDY GRAND PRIX",
                "league": "IndyCar",
                "venue_name": "Barber Motorsports Park",
                "address": "6040 Barber Motorsports Pkwy",
                "city": "Birmingham",
                "state": "AL",
                "postal": "35004",
                "lat": 33.5319,
                "lon": -86.6192,
                "days_offset": 14,
                "hour": 12,
                "price_min": 55.0,
                "price_max": 180.0,
                "url": "https://www.indycar.com/Schedule",
                "desc": "NTT INDYCAR SERIES natural road course championship race.",
                "is_national": True,
            },
            {
                "id": "motogp-americas-gp",
                "title": "MOTOGP: GRAND PRIX OF THE AMERICAS",
                "league": "MotoGP",
                "venue_name": "Circuit of the Americas",
                "address": "9201 Circuit of The Americas Blvd",
                "city": "Austin",
                "state": "TX",
                "postal": "78617",
                "lat": 30.1346,
                "lon": -97.6359,
                "days_offset": 19,
                "hour": 14,
                "price_min": 89.0,
                "price_max": 350.0,
                "url": "https://www.motogp.com/en/calendar",
                "desc": "FIM MotoGP World Championship premier class motorcycle racing.",
                "is_national": True,
            },
            # New Orleans Regional Sports
            {
                "id": "nfl-saints-vs-falcons",
                "title": "NFL: NEW ORLEANS SAINTS VS ATLANTA FALCONS",
                "league": "NFL",
                "venue_name": "Caesars Superdome",
                "address": "1500 Sugar Bowl Dr",
                "city": "New Orleans",
                "state": "LA",
                "postal": "70112",
                "lat": 29.9511,
                "lon": -90.0812,
                "days_offset": 1,
                "hour": 12,
                "price_min": 78.0,
                "price_max": 420.0,
                "url": "https://www.neworleanssaints.com/schedule",
                "desc": "NFC South rivalry matchup live under the dome.",
                "is_national": False,
            },
            {
                "id": "nba-pelicans-vs-lakers",
                "title": "NBA: NEW ORLEANS PELICANS VS LOS ANGELES LAKERS",
                "league": "NBA",
                "venue_name": "Smoothie King Center",
                "address": "1501 Dave Dixon Dr",
                "city": "New Orleans",
                "state": "LA",
                "postal": "70113",
                "lat": 29.9490,
                "lon": -90.0821,
                "days_offset": 2,
                "hour": 19,
                "price_min": 45.0,
                "price_max": 380.0,
                "url": "https://www.nba.com/pelicans/schedule",
                "desc": "Western Conference showdown at the Smoothie King Center.",
                "is_national": False,
            },
            # New York Regional Sports
            {
                "id": "nba-knicks-vs-celtics",
                "title": "NBA: NEW YORK KNICKS VS BOSTON CELTICS",
                "league": "NBA",
                "venue_name": "Madison Square Garden",
                "address": "4 Pennsylvania Plaza",
                "city": "New York",
                "state": "NY",
                "postal": "10001",
                "lat": 40.7505,
                "lon": -73.9934,
                "days_offset": 1,
                "hour": 19,
                "price_min": 95.0,
                "price_max": 480.0,
                "url": "https://www.nba.com/knicks/schedule",
                "desc": "Eastern Conference rivalry matchup at MSG.",
                "is_national": False,
            },
            {
                "id": "nba-nets-vs-heat",
                "title": "NBA: BROOKLYN NETS VS MIAMI HEAT",
                "league": "NBA",
                "venue_name": "Barclays Center",
                "address": "620 Atlantic Ave",
                "city": "Brooklyn",
                "state": "NY",
                "postal": "11217",
                "lat": 40.6826,
                "lon": -73.9754,
                "days_offset": 3,
                "hour": 19,
                "price_min": 45.0,
                "price_max": 320.0,
                "url": "https://www.nba.com/nets/schedule",
                "desc": "Atlantic Division basketball matchup in Brooklyn.",
                "is_national": False,
            },
            # Houston Regional Sports
            {
                "id": "mlb-astros-vs-rangers",
                "title": "MLB: HOUSTON ASTROS VS TEXAS RANGERS",
                "league": "MLB",
                "venue_name": "Daikin Park",
                "address": "501 Crawford St",
                "city": "Houston",
                "state": "TX",
                "postal": "77002",
                "lat": 29.7573,
                "lon": -95.3555,
                "days_offset": 4,
                "hour": 18,
                "price_min": 24.0,
                "price_max": 210.0,
                "url": "https://www.mlb.com/astros/schedule",
                "desc": "Lone Star Series rivalry baseball game.",
                "is_national": True,
            },
            {
                "id": "mls-houston-dynamo-vs-austin",
                "title": "MLS: HOUSTON DYNAMO FC VS AUSTIN FC",
                "league": "MLS",
                "venue_name": "Shell Energy Stadium",
                "address": "2200 Texas Ave",
                "city": "Houston",
                "state": "TX",
                "postal": "77003",
                "lat": 29.7522,
                "lon": -95.3524,
                "days_offset": 3,
                "hour": 19,
                "price_min": 30.0,
                "price_max": 160.0,
                "url": "https://www.houstondynamofc.com/schedule",
                "desc": "Major League Soccer regular season fixture.",
                "is_national": True,
            },
        ]

        for fix in fixtures:
            dist = calculate_haversine_distance(location.latitude, location.longitude, fix["lat"], fix["lon"])
            # Include if within radius or national broadcast or broad query
            if dist > radius_miles and not fix.get("is_national") and radius_miles < 500:
                continue

            event_date = now + timedelta(days=fix["days_offset"])
            event_dt = event_date.replace(hour=fix["hour"], minute=0, second=0, microsecond=0)
            iso_start = event_dt.isoformat()
            iso_end = (event_dt + timedelta(hours=3)).isoformat()

            raw_event = RawEvent(
                source="sports_leagues",
                source_event_id=fix["id"],
                venue_name=fix["venue_name"],
                venue_address=fix["address"],
                venue_city=fix["city"],
                venue_state=fix["state"],
                venue_postal_code=fix["postal"],
                venue_latitude=fix["lat"],
                venue_longitude=fix["lon"],
                title=fix["title"],
                description=fix["desc"],
                category="sports",
                start_time=iso_start,
                end_time=iso_end,
                price_min=fix["price_min"],
                price_max=fix["price_max"],
                currency="USD",
                ticket_url=fix["url"],
                is_featured=1 if fix["league"] in ["NFL", "Formula 1", "NBA"] else 0,
            )
            events.append(raw_event)

        logger.info("SportsLeagueProvider loaded %d fixtures for location (%.4f, %.4f).", len(events), location.latitude, location.longitude)
        return events
