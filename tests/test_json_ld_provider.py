"""Unit tests for JSON-LD schema.org calendar extractor."""

from backend.app.providers.json_ld import JsonLdEventProvider, map_schema_event_category

SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "MusicEvent",
      "name": "Preservation Hall Jazz Night",
      "startDate": "2026-09-15T20:00:00-05:00",
      "endDate": "2026-09-15T22:30:00-05:00",
      "location": {
        "@type": "Place",
        "name": "Preservation Hall",
        "address": {
          "@type": "PostalAddress",
          "streetAddress": "726 St Peter St",
          "addressLocality": "New Orleans",
          "addressRegion": "LA",
          "postalCode": "70116"
        },
        "geo": {
          "@type": "GeoCoordinates",
          "latitude": 29.9584,
          "longitude": -90.0654
        }
      },
      "offers": {
        "@type": "Offer",
        "url": "https://www.preservationhall.com/tickets",
        "price": "25.00",
        "priceCurrency": "USD"
      },
      "image": "https://www.preservationhall.com/poster.jpg",
      "description": "Historic acoustic jazz session."
    }
    </script>
</head>
<body><h1>Preservation Hall Events</h1></body>
</html>
"""


def test_map_schema_event_category():
    """Verify schema event category inference."""
    assert map_schema_event_category("MusicEvent") == "music"
    assert map_schema_event_category("SportsEvent") == "sports"
    assert map_schema_event_category("TheaterEvent") == "theater"
    assert map_schema_event_category("ComedyEvent") == "comedy"
    assert map_schema_event_category("Event", "Band") == "music"


def test_parse_html_json_ld():
    """Verify parsing inline JSON-LD script tags."""
    provider = JsonLdEventProvider()
    events = provider.parse_html_json_ld(SAMPLE_HTML, source_url="https://www.preservationhall.com")

    assert len(events) == 1
    evt = events[0]
    assert evt.title == "Preservation Hall Jazz Night"
    assert evt.venue_name == "Preservation Hall"
    assert evt.venue_city == "New Orleans"
    assert evt.venue_latitude == 29.9584
    assert evt.price_min == 25.0
    assert evt.category == "music"
    assert evt.ticket_url == "https://www.preservationhall.com/tickets"
