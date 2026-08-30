"""Unit tests for Telegram bot message formatters, handlers, and REST API endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app
from backend.app.db.session import init_db
from backend.app.services.telegram.formatters import (
    format_bulletin,
    format_error_box,
    format_help_menu,
    format_pairing_success,
    format_status_card,
    format_watchlist,
)


@pytest.fixture(autouse=True)
async def setup_database():
    """Initialize database before tests."""
    await init_db()


def test_format_bulletin():
    """Verify monospaced bulletin formatting."""
    sample_events = [
        {
            "title": "Preservation Hall Jazz Band",
            "venue_name": "Preservation Hall",
            "category": "music",
            "start_time": "2026-09-01T20:00:00Z",
            "price_min": 25.0,
            "price_max": 35.0,
            "has_ticket": 1,
        }
    ]
    card = format_bulletin("TODAY'S SCHEDULE", sample_events, "NEW ORLEANS")
    assert "OPENPREVUE EVENT GUIDE" in card
    assert "Preservation Hall" in card
    assert "[TKT]" in card
    assert "```" in card


def test_format_error_box():
    """Verify boxed error message structure."""
    card = format_error_box("MISSING SEARCH QUERY", "Specify artist or venue", "/search Saints")
    assert "ERROR: MISSING SEARCH QUERY" in card
    assert "USAGE: /search Saints" in card
    assert "Send /help" in card


def test_format_help_menu():
    """Verify complete help directory."""
    card = format_help_menu()
    assert "/today" in card
    assert "/tonight" in card
    assert "/weekend" in card
    assert "/search" in card
    assert "/pin" in card
    assert "/watch" in card
    assert "/pair" in card


def test_format_pairing_success():
    """Verify pairing confirmation card."""
    card = format_pairing_success("TestUser", 12345678)
    assert "DEVICE PAIRING SUCCESSFUL" in card
    assert "TestUser" in card
    assert "12345678" in card


def test_format_status_card():
    """Verify system telemetry card."""
    stats = {
        "status": "OPERATIONAL",
        "metro_label": "NEW ORLEANS",
        "radius_miles": "35",
        "active_events": 42,
        "last_sync": "SUCCESS (2026-08-30)",
        "weather": "74F CLEAR SKY",
    }
    card = format_status_card(stats)
    assert "OPERATIONAL" in card
    assert "NEW ORLEANS" in card
    assert "42" in card


def test_format_watchlist():
    """Verify active watchlist formatting."""
    card = format_watchlist(["Saints", "Preservation Hall"])
    assert "ACTIVE WATCHLIST KEYWORDS" in card
    assert "1. Saints" in card
    assert "2. Preservation Hall" in card


@pytest.mark.asyncio
async def test_telegram_api_endpoints():
    """Verify Telegram pairing code generation and status endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Generate pairing code
        pair_res = await client.post("/api/v1/telegram/pair-code")
        assert pair_res.status_code == 200
        pair_data = pair_res.json()
        assert "pair_code" in pair_data
        assert pair_data["pair_code"].startswith("PREVUE-")

        # Check status endpoint
        status_res = await client.get("/api/v1/telegram/status")
        assert status_res.status_code == 200
        status_data = status_res.json()
        assert "is_configured" in status_data
        assert "is_running" in status_data

        # List paired users
        users_res = await client.get("/api/v1/telegram/users")
        assert users_res.status_code == 200
        assert isinstance(users_res.json(), list)
