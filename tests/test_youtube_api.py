"""Tests for YouTube validation endpoint and URL parsing."""

import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app
from backend.app.api.v1.endpoints.youtube import parse_youtube_resource


def test_parse_youtube_resource_playlists():
    """Verify regex identification of playlists."""
    assert parse_youtube_resource("https://www.youtube.com/playlist?list=PLrEnWoR732-BHrPp_QLgkMnOw74vTtPrK") == (
        "playlist",
        "PLrEnWoR732-BHrPp_QLgkMnOw74vTtPrK",
    )
    assert parse_youtube_resource("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PL123456789") == (
        "playlist",
        "PL123456789",
    )
    assert parse_youtube_resource("PLrEnWoR732-BHrPp_QLgkMnOw74vTtPrK") == (
        "playlist",
        "PLrEnWoR732-BHrPp_QLgkMnOw74vTtPrK",
    )


def test_parse_youtube_resource_videos():
    """Verify regex identification of single video and live stream resources."""
    assert parse_youtube_resource("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == (
        "video",
        "dQw4w9WgXcQ",
    )
    assert parse_youtube_resource("https://youtu.be/dQw4w9WgXcQ") == (
        "video",
        "dQw4w9WgXcQ",
    )
    assert parse_youtube_resource("https://www.youtube.com/embed/dQw4w9WgXcQ") == (
        "video",
        "dQw4w9WgXcQ",
    )
    assert parse_youtube_resource("https://www.youtube.com/live/dQw4w9WgXcQ") == (
        "video",
        "dQw4w9WgXcQ",
    )
    assert parse_youtube_resource("dQw4w9WgXcQ") == (
        "video",
        "dQw4w9WgXcQ",
    )


def test_parse_youtube_resource_unknown():
    """Verify non-YouTube input returns unknown."""
    assert parse_youtube_resource("https://vimeo.com/123456") == ("unknown", "https://vimeo.com/123456")
    assert parse_youtube_resource("just-some-random-text") == ("unknown", "just-some-random-text")


@pytest.mark.asyncio
async def test_validate_youtube_invalid_url():
    """Verify validation response when an unparseable URL is provided."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/youtube/validate", params={"url": "not-a-real-url"})
        assert res.status_code == 200
        data = res.json()
        assert data["valid"] is False
        assert data["source_type"] == "unknown"
        assert "Invalid YouTube URL" in data["error"]


@pytest.mark.asyncio
async def test_validate_youtube_real_video():
    """Verify live oEmbed validation on a stable public video."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/youtube/validate", params={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
        assert res.status_code == 200
        data = res.json()
        assert data["valid"] is True
        assert data["source_type"] == "video"
        assert data["resource_id"] == "dQw4w9WgXcQ"
        assert "Rick" in data["title"]
