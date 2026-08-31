"""Unit tests for native Viator Partner API ingestion adapter."""

import pytest
from backend.app.providers.base import GeoPoint
from backend.app.providers.viator import ViatorPartnerProvider


MOCK_VIATOR_PRODUCTS = [
    {
        "productCode": "12345P1",
        "title": "New Orleans Ghosts & Voodoo Night Walking Tour",
        "description": "Explore the spooky history of the French Quarter on a guided walking tour.",
        "productUrl": "https://www.viator.com/tours/New-Orleans/Ghost-Tour/d675-12345P1",
        "pricing": {
            "currency": "USD",
            "summary": {
                "fromPrice": 29.99
            }
        },
        "images": [
            {
                "variants": [
                    {"url": "https://media.tacdn.com/media/small.jpg"},
                    {"url": "https://media.tacdn.com/media/large.jpg"}
                ]
            }
        ]
    }
]


@pytest.mark.asyncio
async def test_viator_provider_skips_when_no_api_key():
    provider = ViatorPartnerProvider(api_key="")
    events = await provider.fetch_events(GeoPoint(latitude=29.9511, longitude=-90.0715), 25.0)
    assert events == []


def test_viator_product_parsing():
    provider = ViatorPartnerProvider(api_key="test_key_123")
    location = GeoPoint(latitude=29.9511, longitude=-90.0715)
    events = provider._parse_products(MOCK_VIATOR_PRODUCTS, location)

    assert len(events) == 1
    evt = events[0]
    assert evt.source == "viator"
    assert evt.source_event_id == "viator_12345P1"
    assert "Ghosts & Voodoo" in evt.title
    assert evt.price_min == 29.99
    assert evt.image_url == "https://media.tacdn.com/media/large.jpg"
    assert evt.is_featured == 1
