"""Unit and integration tests for update tracking, capabilities, and in-place engine."""

import json
from pathlib import Path
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.core.config import settings
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
async def test_update_service_capability():
    """Verify runtime update engine capability detection."""
    cap = await update_service.get_update_capability()
    assert "can_update" in cap
    assert "detected_method" in cap
    assert "available_methods" in cap
    assert "trigger_file_path" in cap
    assert "current_version" in cap
    assert isinstance(cap["available_methods"], list)
    assert len(cap["available_methods"]) >= 1


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

        # GET /api/v1/updates/capability
        res_cap = await client.get("/api/v1/updates/capability")
        assert res_cap.status_code == 200
        cap_data = res_cap.json()
        assert "detected_method" in cap_data
        assert "available_methods" in cap_data
        assert "can_update" in cap_data

        # POST /api/v1/updates/apply (Dry Run)
        res_apply = await client.post(
            "/api/v1/updates/apply",
            json={"target_version": "0.22.0", "dry_run": True, "method": "trigger_file"},
        )
        assert res_apply.status_code == 200
        apply_data = res_apply.json()
        assert apply_data["status"] == "dry_run_success"
        assert apply_data["method"] == "trigger_file"
        assert "steps" in apply_data
        assert len(apply_data["steps"]) > 0


@pytest.mark.asyncio
async def test_apply_trigger_file_execution():
    """Verify writing trigger file writes correct JSON payload to disk."""
    trigger_path = Path(settings.DATA_DIR) / ".update_trigger"
    if trigger_path.exists():
        trigger_path.unlink()

    res = await update_service.apply_update(
        target_version="0.22.0",
        dry_run=False,
        method="trigger_file",
    )
    assert res["status"] == "triggered"
    assert res["method"] == "trigger_file"
    assert trigger_path.exists()

    content = json.loads(trigger_path.read_text(encoding="utf-8"))
    assert content["target_version"] == "0.22.0"
    assert content["action"] == "upgrade"
    assert "ghcr.io/upioneer/OpenPrevue:v0.22.0" in content["image"]

    # Clean up test artifact
    trigger_path.unlink()


@pytest.mark.asyncio
async def test_apply_docker_socket_dry_run():
    """Verify Docker socket dry run step generation."""
    res = await update_service.apply_update(
        target_version="0.22.0",
        dry_run=True,
        method="docker_socket",
    )
    assert res["status"] == "dry_run_success"
    assert res["method"] == "docker_socket"
    assert any("Docker" in s for s in res["steps"])


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


@pytest.mark.asyncio
async def test_check_for_updates_with_tags(monkeypatch):
    """Verify check_for_updates parses Git tags as canonical source of truth."""
    import httpx

    simulated_tags = [
        {"name": "v0.22.1", "commit": {"sha": "123"}},
        {"name": "v0.22.0", "commit": {"sha": "456"}},
        {"name": "v0.21.0", "commit": {"sha": "789"}},
    ]

    class MockResponse:
        def __init__(self, url, status_code=200, json_data=None):
            self.url = str(url)
            self.status_code = status_code
            self._json_data = json_data or []
            self.headers = {"x-ratelimit-remaining": "59", "x-ratelimit-reset": "1800000000"}

        def json(self):
            return self._json_data

    async def mock_get(client_self, url, headers=None):
        url_str = str(url)
        if "/tags" in url_str:
            return MockResponse(url, status_code=200, json_data=simulated_tags)
        if "/releases/tags/" in url_str:
            return MockResponse(url, status_code=404, json_data={})
        return MockResponse(url, status_code=404)

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    # When running 0.22.0, newer tag 0.22.1 must trigger update_available = True
    update_service.current_version = "0.22.0"
    status_update = await update_service.check_for_updates(force=True)
    assert status_update["latest_version"] == "0.22.1"
    assert status_update["update_available"] is True
    assert "v0.22.1" in status_update["user_message"]

    # When running 0.22.1, update_available must be False
    update_service.current_version = "0.22.1"
    status_current = await update_service.check_for_updates(force=True)
    assert status_current["latest_version"] == "0.22.1"
    assert status_current["update_available"] is False
    assert "newest version" in status_current["user_message"]
