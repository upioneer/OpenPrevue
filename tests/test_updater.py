"""Unit and integration tests for the update tracking and notification system."""

import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app
from backend.app.services.updater import is_newer_version, parse_semver, update_service


def test_parse_semver():
    """Verify semantic version string parsing."""
    assert parse_semver("0.15.0") == (0, 15, 0)
    assert parse_semver("v0.15.0") == (0, 15, 0)
    assert parse_semver("v1.2.3-beta") == (1, 2, 3)
    assert parse_semver("invalid") == (0, 0, 0)


def test_is_newer_version():
    """Verify version comparison truth table."""
    assert is_newer_version("0.14.0", "0.15.0") is True
    assert is_newer_version("0.15.0", "0.15.1") is True
    assert is_newer_version("0.15.0", "1.0.0") is True
    assert is_newer_version("0.15.0", "0.15.0") is False
    assert is_newer_version("0.15.1", "0.15.0") is False
    assert is_newer_version("1.0.0", "0.15.0") is False


@pytest.mark.asyncio
async def test_update_service_status():
    """Verify update service returns valid status object."""
    status = await update_service.get_status()
    assert "current_version" in status
    assert "latest_version" in status
    assert "update_available" in status
    assert "update_check_interval" in status
    assert "is_rate_limited" in status
    assert isinstance(status["update_available"], bool)


@pytest.mark.asyncio
async def test_updates_api_endpoints():
    """Verify updates REST endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # GET /api/v1/updates/status
        res = await client.get("/api/v1/updates/status")
        assert res.status_code == 200
        data = res.json()
        assert "current_version" in data
        assert "latest_version" in data
        assert "update_available" in data
        assert "update_check_interval" in data

        # POST /api/v1/updates/check
        res_check = await client.post("/api/v1/updates/check")
        assert res_check.status_code == 200
        check_data = res_check.json()
        assert "current_version" in check_data
        assert "update_available" in check_data


@pytest.mark.asyncio
async def test_rate_limit_plain_english_state():
    """Verify rate limit plain English messaging is friendly and non-technical."""
    update_service.is_rate_limited = True
    update_service.rate_limit_reset_minutes = 42
    update_service.user_message = (
        "You have checked for updates too many times recently. "
        "GitHub has paused requests for a bit. Please wait about 42 minutes before checking again."
    )
    status = await update_service.get_status()
    assert status["is_rate_limited"] is True
    assert "42 minutes" in status["user_message"]
    assert "too many times" in status["user_message"]
    # Restore clean state
    update_service.is_rate_limited = False
    update_service.user_message = None
