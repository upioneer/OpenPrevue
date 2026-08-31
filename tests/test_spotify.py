"""Tests for dynamic Spotify metadata resolution endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app


@pytest.mark.asyncio
async def test_get_spotify_metadata_endpoint():
    """Verify GET /api/v1/spotify/metadata returns valid playlist details."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/spotify/metadata?url=https://open.spotify.com/playlist/3jiPmIT4RugR8TPhli5Obk")
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert data["title"] == "OpenPrevue"
        assert "playlist_url" in data
        assert "3jiPmIT4RugR8TPhli5Obk" in data["playlist_url"]


@pytest.mark.asyncio
async def test_get_spotify_metadata_default():
    """Verify default query without parameters retrieves settings playlist."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/spotify/metadata")
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert len(data["title"]) > 0
