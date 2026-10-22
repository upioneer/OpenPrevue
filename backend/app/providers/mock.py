"""Mock event ingestion provider with realistic, calendar-anchored listings."""

from datetime import datetime, timedelta
from backend.app.core.timezone import resolve_app_timezone
from backend.app.db.session import get_db
from backend.app.providers.base import BaseProvider, GeoPoint, RawEvent


class MockEventProvider(BaseProvider):
    """Mock event provider generating realistic, calendar-anchored event listings dynamically matched to location."""

    provider_name: str = "mock"

    async def fetch_events(self, location: GeoPoint, radius_miles: float) -> list[RawEvent]:
        """Generate mock events anchored to explicit calendar dates in the declared timezone."""
        is_nyc = abs(location.latitude - 40.7128) < 1.0 and abs(location.longitude - (-74.0060)) < 1.0
        is_nola = abs(location.latitude - 29.9511) < 1.0 and abs(location.longitude - (-90.0715)) < 1.0
        is_la = abs(location.latitude - 34.0522) < 1.0 and abs(location.longitude - (-118.2437)) < 1.0
        is_chicago = abs(location.latitude - 41.8781) < 1.0 and abs(location.longitude - (-87.6298)) < 1.0

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
                # Day 0 (Today)
                ("Saenger Theatre", "1111 Canal St", 29.9548, -90.0722, "Wicked: Broadway Landmark Musical", "theater", 0, 14, 79.0, 245.0, 0, "https://www.saengernola.com/events"),
                ("Preservation Hall", "726 St Peter", 29.9584, -90.0655, "Preservation Hall Jazz All-Stars", "music", 0, 19, 30.0, 50.0, 0, "https://www.preservationhall.com"),
                ("The Fillmore New Orleans", "6 Canal St", 29.9502, -90.0638, "Khruangbin: A La Sala World Tour", "music", 0, 20, 65.0, 165.0, 1, "https://www.fillmorenola.com/events"),
                ("Tipitina's", "501 Napoleon Ave", 29.9182, -90.1011, "Galactic: Live Uptown Funk Showcase", "music", 0, 21, 35.0, 65.0, 1, "https://www.tipitinas.com"),
                ("Joy Theater", "1200 Canal St", 29.9555, -90.0735, "Canal Street Standup Comedy Tour", "comedy", 0, 20, 25.0, 40.0, 0, "https://thejoytheater.com"),

                # Day 1 (Tomorrow)
                ("Saenger Theatre", "1111 Canal St", 29.9548, -90.0722, "Wicked: Broadway Evening Performance", "theater", 1, 19, 79.0, 245.0, 0, "https://www.saengernola.com/events"),
                ("Preservation Hall", "726 St Peter", 29.9584, -90.0655, "Traditional Acoustic Brass Sessions", "music", 1, 19, 30.0, 50.0, 0, "https://www.preservationhall.com"),
                ("The Fillmore New Orleans", "6 Canal St", 29.9502, -90.0638, "St. Paul & The Broken Bones: Live in NOLA", "music", 1, 20, 55.0, 140.0, 1, "https://www.fillmorenola.com/events"),
                ("Joy Theater", "1200 Canal St", 29.9555, -90.0735, "French Quarter Comedy Showcase", "comedy", 1, 20, 25.0, 40.0, 0, "https://thejoytheater.com"),
                ("Tipitina's", "501 Napoleon Ave", 29.9182, -90.1011, "Rebirth Brass Band: Uptown Residency", "music", 1, 21, 30.0, 55.0, 1, "https://www.tipitinas.com"),

                # Day 2 (Day +2)
                ("Saenger Theatre", "1111 Canal St", 29.9548, -90.0722, "Hamilton: Landmark Broadway Production", "theater", 2, 20, 89.0, 275.0, 0, "https://www.saengernola.com/events"),
                ("Preservation Hall", "726 St Peter", 29.9584, -90.0655, "French Quarter Evening Brass Collective", "music", 2, 18, 30.0, 50.0, 0, "https://www.preservationhall.com"),
                ("The Fillmore New Orleans", "6 Canal St", 29.9502, -90.0638, "Trombone Shorty & Orleans Avenue", "music", 2, 20, 55.0, 145.0, 1, "https://www.fillmorenola.com/events"),
                ("Joy Theater", "1200 Canal St", 29.9555, -90.0735, "Canal Street Late Night Standup", "comedy", 2, 20, 25.0, 40.0, 0, "https://thejoytheater.com"),
                ("Tipitina's", "501 Napoleon Ave", 29.9182, -90.1011, "Dumpstaphunk: Heavy NOLA Funk", "music", 2, 21, 35.0, 60.0, 1, "https://www.tipitinas.com"),

                # Day 3 (Day +3)
                ("Saenger Theatre", "1111 Canal St", 29.9548, -90.0722, "The Lion King: Broadway Landmark Tour", "theater", 3, 19, 75.0, 230.0, 0, "https://www.saengernola.com/events"),
                ("Preservation Hall", "726 St Peter", 29.9584, -90.0655, "Heritage Jazz Band: Master Sets", "music", 3, 19, 30.0, 50.0, 0, "https://www.preservationhall.com"),
                ("The Fillmore New Orleans", "6 Canal St", 29.9502, -90.0638, "Gary Clark Jr.: Live Headliner Tour", "music", 3, 20, 65.0, 160.0, 1, "https://www.fillmorenola.com/events"),
                ("Joy Theater", "1200 Canal St", 29.9555, -90.0735, "NOLA Indie Headliner Showcase", "comedy", 3, 20, 25.0, 40.0, 0, "https://thejoytheater.com"),
                ("Tipitina's", "501 Napoleon Ave", 29.9182, -90.1011, "George Porter Jr. & Runnin' Pardners", "music", 3, 21, 30.0, 55.0, 1, "https://www.tipitinas.com"),

                # Day 4 (Day +4)
                ("Saenger Theatre", "1111 Canal St", 29.9548, -90.0722, "Saenger Symphony: Film in Concert", "theater", 4, 20, 60.0, 180.0, 0, "https://www.saengernola.com/events"),
                ("Preservation Hall", "726 St Peter", 29.9584, -90.0655, "New Orleans Traditional Jazz Revival", "music", 4, 18, 30.0, 50.0, 0, "https://www.preservationhall.com"),
                ("The Fillmore New Orleans", "6 Canal St", 29.9502, -90.0638, "Lake Street Dive: Good Together Tour", "music", 4, 20, 50.0, 135.0, 1, "https://www.fillmorenola.com/events"),
                ("Joy Theater", "1200 Canal St", 29.9555, -90.0735, "Downtown Comedy All-Stars", "comedy", 4, 20, 25.0, 40.0, 0, "https://thejoytheater.com"),
                ("Tipitina's", "501 Napoleon Ave", 29.9182, -90.1011, "The Soul Rebels: Uptown Brass Party", "music", 4, 22, 30.0, 55.0, 1, "https://www.tipitinas.com"),

                # Day 5 (Day +5)
                ("Saenger Theatre", "1111 Canal St", 29.9548, -90.0722, "Wicked: Weekend Broadway Matinee", "theater", 5, 14, 79.0, 245.0, 0, "https://www.saengernola.com/events"),
                ("Preservation Hall", "726 St Peter", 29.9584, -90.0655, "Preservation Hall Legacy Session", "music", 5, 19, 30.0, 50.0, 0, "https://www.preservationhall.com"),
                ("The Fillmore New Orleans", "6 Canal St", 29.9502, -90.0638, "Leon Bridges: The Leon Tour", "music", 5, 21, 70.0, 175.0, 1, "https://www.fillmorenola.com/events"),
                ("Joy Theater", "1200 Canal St", 29.9555, -90.0735, "Joy Theater Weekend Standup Bash", "comedy", 5, 21, 30.0, 45.0, 0, "https://thejoytheater.com"),
                ("Tipitina's", "501 Napoleon Ave", 29.9182, -90.1011, "Big Sam's Funky Nation: Live at Tip's", "music", 5, 21, 35.0, 65.0, 1, "https://www.tipitinas.com"),

                # Day 6 (Day +6)
                ("Saenger Theatre", "1111 Canal St", 29.9548, -90.0722, "Saenger Broadway Showcase Finale", "theater", 6, 19, 79.0, 245.0, 0, "https://www.saengernola.com/events"),
                ("Preservation Hall", "726 St Peter", 29.9584, -90.0655, "Creole Acoustic All-Stars Showcase", "music", 6, 18, 30.0, 50.0, 0, "https://www.preservationhall.com"),
                ("The Fillmore New Orleans", "6 Canal St", 29.9502, -90.0638, "The Revivalists: Hometown Showcase", "music", 6, 19, 65.0, 160.0, 1, "https://www.fillmorenola.com/events"),
                ("Joy Theater", "1200 Canal St", 29.9555, -90.0735, "New Orleans Improv & Standup Gala", "comedy", 6, 19, 25.0, 40.0, 0, "https://thejoytheater.com"),
                ("Tipitina's", "501 Napoleon Ave", 29.9182, -90.1011, "Anders Osborne & Friends: Sunday Jam", "music", 6, 20, 35.0, 65.0, 1, "https://www.tipitinas.com"),

                # Upcoming Sunday NFL Anchor
                ("Caesars Superdome", "1500 Sugar Bowl Dr", 29.9511, -90.0812, "NFL: New Orleans Saints vs Atlanta Falcons", "sports", days_to_sunday, 12, 75.0, 420.0, 1, "https://www.neworleanssaints.com/tickets"),
            ]
        elif is_nyc:
            city = "New York"
            state = "NY"
            postal = "10001"
            schedule = [
                # Day 0 (Today)
                ("Gershwin Theatre", "222 W 51st St", 40.7624, -73.9851, "Wicked: Broadway Landmark Musical", "theater", 0, 14, 79.0, 245.0, 0, "https://wickedthemusical.com"),
                ("Blue Note Jazz Club", "131 W 3rd St", 40.7308, -74.0006, "Ron Carter Quintet: Greenwich Village Sets", "music", 0, 19, 30.0, 55.0, 0, "https://www.bluenotejazz.com/nyc"),
                ("Radio City Music Hall", "1260 6th Ave", 40.7599, -73.9799, "Khruangbin: A La Sala World Tour", "music", 0, 20, 65.0, 165.0, 1, "https://www.msg.com/radio-city-music-hall"),
                ("Brooklyn Steel", "319 Frost St", 40.7193, -73.9388, "Japanese Breakfast: Live in Williamsburg", "music", 0, 21, 35.0, 75.0, 1, "https://www.bowerypresents.com/brooklyn-steel"),
                ("Comedy Cellar", "117 MacDougal St", 40.7300, -74.0002, "MacDougal Street Standup Showcase", "comedy", 0, 20, 25.0, 35.0, 0, "https://www.comedycellar.com"),

                # Day 1 (Tomorrow)
                ("Gershwin Theatre", "222 W 51st St", 40.7624, -73.9851, "Wicked: Broadway Evening Performance", "theater", 1, 19, 79.0, 245.0, 0, "https://wickedthemusical.com"),
                ("Beacon Theatre", "2124 Broadway", 40.7806, -73.9813, "Trey Anastasio: Solo Acoustic Residency", "music", 1, 20, 55.0, 140.0, 1, "https://www.msg.com/beacon-theatre"),
                ("Blue Note Jazz Club", "131 W 3rd St", 40.7308, -74.0006, "Christian McBride Big Band Residency", "music", 1, 19, 35.0, 60.0, 0, "https://www.bluenotejazz.com/nyc"),
                ("Comedy Cellar", "117 MacDougal St", 40.7300, -74.0002, "Village Underground Showcase", "comedy", 1, 20, 25.0, 35.0, 0, "https://www.comedycellar.com"),
                ("Brooklyn Steel", "319 Frost St", 40.7193, -73.9388, "Alvvays: Blue Rev Tour Live", "music", 1, 20, 40.0, 85.0, 1, "https://www.bowerypresents.com/brooklyn-steel"),

                # Day 2 (Day +2)
                ("Gershwin Theatre", "222 W 51st St", 40.7624, -73.9851, "Hamilton: Broadway Landmark Evening", "theater", 2, 20, 95.0, 280.0, 0, "https://wickedthemusical.com"),
                ("Beacon Theatre", "2124 Broadway", 40.7806, -73.9813, "Norah Jones: Visions Tour Live", "music", 2, 20, 65.0, 155.0, 1, "https://www.msg.com/beacon-theatre"),
                ("Comedy Cellar", "117 MacDougal St", 40.7300, -74.0002, "Fat Black Pussycat Late Night Sets", "comedy", 2, 21, 25.0, 35.0, 0, "https://www.comedycellar.com"),
                ("Blue Note Jazz Club", "131 W 3rd St", 40.7308, -74.0006, "Robert Glasper Experiment Live", "music", 2, 20, 40.0, 75.0, 0, "https://www.bluenotejazz.com/nyc"),

                # Day 3 (Day +3)
                ("Gershwin Theatre", "222 W 51st St", 40.7624, -73.9851, "The Lion King: Landmark Broadway Run", "theater", 3, 19, 85.0, 250.0, 0, "https://wickedthemusical.com"),
                ("Radio City Music Hall", "1260 6th Ave", 40.7599, -73.9799, "Leon Bridges: Live at Radio City", "music", 3, 20, 75.0, 195.0, 1, "https://www.msg.com/radio-city-music-hall"),
                ("Brooklyn Steel", "319 Frost St", 40.7193, -73.9388, "Turnstile: GLOW ON World Tour", "music", 3, 20, 45.0, 95.0, 1, "https://www.bowerypresents.com/brooklyn-steel"),
                ("Comedy Cellar", "117 MacDougal St", 40.7300, -74.0002, "MacDougal Late Night Improv & Standup", "comedy", 3, 22, 25.0, 35.0, 0, "https://www.comedycellar.com"),

                # Day 4 (Day +4)
                ("Gershwin Theatre", "222 W 51st St", 40.7624, -73.9851, "Wicked: Friday Evening Showcase", "theater", 4, 20, 79.0, 245.0, 0, "https://wickedthemusical.com"),
                ("Beacon Theatre", "2124 Broadway", 40.7806, -73.9813, "Father John Misty: Mahashmashana Tour", "music", 4, 20, 55.0, 145.0, 1, "https://www.msg.com/beacon-theatre"),
                ("Blue Note Jazz Club", "131 W 3rd St", 40.7308, -74.0006, "Bill Frisell Trio: Village Nights", "music", 4, 19, 35.0, 60.0, 0, "https://www.bluenotejazz.com/nyc"),
                ("Comedy Cellar", "117 MacDougal St", 40.7300, -74.0002, "Weekend Prime Comedy Cellar Standup", "comedy", 4, 20, 30.0, 45.0, 0, "https://www.comedycellar.com"),

                # Day 5 (Day +5)
                ("Gershwin Theatre", "222 W 51st St", 40.7624, -73.9851, "Wicked: Broadway Weekend Matinee", "theater", 5, 14, 79.0, 245.0, 0, "https://wickedthemusical.com"),
                ("Radio City Music Hall", "1260 6th Ave", 40.7599, -73.9799, "St. Vincent: All Born Screaming Tour", "music", 5, 20, 65.0, 175.0, 1, "https://www.msg.com/radio-city-music-hall"),
                ("Brooklyn Steel", "319 Frost St", 40.7193, -73.9388, "IDLES: Love Is The FING Tour", "music", 5, 21, 45.0, 95.0, 1, "https://www.bowerypresents.com/brooklyn-steel"),
                ("Comedy Cellar", "117 MacDougal St", 40.7300, -74.0002, "Saturday Night Standup Showcase", "comedy", 5, 21, 30.0, 45.0, 0, "https://www.comedycellar.com"),

                # Day 6 (Day +6)
                ("Gershwin Theatre", "222 W 51st St", 40.7624, -73.9851, "Wicked: Sunday Evening Performance", "theater", 6, 19, 79.0, 245.0, 0, "https://wickedthemusical.com"),
                ("Blue Note Jazz Club", "131 W 3rd St", 40.7308, -74.0006, "Sunday Jazz Brunch & Evening Sets", "music", 6, 18, 35.0, 60.0, 0, "https://www.bluenotejazz.com/nyc"),
                ("Beacon Theatre", "2124 Broadway", 40.7806, -73.9813, "Gary Clark Jr.: Acoustic & Electric Night", "music", 6, 19, 65.0, 160.0, 1, "https://www.msg.com/beacon-theatre"),
                ("Comedy Cellar", "117 MacDougal St", 40.7300, -74.0002, "Sunday Comedy Wrap Showcase", "comedy", 6, 19, 25.0, 35.0, 0, "https://www.comedycellar.com"),

                # Upcoming Sunday NBA Anchor
                ("Madison Square Garden", "4 Pennsylvania Plaza", 40.7505, -73.9934, "NBA: New York Knicks vs Boston Celtics", "sports", days_to_sunday, 12, 85.0, 450.0, 1, "https://www.msg.com/madison-square-garden"),
            ]
        elif is_la:
            city = "Los Angeles"
            state = "CA"
            postal = "90012"
            schedule = [
                # Day 0 (Today)
                ("Hollywood Bowl", "2301 N Highland Ave", 34.1122, -118.3391, "Symphony Under the Stars", "music", 0, 19, 45.0, 185.0, 1, "https://www.hollywoodbowl.com"),
                ("The Greek Theatre", "2700 N Vermont Ave", 34.1197, -118.2965, "Khruangbin: A La Sala World Tour", "music", 0, 20, 55.0, 160.0, 1, "https://www.lagreektheatre.com"),
                ("The Comedy Store", "8433 Sunset Blvd", 34.0945, -118.3739, "Sunset Strip Comedy Headliners", "comedy", 0, 20, 25.0, 45.0, 0, "https://thecomedystore.com"),
                ("Walt Disney Concert Hall", "111 S Grand Ave", 34.0553, -118.2498, "LA Phil: Masterwork Showcase", "music", 0, 14, 60.0, 220.0, 0, "https://www.laphil.com"),

                # Day 1 (Tomorrow)
                ("Hollywood Bowl", "2301 N Highland Ave", 34.1122, -118.3391, "John Williams Film Score Gala", "music", 1, 20, 55.0, 210.0, 1, "https://www.hollywoodbowl.com"),
                ("The Greek Theatre", "2700 N Vermont Ave", 34.1197, -118.2965, "Leon Bridges: Live at The Greek", "music", 1, 20, 50.0, 145.0, 1, "https://www.lagreektheatre.com"),
                ("The Comedy Store", "8433 Sunset Blvd", 34.0945, -118.3739, "Main Room Weekend Showcase", "comedy", 1, 21, 30.0, 50.0, 0, "https://thecomedystore.com"),
                ("Walt Disney Concert Hall", "111 S Grand Ave", 34.0553, -118.2498, "Organ Recital & Chamber Sets", "music", 1, 19, 40.0, 120.0, 0, "https://www.laphil.com"),

                # Day 2 (Day +2)
                ("Hollywood Bowl", "2301 N Highland Ave", 34.1122, -118.3391, "Jazz at the Bowl All-Stars", "music", 2, 20, 40.0, 160.0, 1, "https://www.hollywoodbowl.com"),
                ("The Greek Theatre", "2700 N Vermont Ave", 34.1197, -118.2965, "St. Vincent: All Born Screaming", "music", 2, 20, 55.0, 150.0, 1, "https://www.lagreektheatre.com"),
                ("The Comedy Store", "8433 Sunset Blvd", 34.0945, -118.3739, "Original Room Late Night Standup", "comedy", 2, 22, 25.0, 40.0, 0, "https://thecomedystore.com"),

                # Day 3 (Day +3)
                ("The Greek Theatre", "2700 N Vermont Ave", 34.1197, -118.2965, "Gary Clark Jr.: Live Headliner", "music", 3, 20, 60.0, 160.0, 1, "https://www.lagreektheatre.com"),
                ("Walt Disney Concert Hall", "111 S Grand Ave", 34.0553, -118.2498, "Contemporary Chamber Ensemble", "music", 3, 20, 50.0, 140.0, 0, "https://www.laphil.com"),
                ("The Comedy Store", "8433 Sunset Blvd", 34.0945, -118.3739, "Belly Room Standup Spotlight", "comedy", 3, 20, 20.0, 35.0, 0, "https://thecomedystore.com"),

                # Day 4 (Day +4)
                ("Hollywood Bowl", "2301 N Highland Ave", 34.1122, -118.3391, "Friday Fireworks Spectacular", "music", 4, 20, 50.0, 195.0, 1, "https://www.hollywoodbowl.com"),
                ("The Comedy Store", "8433 Sunset Blvd", 34.0945, -118.3739, "Friday Night Comedy Bash", "comedy", 4, 21, 30.0, 50.0, 0, "https://thecomedystore.com"),

                # Day 5 (Day +5)
                ("Hollywood Bowl", "2301 N Highland Ave", 34.1122, -118.3391, "Weekend Classical Matinee", "music", 5, 14, 45.0, 175.0, 0, "https://www.hollywoodbowl.com"),
                ("The Greek Theatre", "2700 N Vermont Ave", 34.1197, -118.2965, "Turnstile: GLOW ON Tour", "music", 5, 21, 55.0, 140.0, 1, "https://www.lagreektheatre.com"),

                # Day 6 (Day +6)
                ("Walt Disney Concert Hall", "111 S Grand Ave", 34.0553, -118.2498, "Sunday Symphony Showcase", "music", 6, 15, 45.0, 160.0, 0, "https://www.laphil.com"),
                ("The Comedy Store", "8433 Sunset Blvd", 34.0945, -118.3739, "Sunday Roast & Standup Showcase", "comedy", 6, 19, 25.0, 40.0, 0, "https://thecomedystore.com"),

                # Anchor Sunday NBA
                ("Crypto.com Arena", "1111 S Figueroa St", 34.0430, -118.2673, "NBA: Los Angeles Lakers vs Golden State Warriors", "sports", days_to_sunday, 12, 85.0, 480.0, 1, "https://www.nba.com/lakers/tickets"),
            ]
        elif is_chicago:
            city = "Chicago"
            state = "IL"
            postal = "60601"
            schedule = [
                # Day 0 (Today)
                ("The Chicago Theatre", "175 N State St", 41.8853, -87.6277, "Wicked: Broadway Landmark Tour", "theater", 0, 14, 75.0, 240.0, 0, "https://www.msg.com/the-chicago-theatre"),
                ("Metro Chicago", "3730 N Clark St", 41.9508, -87.6587, "Japanese Breakfast: Live at Metro", "music", 0, 20, 35.0, 75.0, 1, "https://metrochicago.com"),
                ("The Green Mill", "4802 N Broadway", 41.9692, -87.6599, "Uptown Traditional Jazz Sets", "music", 0, 19, 20.0, 40.0, 0, "https://greenmilljazz.com"),
                ("Steppenwolf Theatre", "1650 N Halsted St", 41.9126, -87.6483, "Contemporary Stage Production", "theater", 0, 19, 50.0, 130.0, 0, "https://www.steppenwolf.org"),

                # Day 1 (Tomorrow)
                ("The Chicago Theatre", "175 N State St", 41.8853, -87.6277, "Wicked: Broadway Evening Performance", "theater", 1, 19, 75.0, 240.0, 0, "https://www.msg.com/the-chicago-theatre"),
                ("Metro Chicago", "3730 N Clark St", 41.9508, -87.6587, "Khruangbin: A La Sala World Tour", "music", 1, 20, 50.0, 135.0, 1, "https://metrochicago.com"),
                ("The Green Mill", "4802 N Broadway", 41.9692, -87.6599, "Green Mill Jazz Quartet Residency", "music", 1, 20, 25.0, 45.0, 0, "https://greenmilljazz.com"),
                ("Steppenwolf Theatre", "1650 N Halsted St", 41.9126, -87.6483, "Steppenwolf Ensemble Showcase", "theater", 1, 20, 55.0, 140.0, 0, "https://www.steppenwolf.org"),

                # Day 2 (Day +2)
                ("The Chicago Theatre", "175 N State St", 41.8853, -87.6277, "Hamilton: Broadway Landmark Run", "theater", 2, 20, 85.0, 260.0, 0, "https://www.msg.com/the-chicago-theatre"),
                ("Metro Chicago", "3730 N Clark St", 41.9508, -87.6587, "St. Paul & The Broken Bones", "music", 2, 20, 45.0, 95.0, 1, "https://metrochicago.com"),
                ("The Green Mill", "4802 N Broadway", 41.9692, -87.6599, "Chicago Jazz Underground Sets", "music", 2, 21, 20.0, 40.0, 0, "https://greenmilljazz.com"),

                # Day 3 (Day +3)
                ("The Chicago Theatre", "175 N State St", 41.8853, -87.6277, "The Lion King: Broadway Tour", "theater", 3, 19, 75.0, 230.0, 0, "https://www.msg.com/the-chicago-theatre"),
                ("Metro Chicago", "3730 N Clark St", 41.9508, -87.6587, "Gary Clark Jr.: Live in Wrigleyville", "music", 3, 20, 55.0, 140.0, 1, "https://metrochicago.com"),
                ("Steppenwolf Theatre", "1650 N Halsted St", 41.9126, -87.6483, "New American Play Festival", "theater", 3, 19, 45.0, 110.0, 0, "https://www.steppenwolf.org"),

                # Day 4 (Day +4)
                ("The Chicago Theatre", "175 N State St", 41.8853, -87.6277, "Chicago Comedy All-Stars Night", "comedy", 4, 20, 40.0, 110.0, 0, "https://www.msg.com/the-chicago-theatre"),
                ("The Green Mill", "4802 N Broadway", 41.9692, -87.6599, "Friday Night Jazz Showcase", "music", 4, 21, 25.0, 45.0, 0, "https://greenmilljazz.com"),
                ("Metro Chicago", "3730 N Clark St", 41.9508, -87.6587, "Turnstile: GLOW ON World Tour", "music", 4, 21, 45.0, 95.0, 1, "https://metrochicago.com"),

                # Day 5 (Day +5)
                ("The Chicago Theatre", "175 N State St", 41.8853, -87.6277, "Wicked: Weekend Broadway Matinee", "theater", 5, 14, 75.0, 240.0, 0, "https://www.msg.com/the-chicago-theatre"),
                ("Steppenwolf Theatre", "1650 N Halsted St", 41.9126, -87.6483, "Saturday Ensemble Matinee", "theater", 5, 15, 50.0, 125.0, 0, "https://www.steppenwolf.org"),

                # Day 6 (Day +6)
                ("The Chicago Theatre", "175 N State St", 41.8853, -87.6277, "Sunday Symphony Gala Finale", "music", 6, 18, 55.0, 160.0, 0, "https://www.msg.com/the-chicago-theatre"),
                ("The Green Mill", "4802 N Broadway", 41.9692, -87.6599, "Uptown Poetry & Jazz Slam", "music", 6, 19, 15.0, 30.0, 0, "https://greenmilljazz.com"),

                # Anchor Sunday NBA
                ("United Center", "1901 W Madison St", 41.8807, -87.6742, "NBA: Chicago Bulls vs Milwaukee Bucks", "sports", days_to_sunday, 12, 75.0, 420.0, 1, "https://www.nba.com/bulls/tickets"),
            ]
        else:
            city = "Local Metro"
            async with get_db() as db:
                try:
                    async with db.execute("SELECT value FROM settings WHERE key = 'metro_label'") as cursor:
                        row = await cursor.fetchone()
                        if row and row["value"]:
                            city = row["value"].title()
                except Exception:
                    pass

            state = "US"
            postal = "00000"
            lat = location.latitude
            lon = location.longitude
            schedule = [
                # Day 0 (Today)
                (f"{city} Civic Playhouse", "700 Civic Blvd", lat - 0.015, lon + 0.01, "Broadway Touring Musical", "theater", 0, 14, 65.0, 180.0, 0, "https://www.broadway.org"),
                (f"{city} Symphony Hall", "500 Center Ave", lat + 0.015, lon - 0.01, "Symphony Orchestra Gala", "music", 0, 19, 40.0, 95.0, 1, "https://www.ticketmaster.com"),
                (f"{city} Grand Theatre", "250 Main St", lat - 0.01, lon - 0.01, "Headliner Live Concert Tour", "music", 0, 20, 55.0, 150.0, 1, "https://www.ticketmaster.com"),
                (f"{city} Comedy Underground", "42 Arts District", lat + 0.005, lon - 0.005, "Standup Comedy Headliners", "comedy", 0, 20, 25.0, 45.0, 0, "https://www.ticketmaster.com"),

                # Day 1 (Tomorrow)
                (f"{city} Civic Playhouse", "700 Civic Blvd", lat - 0.015, lon + 0.01, "Broadway Touring Evening Show", "theater", 1, 19, 65.0, 180.0, 0, "https://www.broadway.org"),
                (f"{city} Comedy Underground", "42 Arts District", lat + 0.005, lon - 0.005, "Standup Comedy Headliners", "comedy", 1, 20, 25.0, 45.0, 0, "https://www.ticketmaster.com"),
                (f"{city} Grand Theatre", "250 Main St", lat - 0.01, lon - 0.01, "Indie Rock Showcase", "music", 1, 20, 45.0, 110.0, 1, "https://www.ticketmaster.com"),
                (f"{city} Symphony Hall", "500 Center Ave", lat + 0.015, lon - 0.01, "Chamber Music Evening Series", "music", 1, 19, 35.0, 85.0, 0, "https://www.ticketmaster.com"),

                # Day 2 (Day +2)
                (f"{city} Civic Playhouse", "700 Civic Blvd", lat - 0.015, lon + 0.01, "Landmark Stage Production", "theater", 2, 20, 65.0, 180.0, 0, "https://www.broadway.org"),
                (f"{city} Comedy Underground", "42 Arts District", lat + 0.005, lon - 0.005, "Late Night Improv & Standup", "comedy", 2, 20, 25.0, 45.0, 0, "https://www.ticketmaster.com"),
                (f"{city} Grand Theatre", "250 Main St", lat - 0.01, lon - 0.01, "National Touring Rock Showcase", "music", 2, 20, 50.0, 130.0, 1, "https://www.ticketmaster.com"),

                # Day 3 (Day +3)
                (f"{city} Civic Playhouse", "700 Civic Blvd", lat - 0.015, lon + 0.01, "Broadway Tour Evening Musical", "theater", 3, 19, 65.0, 180.0, 0, "https://www.broadway.org"),
                (f"{city} Symphony Hall", "500 Center Ave", lat + 0.015, lon - 0.01, "Philharmonic Pops Night", "music", 3, 19, 45.0, 110.0, 1, "https://www.ticketmaster.com"),
                (f"{city} Comedy Underground", "42 Arts District", lat + 0.005, lon - 0.005, "Underground Comedy Spotlight", "comedy", 3, 21, 25.0, 40.0, 0, "https://www.ticketmaster.com"),

                # Day 4 (Day +4)
                (f"{city} Grand Theatre", "250 Main St", lat - 0.01, lon - 0.01, "Acoustic Songwriters Night", "music", 4, 20, 40.0, 95.0, 1, "https://www.ticketmaster.com"),
                (f"{city} Comedy Underground", "42 Arts District", lat + 0.005, lon - 0.005, "Weekend Comedy Showcase", "comedy", 4, 20, 25.0, 45.0, 0, "https://www.ticketmaster.com"),
                (f"{city} Symphony Hall", "500 Center Ave", lat + 0.015, lon - 0.01, "Guest Master Soloist Gala", "music", 4, 19, 50.0, 125.0, 1, "https://www.ticketmaster.com"),

                # Day 5 (Day +5)
                (f"{city} Civic Playhouse", "700 Civic Blvd", lat - 0.015, lon + 0.01, "Weekend Matinee Musical", "theater", 5, 14, 65.0, 180.0, 0, "https://www.broadway.org"),
                (f"{city} Grand Theatre", "250 Main St", lat - 0.01, lon - 0.01, "Electric Blues & Soul Tour", "music", 5, 21, 55.0, 140.0, 1, "https://www.ticketmaster.com"),
                (f"{city} Comedy Underground", "42 Arts District", lat + 0.005, lon - 0.005, "Saturday Headliner Comedy Standup", "comedy", 5, 21, 30.0, 50.0, 0, "https://www.ticketmaster.com"),

                # Day 6 (Day +6)
                (f"{city} Civic Playhouse", "700 Civic Blvd", lat - 0.015, lon + 0.01, "Sunday Broadway Gala Finale", "theater", 6, 19, 65.0, 180.0, 0, "https://www.broadway.org"),
                (f"{city} Symphony Hall", "500 Center Ave", lat + 0.015, lon - 0.01, "Symphony Sunday Matinee", "music", 6, 15, 35.0, 90.0, 1, "https://www.ticketmaster.com"),
                (f"{city} Comedy Underground", "42 Arts District", lat + 0.005, lon - 0.005, "Sunday Open Mic & Standup", "comedy", 6, 19, 20.0, 35.0, 0, "https://www.ticketmaster.com"),

                # Upcoming Sunday Sports Anchor
                (f"{city} Arena", "100 Arena Way", lat + 0.01, lon + 0.01, "Pro Basketball: Home Showdown", "sports", days_to_sunday, 12, 45.0, 250.0, 1, "https://www.nba.com/tickets"),
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
