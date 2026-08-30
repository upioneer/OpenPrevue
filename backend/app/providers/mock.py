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
        tz = ZoneInfo("America/New_York")
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
            # Madison Square Garden - Featured NBA
            RawEvent(
                source="mock",
                source_event_id="mock-msg-knicks-celtics",
                venue_name="Madison Square Garden",
                venue_address="4 Pennsylvania Plaza",
                venue_city="New York",
                venue_state="NY",
                venue_postal_code="10001",
                venue_latitude=40.7505,
                venue_longitude=-73.9934,
                title="NBA: New York Knicks vs Boston Celtics",
                description="Eastern Conference rivalry showdown at the World's Most Famous Arena.",
                category="sports",
                start_time=t_sun_12pm.isoformat(),
                end_time=(t_sun_12pm + timedelta(hours=3, minutes=30)).isoformat(),
                price_min=85.00,
                price_max=450.00,
                currency="USD",
                image_url="https://images.unsplash.com/photo-1504450758481-7338eba7524a?w=800&auto=format&fit=crop&q=80",
                ticket_url="https://www.ticketmaster.com",
                is_featured=1,
            ),
            # Radio City Music Hall - Featured Concert
            RawEvent(
                source="mock",
                source_event_id="mock-rcmh-concert",
                venue_name="Radio City Music Hall",
                venue_address="1260 6th Ave",
                venue_city="New York",
                venue_state="NY",
                venue_postal_code="10020",
                venue_latitude=40.7599,
                venue_longitude=-73.9799,
                title="Khruangbin: A La Sala World Tour",
                description="Psychedelic dub-funk trio performing live on 6th Avenue in Manhattan.",
                category="music",
                start_time=t_today_8pm.isoformat(),
                end_time=(t_today_8pm + timedelta(hours=3)).isoformat(),
                price_min=65.00,
                price_max=165.00,
                currency="USD",
                image_url="https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&auto=format&fit=crop&q=80",
                ticket_url="https://www.radiocity.com",
                is_featured=1,
            ),
            # Brooklyn Steel - Indie Live Performance
            RawEvent(
                source="mock",
                source_event_id="mock-bk-steel-show",
                venue_name="Brooklyn Steel",
                venue_address="319 Frost St",
                venue_city="Brooklyn",
                venue_state="NY",
                venue_postal_code="11222",
                venue_latitude=40.7193,
                venue_longitude=-73.9388,
                title="Japanese Breakfast: Live in Williamsburg",
                description="Acclaimed indie pop performance featuring full orchestral arrangements.",
                category="music",
                start_time=t_today_9pm.isoformat(),
                end_time=(t_today_9pm + timedelta(hours=3)).isoformat(),
                price_min=35.00,
                price_max=75.00,
                currency="USD",
                image_url="https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&auto=format&fit=crop&q=80",
                ticket_url="https://www.bowerypresents.com",
                is_featured=1,
            ),
            # Beacon Theatre - Broadway & Acoustic Series
            RawEvent(
                source="mock",
                source_event_id="mock-beacon-acoustic",
                venue_name="Beacon Theatre",
                venue_address="2124 Broadway",
                venue_city="New York",
                venue_state="NY",
                venue_postal_code="10023",
                venue_latitude=40.7806,
                venue_longitude=-73.9813,
                title="Trey Anastasio: Solo Acoustic Residency",
                description="Intimate evening of acoustic storytelling and guitar work on the Upper West Side.",
                category="music",
                start_time=t_tom_8pm.isoformat(),
                end_time=(t_tom_8pm + timedelta(hours=3)).isoformat(),
                price_min=55.00,
                price_max=140.00,
                currency="USD",
                image_url="https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800&auto=format&fit=crop&q=80",
                ticket_url="https://www.beacontheatre.com",
                is_featured=0,
            ),
            # Gershwin Theatre - Wicked Broadway
            RawEvent(
                source="mock",
                source_event_id="mock-gershwin-wicked-matinee",
                venue_name="Gershwin Theatre",
                venue_address="222 W 51st St",
                venue_city="New York",
                venue_state="NY",
                venue_postal_code="10019",
                venue_latitude=40.7624,
                venue_longitude=-73.9851,
                title="Wicked: Broadway Landmark Musical (Matinee)",
                description="The untold true story of the Witches of Oz live in Times Square.",
                category="theater",
                start_time=t_today_2pm.isoformat(),
                end_time=(t_today_2pm + timedelta(hours=2, minutes=45)).isoformat(),
                price_min=79.00,
                price_max=245.00,
                currency="USD",
                image_url="https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?w=800&auto=format&fit=crop&q=80",
                ticket_url="https://www.wickedthemusical.com",
                is_featured=0,
            ),
            RawEvent(
                source="mock",
                source_event_id="mock-gershwin-wicked-evening",
                venue_name="Gershwin Theatre",
                venue_address="222 W 51st St",
                venue_city="New York",
                venue_state="NY",
                venue_postal_code="10019",
                venue_latitude=40.7624,
                venue_longitude=-73.9851,
                title="Wicked: Broadway Landmark Musical (Evening)",
                description="The untold true story of the Witches of Oz live in Times Square.",
                category="theater",
                start_time=t_today_8pm.isoformat(),
                end_time=(t_today_8pm + timedelta(hours=2, minutes=45)).isoformat(),
                price_min=89.00,
                price_max=295.00,
                currency="USD",
                image_url="https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?w=800&auto=format&fit=crop&q=80",
                ticket_url="https://www.wickedthemusical.com",
                is_featured=1,
            ),
            # Blue Note Jazz Club - Late Night Sessions
            RawEvent(
                source="mock",
                source_event_id="mock-bluenote-session",
                venue_name="Blue Note Jazz Club",
                venue_address="131 W 3rd St",
                venue_city="New York",
                venue_state="NY",
                venue_postal_code="10012",
                venue_latitude=40.7308,
                venue_longitude=-74.0006,
                title="Ron Carter Quintet: Greenwich Village Sets",
                description="Legendary jazz bassist performing acoustic sets in Greenwich Village.",
                category="music",
                start_time=t_today_7pm.isoformat(),
                end_time=(t_today_7pm + timedelta(hours=2, minutes=30)).isoformat(),
                price_min=30.00,
                price_max=55.00,
                currency="USD",
                image_url="https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=800&auto=format&fit=crop&q=80",
                ticket_url="https://www.bluenotejazz.com",
                is_featured=0,
            ),
            # Comedy Cellar - MacDougal Street Showcase
            RawEvent(
                source="mock",
                source_event_id="mock-comedy-cellar",
                venue_name="Comedy Cellar",
                venue_address="117 MacDougal St",
                venue_city="New York",
                venue_state="NY",
                venue_postal_code="10012",
                venue_latitude=40.7300,
                venue_longitude=-74.0002,
                title="MacDougal Street Standup Showcase",
                description="Top national headliners as seen on Netflix, HBO, and late night television.",
                category="comedy",
                start_time=t_in2_8pm.isoformat(),
                end_time=(t_in2_8pm + timedelta(hours=2)).isoformat(),
                price_min=25.00,
                price_max=35.00,
                currency="USD",
                image_url="https://images.unsplash.com/photo-1585699324551-f6c309eedeca?w=800&auto=format&fit=crop&q=80",
                ticket_url="https://www.comedycellar.com",
                is_featured=0,
            ),
        ]

        return mock_raw_data
