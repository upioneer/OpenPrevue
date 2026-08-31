"""Unit tests for TripAdvisor and Viator travel wishlist ingestion provider."""

import pytest
from backend.app.providers.base import GeoPoint
from backend.app.providers.travel_wishlist import TravelWishlistProvider, map_travel_category


TRIPADVISOR_MOCK_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Top 10 Things to Do in Austin - Tripadvisor</title>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "TouristTrip",
        "name": "Austin Live Music and Brewery Crawl",
        "description": "Guided evening tour of legendary Austin music venues and craft breweries.",
        "startDate": "2026-09-01T19:00:00Z",
        "location": {
            "@type": "Place",
            "name": "Rainey Street Historic District",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "Austin",
                "addressRegion": "TX"
            },
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": "30.2672",
                "longitude": "-97.7431"
            }
        },
        "offers": {
            "@type": "Offer",
            "price": "65.00",
            "priceCurrency": "USD"
        },
        "image": "https://media-cdn.tripadvisor.com/media/photo-s/austin_music.jpg",
        "url": "https://www.tripadvisor.com/Attraction_Review-austin-crawl.html"
    }
    </script>
</head>
<body>
    <h1>Austin Live Music and Brewery Crawl</h1>
</body>
</html>
"""

VIATOR_MOCK_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>French Quarter Historical Food Tour | Viator</title>
    <meta property="og:title" content="French Quarter Historical Food Tour | Viator" />
    <meta property="og:description" content="Sample authentic gumbo, beignets, and pralines for only $75.00 per person." />
    <meta property="og:image" content="https://media.tacdn.com/media/attractions-splice-spp-674x446/french_quarter.jpg" />
</head>
<body>
    <h1>French Quarter Historical Food Tour</h1>
</body>
</html>
"""


def test_map_travel_category():
    assert map_travel_category("Austin Jazz & Blues Fest", "Live jazz concert") == "music"
    assert map_travel_category("Knicks vs Celtics", "NBA game at arena") == "sports"
    assert map_travel_category("Broadway Musical", "Award winning theater performance") == "theater"
    assert map_travel_category("Stand Up Comedy Show", "Late night comedy club") == "comedy"
    assert map_travel_category("French Quarter Food Tour", "Culinary tasting tour") == "community"


def test_parse_tripadvisor_json_ld():
    provider = TravelWishlistProvider(target_urls=["https://www.tripadvisor.com/Trips/12345"])
    events = provider.parse_html_page(TRIPADVISOR_MOCK_HTML, "https://www.tripadvisor.com/Trips/12345")

    assert len(events) == 1
    evt = events[0]
    assert evt.source == "tripadvisor"
    assert "Austin Live Music and Brewery Crawl" in evt.title
    assert evt.venue_name == "Rainey Street Historic District"
    assert evt.venue_city == "Austin"
    assert evt.venue_state == "TX"
    assert evt.venue_latitude == 30.2672
    assert evt.price_min == 65.00
    assert evt.is_featured == 1


def test_parse_viator_opengraph_fallback():
    provider = TravelWishlistProvider(target_urls=["https://www.viator.com/tours/new-orleans/food-tour"])
    events = provider.parse_html_page(VIATOR_MOCK_HTML, "https://www.viator.com/tours/new-orleans/food-tour")

    assert len(events) == 1
    evt = events[0]
    assert evt.source == "viator"
    assert "French Quarter Historical Food Tour" in evt.title
    assert evt.price_min == 75.00
    assert evt.is_featured == 1
    assert evt.image_url is not None
