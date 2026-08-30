"""Test health and observability endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Verify health check returns status 200 and expected keys."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("healthy", "degraded")
        assert data["database"] == "ok"
        assert "mock" in data["providers"]


@pytest.mark.asyncio
async def test_spa_root_serves_html():
    """Verify root endpoint serves frontend SPA when dist is built."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert "OpenPrevue" in response.text
