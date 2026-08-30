"""Unit tests for iCal (.ics) calendar feed parser."""

from backend.app.providers.ical import ICalEventProvider, parse_ical_datetime

SAMPLE_ICS = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//OpenPrevue Test//EN
BEGIN:VEVENT
UID:uid-12345@example.com
DTSTAMP:20260830T000000Z
DTSTART:20260920T193000Z
DTEND:20260920T220000Z
SUMMARY:Louisiana Philharmonic Orchestra
DESCRIPTION:Masterworks series featuring Beethoven Symphony No. 9
LOCATION:Orpheum Theater, 129 Roosevelt Way, New Orleans, LA
URL:https://www.orpheumnola.com
END:VEVENT
END:VCALENDAR
"""


def test_parse_ical_datetime():
    """Verify ISO conversion of iCal timestamp formats."""
    assert parse_ical_datetime("20260920T193000Z") == "2026-09-20T19:30:00+00:00"
    assert parse_ical_datetime("20260920") == "2026-09-20T00:00:00"
    assert parse_ical_datetime("invalid") is None


def test_parse_ics_text():
    """Verify parsing RFC 5545 calendar stream."""
    provider = ICalEventProvider()
    events = provider.parse_ics_text(SAMPLE_ICS, source_url="https://www.orpheumnola.com/events.ics")

    assert len(events) == 1
    evt = events[0]
    assert evt.title == "Louisiana Philharmonic Orchestra"
    assert "Orpheum Theater" in evt.venue_name
    assert evt.category == "music"
    assert evt.start_time == "2026-09-20T19:30:00+00:00"
    assert evt.ticket_url == "https://www.orpheumnola.com"
