"""Mock event ingestion provider with realistic local listings."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from backend.app.providers.base import BaseProvider, GeoPoint, RawEvent


class MockEventProvider(BaseProvider):
    """Mock event provider generating realistic, time-anchored event listings."""

    provider_name: str = "mock"

    async def fetch_events(self, location: GeoPoint, radius_miles: float) -> list[RawEvent]:
        """Generate mock events relative to current timestamp."""
        # Use local timezone
        tz = ZoneInfo("America/Chicago")
        now = datetime.now(tz)
        today = now.date()

        # Build dates relative to today
        t_today_11am = datetime(today.year, today.month, today.day, 11, 0, tzinfo=tz)
        t_today_2pm = datetime(today.year, today.month, today.day, 14, 0, tzinfo=tz)
        t_today_7pm = datetime(today.year, today.month, today.day, 19, 0, tzinfo=tz)
        t_today_8pm = datetime(today.year, today.month, today.day, 20, 0, tzinfo=tz)
        t_today_9pm = datetime(today.year, today.month, today.day, 21, 0, tzinfo=tz)

        d_tomorrow = today + timedelta(days=1)
        t_tom_2pm = datetime(d_tomorrow.year, d_tomorrow.month, d_tomorrow.day, 14, 0, tzinfo=tz)
        t_tom_7pm = datetime(d_tomorrow.year, d_tomorrow.month, d_tomorrow.day, 19, 0, tzinfo=tz)
        t_tom_8pm = datetime(d_tomorrow.year, d_tomorrow.month, d_tomorrow.day, 20, 0, tzinfo=tz)
        t_tom_9pm = datetime(d_tomorrow.year, d_tomorrow.month, d_tomorrow.day, 21, 0, tzinfo=tz)

        d_in2days = today + timedelta(days=2)
        t_in2_7pm = datetime(d_in2days.year, d_in2days.month, d_in2days.day, 19, 0, tzinfo=tz)
        t_in2_8pm = datetime(d_in2days.year, d_in2days.month, d_in2days.day, 20, 0, tzinfo=tz)

        d_sunday = today + timedelta(days=(6 - today.weekday()) % 7)
        if d_sunday == today:
            d_sunday = today + timedelta(days=7)
        t_sun_12pm = datetime(d_sunday.year, d_sunday.month, d_sunday.day, 12, 0, tzinfo=tz)

        mock_raw_data = [
            # Caesars Superdome - Featured NFL
            RawEvent(
                source="mock",
                source_event_id="mock-saints-falcons",
                venue_name="Caesars Superdome",
                venue_address="1500 Sugar Bowl Dr",
                venue_city="New Orleans",
                venue_state="LA",
                venue_postal_code="70112",
                venue_latitude=29.9511,
                venue_longitude=-90.0812,
                title="New Orleans Saints vs Atlanta Falcons",
                description="NFC South rivalry showdown at the Caesars Superdome. Doors open 2 hours prior to kickoff.",
                category="sports",
                start_time=t_sun_12pm.isoformat(),
                end_time=(t_sun_12pm + timedelta(hours=3, minutes=30)).isoformat(),
                price_min=68.00,
                price_max=285.00,
                currency="USD",
                image_url="https://images.unsplash.com/photo-1566577739112-5180d4bf9390?w=800&auto=format&fit=crop&q=80",
                ticket_url="https://www.ticketmaster.com",
                is_featured=1,
            ),
            # House of Blues - Gospel Brunch & Evening Concert
            RawEvent(
                source="mock",
                source_event_id="mock-hob-brunch",
                venue_name="House of Blues New Orleans",
                venue_address="225 Decatur St",
                venue_city="New Orleans",
                venue_state="LA",
                venue_postal_code="70130",
                venue_latitude=29.9535,
                venue_longitude=-90.0655,
                title="World Famous Gospel Brunch",
                description="Traditional Southern buffet and live gospel celebration in the historic music hall.",
                category="community",
                start_time=t_today_11am.isoformat(),
                end_time=(t_today_11am + timedelta(hours=2)).isoformat(),
                price_min=45.00,
                price_max=55.00,
                currency="USD",
                image_url="https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800&auto=format&fit=crop&q=80",
                ticket_url="https://www.houseofblues.com/neworleans",
                is_featured=0,
            ),
            RawEvent(
                source="mock",
                source_event_id="mock-hob-tab-benoit",
                venue_name="House of Blues New Orleans",
                venue_address="225 Decatur St",
                venue_city="New Orleans",
                venue_state="LA",
                venue_postal_code="70130",
                venue_latitude=29.9535,
                venue_longitude=-90.0655,
                title="Tab Benoit & The Delta Blues Allstars",
                description="Grammy-nominated Louisiana blues guitarist performing live in the Voodoo Garden.",
                category="music",
                start_time=t_today_8pm.isoformat(),
                end_time=(t_today_8pm + timedelta(hours=3)).isoformat(),
                price_min=32.50,
                price_max=75.00,
                currency="USD",
                image_url="https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=800&auto=format&fit=crop&q=80",
                ticket_url="https://www.houseofblues.com/neworleans",
                is_featured=1,
            ),
            # Fillmore NOLA - Khruangbin & Dark Star
            RawEvent(
                source="mock",
                source_event_id="mock-fillmore-khruangbin",
                venue_name="The Fillmore New Orleans",
                venue_address="6 Canal St",
                venue_city="New Orleans",
                venue_state="LA",
                venue_postal_code="70130",
                venue_latitude=29.9507,
                venue_longitude=-90.0635,
                title="Khruangbin: A La Sala Tour",
                description="Psychedelic dub-funk trio performing live on Canal Street with special guests.",
                category="music",
                start_time=t_today_8pm.isoformat(),
                end_time=(t_today_8pm + timedelta(hours=3)).isoformat(),
                price_min=59.50,
                price_max=145.00,
                currency="USD",
                image_url="https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&auto=format&fit=crop&q=80",
                ticket_url="https://www.fillmorenola.com",
                is_featured=1,
            ),
            RawEvent(
                source="mock",
                source_event_id="mock-fillmore-dark-star",
                venue_name="The Fillmore New Orleans",
                venue_address="6 Canal St",
                venue_city="New Orleans",
                venue_state="LA",
                venue_postal_code="70130",
                venue_latitude=29.9507,
                venue_longitude=-90.0635,
                title="Dark Star Orchestra: Grateful Dead Experience",
                description="Faithfully recreating historic Grateful Dead concert setlists note for note.",
                category="music",
                start_time=t_tom_8pm.isoformat(),
                end_time=(t_tom_8pm + timedelta(hours=3, minutes=30)).isoformat(),
                price_min=35.00,
                price_max=65.00,
                currency="USD",
                image_url="https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=800&auto=format&fit=crop&q=80",
                ticket_url="https://www.fillmorenola.com",
                is_featured=0,
            ),
            # Saenger Theatre - Broadway Series
            RawEvent(
                source="mock",
                source_event_id="mock-saenger-wicked-matinee",
                venue_name="Saenger Theatre",
                venue_address="1111 Canal St",
                venue_city="New Orleans",
                venue_state="LA",
                venue_postal_code="70112",
                venue_latitude=29.9556,
                venue_longitude=-90.0725,
                title="Wicked: Broadway National Tour (Matinee)",
                description="The untold true story of the Witches of Oz in the grand historic Saenger Theatre.",
                category="theater",
                start_time=t_today_2pm.isoformat(),
                end_time=(t_today_2pm + timedelta(hours=2, minutes=45)).isoformat(),
                price_min=54.00,
                price_max=185.00,
                currency="USD",
                image_url="https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?w=800&auto=format&fit=crop&q=80",
                ticket_url="https://www.saengernola.com",
                is_featured=0,
            ),
            RawEvent(
                source="mock",
                source_event_id="mock-saenger-wicked-evening",
                venue_name="Saenger Theatre",
                venue_address="1111 Canal St",
                venue_city="New Orleans",
                venue_state="LA",
                venue_postal_code="70112",
                venue_latitude=29.9556,
                venue_longitude=-90.0725,
                title="Wicked: Broadway National Tour (Evening)",
                description="The untold true story of the Witches of Oz in the grand historic Saenger Theatre.",
                category="theater",
                start_time=t_today_8pm.isoformat(),
                end_time=(t_today_8pm + timedelta(hours=2, minutes=45)).isoformat(),
                price_min=64.00,
                price_max=215.00,
                currency="USD",
                image_url="https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?w=800&auto=format&fit=crop&q=80",
                ticket_url="https://www.saengernola.com",
                is_featured=1,
            ),
            RawEvent(
                source="mock",
                source_event_id="mock-saenger-wicked-tom",
                venue_name="Saenger Theatre",
                venue_address="1111 Canal St",
                venue_city="New Orleans",
                venue_state="LA",
                venue_postal_code="70112",
                venue_latitude=29.9556,
                venue_longitude=-90.0725,
                title="Wicked: Broadway National Tour",
                description="The untold true story of the Witches of Oz.",
                category="theater",
                start_time=t_tom_8pm.isoformat(),
                end_time=(t_tom_8pm + timedelta(hours=2, minutes=45)).isoformat(),
                price_min=54.00,
                price_max=185.00,
                currency="USD",
                image_url="https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?w=800&auto=format&fit=crop&q=80",
                ticket_url="https://www.saengernola.com",
                is_featured=0,
            ),
            # Tipitina's - Funk & Brass
            RawEvent(
                source="mock",
                source_event_id="mock-tipitinas-pres-brass",
                venue_name="Tipitina's",
                venue_address="501 Napoleon Ave",
                venue_city="New Orleans",
                venue_state="LA",
                venue_postal_code="70115",
                venue_latitude=29.9189,
                venue_longitude=-90.1009,
                title="Preservation Brass All-Stars",
                description="Legendary Uptown music hall hosting New Orleans classic street beats and brass melodies.",
                category="music",
                start_time=t_today_7pm.isoformat(),
                end_time=(t_today_7pm + timedelta(hours=2, minutes=30)).isoformat(),
                price_min=20.00,
                price_max=35.00,
                currency="USD",
                image_url="https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&auto=format&fit=crop&q=80",
                ticket_url="https://www.tipitinas.com",
                is_featured=0,
            ),
            RawEvent(
                source="mock",
                source_event_id="mock-tipitinas-galactic",
                venue_name="Tipitina's",
                venue_address="501 Napoleon Ave",
                venue_city="New Orleans",
                venue_state="LA",
                venue_postal_code="70115",
                venue_latitude=29.9189,
                venue_longitude=-90.1009,
                title="Galactic featuring Anjelika Jelly Joseph",
                description="New Orleans funk royalty returns to their home venue for a high-voltage throwdown.",
                category="music",
                start_time=t_today_9pm.isoformat(),
                end_time=(t_today_9pm + timedelta(hours=3)).isoformat(),
                price_min=30.00,
                price_max=50.00,
                currency="USD",
                image_url="https://images.unsplash.com/photo-1520523839898-507129cd14f1?w=800&auto=format&fit=crop&q=80",
                ticket_url="https://www.tipitinas.com",
                is_featured=1,
            ),
            # Smoothie King Center - NBA Basketball
            RawEvent(
                source="mock",
                source_event_id="mock-pelicans-warriors",
                venue_name="Smoothie King Center",
                venue_address="1501 Dave Dixon Dr",
                venue_city="New Orleans",
                venue_state="LA",
                venue_postal_code="70113",
                venue_latitude=29.9490,
                venue_longitude=-90.0821,
                title="New Orleans Pelicans vs Golden State Warriors",
                description="Western Conference NBA action. Zion Williamson and the Pelicans host Golden State.",
                category="sports",
                start_time=t_tom_7pm.isoformat(),
                end_time=(t_tom_7pm + timedelta(hours=2, minutes=30)).isoformat(),
                price_min=38.00,
                price_max=320.00,
                currency="USD",
                image_url="https://images.unsplash.com/photo-1504450758481-7338eba7524a?w=800&auto=format&fit=crop&q=80",
                ticket_url="https://www.seatgeek.com",
                is_featured=1,
            ),
            # Joy Theater - Standup Comedy
            RawEvent(
                source="mock",
                source_event_id="mock-joy-comedy-night",
                venue_name="The Joy Theater",
                venue_address="1200 Canal St",
                venue_city="New Orleans",
                venue_state="LA",
                venue_postal_code="70112",
                venue_latitude=29.9567,
                venue_longitude=-90.0736,
                title="Canal Street Standup Spectacular",
                description="National touring comedians featured on Netflix and Comedy Central perform live.",
                category="comedy",
                start_time=t_in2_8pm.isoformat(),
                end_time=(t_in2_8pm + timedelta(hours=2)).isoformat(),
                price_min=25.00,
                price_max=45.00,
                currency="USD",
                image_url="https://images.unsplash.com/photo-1585699324551-f6c309eedeca?w=800&auto=format&fit=crop&q=80",
                ticket_url="https://www.thejoytheater.com",
                is_featured=0,
            ),
        ]

        return mock_raw_data
