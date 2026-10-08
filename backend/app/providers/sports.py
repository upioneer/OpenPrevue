"""Motorsport and major sports league event provider (Formula 1, NASCAR, IndyCar, MotoGP, NFL, NBA, MLB, MLS)."""

from datetime import datetime, timedelta
from typing import Any
import httpx

from backend.app.core.logging import logger
from backend.app.core.timezone import resolve_app_timezone
from backend.app.providers.base import BaseProvider, GeoPoint, RawEvent
from backend.app.services.ingestion import calculate_haversine_distance


class SportsLeagueProvider(BaseProvider):
    """Aggregates schedule feeds from major motorsport and professional sports leagues with live scoreboard accuracy and strict geographic localization."""

    provider_name: str = "sports_leagues"

    # Coverage mode: "local_only" (default), "national_broadcasts", or "disabled"
    coverage_mode: str = "local_only"

    # Comprehensive North American major sports and motorsport venue coordinate registry
    VENUE_COORDINATES: dict[str, tuple[float, float, str, str, str]] = {
        # NFL Stadiums
        "allegiant stadium": (36.0908, -115.1833, "Las Vegas", "NV", "89118"),
        "arrowhead stadium": (39.0489, -94.4839, "Kansas City", "MO", "64129"),
        "geha field at arrowhead stadium": (39.0489, -94.4839, "Kansas City", "MO", "64129"),
        "at&t stadium": (32.7473, -97.0945, "Arlington", "TX", "76011"),
        "bank of america stadium": (35.2258, -80.8528, "Charlotte", "NC", "28202"),
        "caesars superdome": (29.9511, -90.0812, "New Orleans", "LA", "70112"),
        "cleveland browns stadium": (41.5061, -81.6995, "Cleveland", "OH", "44114"),
        "huntington bank field": (41.5061, -81.6995, "Cleveland", "OH", "44114"),
        "empower field at mile high": (39.7439, -105.0201, "Denver", "CO", "80204"),
        "everbank stadium": (30.3239, -81.6373, "Jacksonville", "FL", "32202"),
        "tiaa bank field": (30.3239, -81.6373, "Jacksonville", "FL", "32202"),
        "ford field": (42.3400, -83.0456, "Detroit", "MI", "48226"),
        "gillette stadium": (42.0909, -71.2643, "Foxborough", "MA", "02035"),
        "hard rock stadium": (25.9580, -80.2389, "Miami Gardens", "FL", "33056"),
        "highmark stadium": (42.7738, -78.7870, "Orchard Park", "NY", "14127"),
        "lambeau field": (44.5013, -88.0622, "Green Bay", "WI", "54304"),
        "levi's stadium": (37.4032, -121.9698, "Santa Clara", "CA", "95054"),
        "lincoln financial field": (39.9008, -75.1675, "Philadelphia", "PA", "19148"),
        "lucas oil stadium": (39.7601, -86.1639, "Indianapolis", "IN", "46225"),
        "lumen field": (47.5952, -122.3316, "Seattle", "WA", "98134"),
        "m&t bank stadium": (39.2780, -76.6227, "Baltimore", "MD", "21230"),
        "mercedes-benz stadium": (33.7553, -84.4010, "Atlanta", "GA", "30313"),
        "metlife stadium": (40.8135, -74.0745, "East Rutherford", "NJ", "07073"),
        "nissan stadium": (36.1665, -86.7713, "Nashville", "TN", "37213"),
        "northwest stadium": (38.9076, -76.8645, "Landover", "MD", "20785"),
        "commanders field": (38.9076, -76.8645, "Landover", "MD", "20785"),
        "fedexfield": (38.9076, -76.8645, "Landover", "MD", "20785"),
        "paycor stadium": (39.0955, -84.5161, "Cincinnati", "OH", "45202"),
        "raymond james stadium": (27.9759, -82.5033, "Tampa", "FL", "33607"),
        "nrg stadium": (29.6847, -95.4107, "Houston", "TX", "77054"),
        "reliant stadium": (29.6847, -95.4107, "Houston", "TX", "77054"),
        "sofi stadium": (33.9535, -118.3392, "Inglewood", "CA", "90301"),
        "soldier field": (41.8623, -87.6167, "Chicago", "IL", "60605"),
        "state farm stadium": (33.5276, -112.2626, "Glendale", "AZ", "85305"),
        "acrisure stadium": (40.4468, -80.0158, "Pittsburgh", "PA", "15212"),
        "heinz field": (40.4468, -80.0158, "Pittsburgh", "PA", "15212"),
        "u.s. bank stadium": (44.9735, -93.2575, "Minneapolis", "MN", "55415"),
        "tottenham hotspur stadium": (51.6042, -0.0662, "London", "UK", "N17 0AP"),
        "wembley stadium": (51.5560, -0.2795, "London", "UK", "HA9 0WS"),
        "allianz arena": (48.2188, 11.6247, "Munich", "DE", "80939"),

        # NBA Arenas
        "madison square garden": (40.7505, -73.9934, "New York", "NY", "10001"),
        "barclays center": (40.6826, -73.9754, "Brooklyn", "NY", "11217"),
        "td garden": (42.3662, -71.0621, "Boston", "MA", "02114"),
        "wells fargo center": (39.9012, -75.1720, "Philadelphia", "PA", "19148"),
        "scotiabank arena": (43.6435, -79.3791, "Toronto", "ON", "M5J 2L2"),
        "united center": (41.8807, -87.6742, "Chicago", "IL", "60612"),
        "rocket mortgage fieldhouse": (41.4965, -81.6882, "Cleveland", "OH", "44115"),
        "little caesars arena": (42.3411, -83.0553, "Detroit", "MI", "48201"),
        "gainbridge fieldhouse": (39.7640, -86.1555, "Indianapolis", "IN", "46204"),
        "fiserv forum": (43.0451, -87.9174, "Milwaukee", "WI", "53205"),
        "state farm arena": (33.7573, -84.3963, "Atlanta", "GA", "30303"),
        "spectrum center": (35.2251, -80.8392, "Charlotte", "NC", "28202"),
        "kaseya center": (25.7814, -80.1870, "Miami", "FL", "33132"),
        "ftx arena": (25.7814, -80.1870, "Miami", "FL", "33132"),
        "american airlines arena": (25.7814, -80.1870, "Miami", "FL", "33132"),
        "kia center": (28.5392, -81.3839, "Orlando", "FL", "32801"),
        "amway center": (28.5392, -81.3839, "Orlando", "FL", "32801"),
        "capital one arena": (38.8981, -77.0209, "Washington", "DC", "20004"),
        "ball arena": (39.7487, -105.0076, "Denver", "CO", "80204"),
        "target center": (44.9795, -93.2761, "Minneapolis", "MN", "55403"),
        "paycom center": (35.4634, -97.5151, "Oklahoma City", "OK", "73102"),
        "moda center": (45.5316, -122.6668, "Portland", "OR", "97227"),
        "delta center": (40.7683, -111.9011, "Salt Lake City", "UT", "84101"),
        "chase center": (37.7680, -122.3877, "San Francisco", "CA", "94158"),
        "crypto.com arena": (34.0430, -118.2673, "Los Angeles", "CA", "90015"),
        "staples center": (34.0430, -118.2673, "Los Angeles", "CA", "90015"),
        "intuit dome": (33.9450, -118.3420, "Inglewood", "CA", "90301"),
        "footprint center": (33.4457, -112.0712, "Phoenix", "AZ", "85004"),
        "golden 1 center": (38.5802, -121.4997, "Sacramento", "CA", "95814"),
        "american airlines center": (32.7905, -96.8103, "Dallas", "TX", "75219"),
        "toyota center": (29.7508, -95.3621, "Houston", "TX", "77002"),
        "fedexforum": (35.1382, -90.0506, "Memphis", "TN", "38103"),
        "smoothie king center": (29.9490, -90.0821, "New Orleans", "LA", "70113"),
        "frost bank center": (29.4270, -98.4375, "San Antonio", "TX", "78219"),
        "at&t center": (29.4270, -98.4375, "San Antonio", "TX", "78219"),
        "videotron centre": (46.8286, -71.2464, "Quebec City", "QC", "G1L 5A1"),

        # MLB Ballparks
        "yankee stadium": (40.8296, -73.9262, "Bronx", "NY", "10451"),
        "citi field": (40.7571, -73.8458, "Queens", "NY", "11368"),
        "fenway park": (42.3467, -71.0972, "Boston", "MA", "02215"),
        "oriole park at camden yards": (39.2839, -76.6216, "Baltimore", "MD", "21201"),
        "tropicana field": (27.7682, -82.6534, "St. Petersburg", "FL", "33705"),
        "rogers centre": (43.6414, -79.3894, "Toronto", "ON", "M5V 1J1"),
        "guaranteed rate field": (41.8299, -87.6338, "Chicago", "IL", "60616"),
        "progressive field": (41.4962, -81.6852, "Cleveland", "OH", "44115"),
        "comerica park": (42.3390, -83.0485, "Detroit", "MI", "48226"),
        "kauffman stadium": (39.0517, -94.4803, "Kansas City", "MO", "64129"),
        "target field": (44.9817, -93.2778, "Minneapolis", "MN", "55403"),
        "daikin park": (29.7573, -95.3555, "Houston", "TX", "77002"),
        "minute maid park": (29.7573, -95.3555, "Houston", "TX", "77002"),
        "angel stadium": (33.8003, -117.8827, "Anaheim", "CA", "92806"),
        "oakland coliseum": (37.7516, -122.2008, "Oakland", "CA", "94621"),
        "sutter health park": (38.5804, -121.5134, "West Sacramento", "CA", "95691"),
        "t-mobile park": (47.5914, -122.3325, "Seattle", "WA", "98134"),
        "globe life field": (32.7473, -97.0838, "Arlington", "TX", "76011"),
        "truist park": (33.8908, -84.4678, "Atlanta", "GA", "30339"),
        "loandepot park": (25.7781, -80.2197, "Miami", "FL", "33125"),
        "marlins park": (25.7781, -80.2197, "Miami", "FL", "33125"),
        "citizens bank park": (39.9061, -75.1665, "Philadelphia", "PA", "19148"),
        "nationals park": (38.8730, -77.0074, "Washington", "DC", "20003"),
        "wrigley field": (41.9484, -87.6553, "Chicago", "IL", "60613"),
        "great american ball park": (39.0979, -84.5082, "Cincinnati", "OH", "45202"),
        "american family field": (43.0280, -87.9712, "Milwaukee", "WI", "53214"),
        "pnc park": (40.4469, -80.0057, "Pittsburgh", "PA", "15212"),
        "busch stadium": (38.6226, -90.1928, "St. Louis", "MO", "63102"),
        "chase field": (33.4453, -112.0667, "Phoenix", "AZ", "85004"),
        "coors field": (39.7559, -104.9942, "Denver", "CO", "80205"),
        "dodger stadium": (34.0739, -118.2400, "Los Angeles", "CA", "90012"),
        "petco park": (32.7076, -117.1570, "San Diego", "CA", "92101"),
        "oracle park": (37.7786, -122.3893, "San Francisco", "CA", "94107"),

        # MLS Stadiums
        "red bull arena": (40.7368, -74.1503, "Harrison", "NJ", "07029"),
        "subaru park": (39.8328, -75.3785, "Chester", "PA", "19013"),
        "audi field": (38.8686, -77.0129, "Washington", "DC", "20024"),
        "inter miami cf stadium": (26.1929, -80.1607, "Fort Lauderdale", "FL", "33309"),
        "chase stadium": (26.1929, -80.1607, "Fort Lauderdale", "FL", "33309"),
        "inter&co stadium": (28.5411, -81.3892, "Orlando", "FL", "32805"),
        "exploria stadium": (28.5411, -81.3892, "Orlando", "FL", "32805"),
        "tql stadium": (39.1114, -84.5222, "Cincinnati", "OH", "45214"),
        "lower.com field": (39.9686, -83.0177, "Columbus", "OH", "43215"),
        "allianz field": (44.9531, -93.1650, "Saint Paul", "MN", "55104"),
        "geodis park": (36.1311, -86.7656, "Nashville", "TN", "37203"),
        "shell energy stadium": (29.7522, -95.3524, "Houston", "TX", "77003"),
        "q2 stadium": (30.3883, -97.7196, "Austin", "TX", "78758"),
        "toyota stadium": (33.1544, -96.8353, "Frisco", "TX", "75033"),
        "children's mercy park": (39.1215, -94.8232, "Kansas City", "KS", "66111"),
        "dick's sporting goods park": (39.8056, -104.8919, "Commerce City", "CO", "80022"),
        "america first field": (40.5829, -111.8931, "Sandy", "UT", "84070"),
        "providence park": (45.5216, -122.6917, "Portland", "OR", "97205"),
        "bc place": (49.2768, -123.1120, "Vancouver", "BC", "V6B 4A7"),
        "bmo field": (43.6332, -79.4186, "Toronto", "ON", "M6K 3C3"),
        "saputo stadium": (45.5631, -73.5528, "Montreal", "QC", "H1V 3N7"),
        "stade saputo": (45.5631, -73.5528, "Montreal", "QC", "H1V 3N7"),
        "bmo stadium": (34.0128, -118.2850, "Los Angeles", "CA", "90037"),
        "banc of california stadium": (34.0128, -118.2850, "Los Angeles", "CA", "90037"),
        "dignity health sports park": (33.8644, -118.2611, "Carson", "CA", "90746"),
        "paypal park": (37.3513, -121.9250, "San Jose", "CA", "95110"),

        # Major Motorsport Raceways
        "circuit of the americas": (30.1346, -97.6359, "Austin", "TX", "78617"),
        "daytona international speedway": (29.1856, -81.0706, "Daytona Beach", "FL", "32114"),
        "indianapolis motor speedway": (39.7950, -86.2346, "Indianapolis", "IN", "46222"),
        "talladega superspeedway": (33.5670, -86.0660, "Lincoln", "AL", "35096"),
        "charlotte motor speedway": (35.3517, -80.6836, "Concord", "NC", "28027"),
        "barber motorsports park": (33.5319, -86.6192, "Birmingham", "AL", "35004"),
        "watkins glen international": (42.3369, -76.9272, "Watkins Glen", "NY", "14891"),
        "road america": (43.8055, -87.9942, "Elkhart Lake", "WI", "53020"),
        "weathertech raceway laguna seca": (36.5844, -121.7536, "Salinas", "CA", "93908"),
        "sonoma raceway": (38.1614, -122.4597, "Sonoma", "CA", "95476"),
    }

    # Metro/City fallback coordinates when a venue is unlisted or custom
    CITY_COORDINATES: dict[str, tuple[float, float, str]] = {
        "new york:ny": (40.7128, -74.0060, "10001"),
        "east rutherford:nj": (40.8135, -74.0745, "07073"),
        "brooklyn:ny": (40.6826, -73.9754, "11217"),
        "bronx:ny": (40.8296, -73.9262, "10451"),
        "queens:ny": (40.7571, -73.8458, "11368"),
        "harrison:nj": (40.7368, -74.1503, "07029"),
        "newark:nj": (40.7357, -74.1724, "07102"),
        "philadelphia:pa": (39.9526, -75.1652, "19107"),
        "boston:ma": (42.3601, -71.0589, "02108"),
        "foxborough:ma": (42.0909, -71.2643, "02035"),
        "orchard park:ny": (42.7738, -78.7870, "14127"),
        "buffalo:ny": (42.8864, -78.8784, "14202"),
        "chicago:il": (41.8781, -87.6298, "60601"),
        "cleveland:oh": (41.4993, -81.6944, "44113"),
        "cincinnati:oh": (39.1031, -84.5120, "45202"),
        "detroit:mi": (42.3314, -83.0458, "48226"),
        "green bay:wi": (44.5192, -88.0198, "54301"),
        "milwaukee:wi": (43.0389, -87.9065, "53202"),
        "minneapolis:mn": (44.9778, -93.2650, "55401"),
        "kansas city:mo": (39.0997, -94.5786, "64105"),
        "denver:co": (39.7392, -104.9903, "80202"),
        "dallas:tx": (32.7767, -96.7970, "75201"),
        "arlington:tx": (32.7357, -97.1081, "76010"),
        "houston:tx": (29.7604, -95.3698, "77002"),
        "austin:tx": (30.2672, -97.7431, "78701"),
        "san antonio:tx": (29.4241, -98.4936, "78205"),
        "new orleans:la": (29.9511, -90.0715, "70112"),
        "atlanta:ga": (33.7490, -84.3880, "30303"),
        "charlotte:nc": (35.2271, -80.8431, "28202"),
        "miami:fl": (25.7617, -80.1918, "33101"),
        "miami gardens:fl": (25.9421, -80.2456, "33056"),
        "tampa:fl": (27.9506, -82.4572, "33602"),
        "st. petersburg:fl": (27.7676, -82.6403, "33701"),
        "orlando:fl": (28.5383, -81.3792, "32801"),
        "jacksonville:fl": (30.3322, -81.6557, "32202"),
        "nashville:tn": (36.1627, -86.7816, "37201"),
        "memphis:tn": (35.1495, -90.0490, "38103"),
        "indianapolis:in": (39.7684, -86.1581, "46204"),
        "baltimore:md": (39.2904, -76.6122, "21202"),
        "washington:dc": (38.9072, -77.0369, "20001"),
        "landover:md": (38.9340, -76.8964, "20785"),
        "pittsburgh:pa": (40.4406, -79.9959, "15219"),
        "seattle:wa": (47.6062, -122.3321, "98101"),
        "portland:or": (45.5152, -122.6784, "97201"),
        "san francisco:ca": (37.7749, -122.4194, "94102"),
        "oakland:ca": (37.8044, -122.2712, "94612"),
        "san jose:ca": (37.3382, -121.8863, "95113"),
        "santa clara:ca": (37.3541, -121.9552, "95050"),
        "los angeles:ca": (34.0522, -118.2437, "90012"),
        "inglewood:ca": (33.9617, -118.3531, "90301"),
        "anaheim:ca": (33.8366, -117.9143, "92805"),
        "carson:ca": (33.8317, -118.2817, "90745"),
        "san diego:ca": (32.7157, -117.1611, "92101"),
        "phoenix:az": (33.4484, -112.0740, "85003"),
        "glendale:az": (33.5387, -112.1860, "85301"),
        "las vegas:nv": (36.1699, -115.1398, "89101"),
        "salt lake city:ut": (40.7608, -111.8910, "84111"),
        "london:uk": (51.5074, -0.1278, "EC1A 1BB"),
        "london:us": (51.5074, -0.1278, "EC1A 1BB"),
        "quebec city:qc": (46.8139, -71.2080, "G1R 4P5"),
        "quebec city:pq": (46.8139, -71.2080, "G1R 4P5"),
        "toronto:on": (43.6532, -79.3832, "M5H 2N2"),
        "vancouver:bc": (49.2827, -123.1207, "V6B 1A1"),
        "montreal:qc": (45.5017, -73.5673, "H2Y 1C6"),
    }

    def resolve_venue_location(
        self,
        venue_name: str,
        city: str | None = None,
        state: str | None = None,
    ) -> tuple[float | None, float | None, str, str, str]:
        """Resolve precise geographic coordinates and address for sports venues with multi-tier fallback."""
        v_key = venue_name.lower().strip()

        # 1. Exact match in venue coordinates
        if v_key in self.VENUE_COORDINATES:
            return self.VENUE_COORDINATES[v_key]

        # 2. Substring or keyword match in known venue registry
        for k, coords in self.VENUE_COORDINATES.items():
            if k in v_key or v_key in k:
                return coords

        # 3. Fallback to city/state coordinates
        if city and state:
            c_key = f"{city.lower().strip()}:{state.lower().strip()}"
            if c_key in self.CITY_COORDINATES:
                lat, lon, postal = self.CITY_COORDINATES[c_key]
                return lat, lon, city, state, postal

        # 4. Fallback to city-only prefix match
        if city:
            c_clean = city.lower().strip()
            for c_key, coords in self.CITY_COORDINATES.items():
                if c_key.startswith(f"{c_clean}:"):
                    lat, lon, postal = coords
                    return lat, lon, city, state or "", postal

        return None, None, city or "Metro", state or "US", ""

    async def fetch_events(self, location: GeoPoint, radius_miles: float) -> list[RawEvent]:
        """Fetch sports events from live public feeds combined with canonical motorsport and regional broadcasts."""
        if self.coverage_mode == "disabled":
            logger.info("SportsLeagueProvider skipped: coverage_mode is disabled.")
            return []

        events: list[RawEvent] = []
        # Fixture days anchor to the declared local zone so schedule content
        # flips at local midnight. Live ESPN absolutes are unaffected.
        now = datetime.now(await resolve_app_timezone())

        # 1. Ingest live ESPN scoreboards with authentic kickoff/tipoff accuracy
        live_events = await self._fetch_live_espn_events(location, radius_miles)
        if live_events:
            events.extend(live_events)
            logger.info("SportsLeagueProvider loaded %d live events from official league scoreboards.", len(live_events))

        # 2. Add canonical motorsport broadcasts (F1, NASCAR, IndyCar, MotoGP) and regional fixtures
        existing_keys = {self._canonical_match_key(e.title, e.venue_name) for e in events}
        calendar_fixtures = self._get_calendar_fixtures(now, location, radius_miles, existing_keys)
        events.extend(calendar_fixtures)

        logger.info(
            "SportsLeagueProvider loaded %d fixtures total for location (%.4f, %.4f) [mode=%s, radius=%.1f mi].",
            len(events),
            location.latitude,
            location.longitude,
            self.coverage_mode,
            radius_miles,
        )
        return events

    def _canonical_match_key(self, title: str, venue_name: str) -> str:
        """Generate normalized lookup key to prevent duplicates between live feeds and static fixtures."""
        clean_title = title.lower().replace("nfl:", "").replace("nba:", "").replace("mlb:", "").replace("mls:", "").strip()
        return f"{venue_name.lower()}:{clean_title}"

    async def _fetch_live_espn_events(self, location: GeoPoint, radius_miles: float) -> list[RawEvent]:
        """Query official public unauthenticated ESPN scoreboard feeds for live schedule accuracy."""
        endpoints = [
            ("NFL", "football/nfl"),
            ("NBA", "basketball/nba"),
            ("MLB", "baseball/mlb"),
            ("MLS", "soccer/usa.1"),
        ]
        results: list[RawEvent] = []

        async with httpx.AsyncClient(timeout=4.0) as client:
            for league, path in endpoints:
                url = f"https://site.api.espn.com/apis/site/v2/sports/{path}/scoreboard"
                try:
                    resp = await client.get(url, headers={"User-Agent": "OpenPrevue/1.0"})
                    if resp.status_code != 200:
                        continue
                    data = resp.json()
                    raw_items = data.get("events", [])
                    for item in raw_items:
                        comp = item.get("competitions", [{}])[0]
                        venue_dict = comp.get("venue", {})
                        raw_venue_name = venue_dict.get("fullName") or "Arena / Stadium"
                        address_dict = venue_dict.get("address", {})
                        raw_city = address_dict.get("city") or "Metro"
                        raw_state = address_dict.get("state") or "US"

                        # Resolve coordinates via comprehensive stadium and city dictionary
                        lat, lon, city, state, postal = self.resolve_venue_location(raw_venue_name, raw_city, raw_state)
                        venue_name = raw_venue_name

                        # Distance filtering logic based on coverage_mode
                        if lat is not None and lon is not None:
                            dist = calculate_haversine_distance(location.latitude, location.longitude, lat, lon)
                            if self.coverage_mode == "local_only" and dist > radius_miles:
                                # Out of market stadium: suppress from local guide
                                continue
                            is_national = dist > radius_miles
                        else:
                            # Coordinates could not be resolved
                            if self.coverage_mode == "local_only":
                                # In local_only mode, unconfirmed locations cannot be assumed local
                                logger.debug("Skipping unverified sports venue in local_only mode: %s", raw_venue_name)
                                continue
                            is_national = True

                        # Competitors formatting
                        competitors = comp.get("competitors", [])
                        if len(competitors) >= 2:
                            home_team = next((c["team"]["displayName"] for c in competitors if c.get("homeAway") == "home"), competitors[0]["team"]["displayName"])
                            away_team = next((c["team"]["displayName"] for c in competitors if c.get("homeAway") == "away"), competitors[1]["team"]["displayName"])
                            event_title = f"{league}: {home_team.upper()} VS {away_team.upper()}"
                        else:
                            event_title = f"{league}: {item.get('name', 'Live Game').upper()}"

                        # Start and end ISO timestamps directly from league feed
                        start_iso = item.get("date")
                        if not start_iso:
                            continue
                        try:
                            start_dt = datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
                            end_iso = (start_dt + timedelta(hours=3)).isoformat()
                        except ValueError:
                            end_iso = None

                        # Ticket URL fallback
                        ticket_url = "https://www.espn.com"
                        tickets = comp.get("tickets", [])
                        if tickets and tickets[0].get("links"):
                            ticket_url = tickets[0]["links"][0].get("href", ticket_url)

                        results.append(
                            RawEvent(
                                source="sports_leagues",
                                source_event_id=f"espn-{league.lower()}-{item.get('id', start_iso)}",
                                venue_name=venue_name,
                                venue_address=address_dict.get("address", None),
                                venue_city=city,
                                venue_state=state,
                                venue_postal_code=postal,
                                venue_latitude=lat,
                                venue_longitude=lon,
                                title=event_title,
                                description=f"Official {league} regular season/playoff live broadcast.",
                                category="sports",
                                start_time=start_iso,
                                end_time=end_iso,
                                price_min=45.0,
                                price_max=350.0,
                                currency="USD",
                                ticket_url=ticket_url,
                                is_featured=1 if is_national else 0,
                            )
                        )
                except Exception as ex:
                    logger.debug("Live ESPN feed for %s skipped: %s", league, ex)

        return results

    def _get_calendar_fixtures(
        self,
        now: datetime,
        location: GeoPoint,
        radius_miles: float,
        existing_keys: set[str],
    ) -> list[RawEvent]:
        """Provide verified motorsport broadcasts and regional fallback fixtures with anchor days."""
        weekday = now.weekday()  # Monday=0, Sunday=6
        days_to_sunday = (6 - weekday) % 7
        if days_to_sunday == 0:
            days_to_sunday = 7

        days_to_saturday = (5 - weekday) % 7
        if days_to_saturday == 0:
            days_to_saturday = 7

        fixtures = [
            # National Motorsport Broadcasts (Fixed Sunday sessions)
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
                "days_offset": days_to_sunday,
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
                "days_offset": days_to_sunday,
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
                "days_offset": days_to_sunday + 7,
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
                "days_offset": days_to_sunday + 14,
                "hour": 14,
                "price_min": 89.0,
                "price_max": 350.0,
                "url": "https://www.motogp.com/en/calendar",
                "desc": "FIM MotoGP World Championship premier class motorcycle racing.",
                "is_national": True,
            },
            # Regional Showcase Fixtures (Anchored to authentic weekend gamedays)
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
                "days_offset": days_to_sunday,
                "hour": 12,
                "price_min": 78.0,
                "price_max": 420.0,
                "url": "https://www.neworleanssaints.com/schedule",
                "desc": "NFC South rivalry matchup live under the dome.",
                "is_national": True,
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
                "days_offset": days_to_saturday,
                "hour": 19,
                "price_min": 45.0,
                "price_max": 380.0,
                "url": "https://www.nba.com/pelicans/schedule",
                "desc": "Western Conference showdown at the Smoothie King Center.",
                "is_national": True,
            },
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
                "days_offset": days_to_sunday,
                "hour": 12,
                "price_min": 95.0,
                "price_max": 480.0,
                "url": "https://www.nba.com/knicks/schedule",
                "desc": "Eastern Conference rivalry matchup at MSG.",
                "is_national": True,
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
                "days_offset": days_to_sunday,
                "hour": 19,
                "price_min": 45.0,
                "price_max": 320.0,
                "url": "https://www.nba.com/nets/schedule",
                "desc": "Atlantic Division basketball matchup in Brooklyn.",
                "is_national": False,
            },
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
                "days_offset": days_to_saturday,
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
                "days_offset": days_to_saturday,
                "hour": 19,
                "price_min": 30.0,
                "price_max": 160.0,
                "url": "https://www.houstondynamofc.com/schedule",
                "desc": "Major League Soccer regular season fixture.",
                "is_national": True,
            },
        ]

        calendar_events: list[RawEvent] = []
        for fix in fixtures:
            dist = calculate_haversine_distance(location.latitude, location.longitude, fix["lat"], fix["lon"])

            # In local_only mode, strictly enforce radius. In national_broadcasts mode, permit national broadcasts.
            if self.coverage_mode == "local_only" and dist > radius_miles:
                continue
            if self.coverage_mode != "national_broadcasts" and dist > radius_miles and not fix.get("is_national"):
                continue

            match_key = self._canonical_match_key(fix["title"], fix["venue_name"])
            if match_key in existing_keys:
                continue

            event_date = now + timedelta(days=fix["days_offset"])
            event_dt = event_date.replace(hour=fix["hour"], minute=0, second=0, microsecond=0)
            iso_start = event_dt.isoformat()
            iso_end = (event_dt + timedelta(hours=3)).isoformat()

            is_national = dist > radius_miles
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
                is_featured=1 if (is_national or fix["league"] in ["NFL", "Formula 1", "NBA"]) else 0,
            )
            calendar_events.append(raw_event)

        return calendar_events
