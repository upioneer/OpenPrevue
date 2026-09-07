"""YouTube metadata resolution and embed validation API."""

import re
import httpx
from fastapi import APIRouter, Query
from pydantic import BaseModel
from backend.app.core.logging import logger

router = APIRouter(prefix="/youtube")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


class YouTubeValidationResponse(BaseModel):
    """Normalized validation and telemetry payload for YouTube streams."""
    valid: bool
    source_type: str | None = None
    resource_id: str | None = None
    title: str | None = None
    author_name: str | None = None
    thumbnail_url: str | None = None
    embed_url: str | None = None
    error: str | None = None


def parse_youtube_resource(raw_input: str) -> tuple[str, str]:
    """Extract source type ('playlist' | 'video' | 'unknown') and clean resource ID."""
    clean = raw_input.strip()

    # 1. Check for playlist query parameter (including watch?v=...&list=PL...)
    match_list = re.search(r"[?&]list=([a-zA-Z0-9_-]+)", clean)
    if match_list:
        return "playlist", match_list.group(1)

    # 2. Check for raw playlist ID (typically starts with PL, UU, FL, RD, OLAK)
    if re.match(r"^(PL|UU|FL|RD|OLAK)[a-zA-Z0-9_-]+$", clean, re.IGNORECASE):
        return "playlist", clean

    # 3. Check for single video URL formats
    match_video = re.search(r"(?:v=|\/embed\/|\/shorts\/|youtu\.be\/)([a-zA-Z0-9_-]{11})", clean)
    if match_video:
        return "video", match_video.group(1)

    # 4. Check for raw 11-character video ID
    if re.match(r"^[a-zA-Z0-9_-]{11}$", clean):
        return "video", clean

    return "unknown", clean


@router.get("/validate", response_model=YouTubeValidationResponse)
async def validate_youtube_source(url: str = Query(..., description="YouTube playlist URL, video URL, or resource ID")) -> YouTubeValidationResponse:
    """Validate a YouTube playlist or video URL and check embed availability before saving."""
    source_type, resource_id = parse_youtube_resource(url)

    if source_type == "unknown":
        return YouTubeValidationResponse(
            valid=False,
            source_type="unknown",
            resource_id=resource_id,
            error="Invalid YouTube URL or ID format. Provide a playlist URL or video link.",
        )

    # Validate Playlist
    if source_type == "playlist":
        playlist_url = f"https://www.youtube.com/playlist?list={resource_id}"
        embed_url = f"https://www.youtube-nocookie.com/embed/videoseries?list={resource_id}"
        try:
            async with httpx.AsyncClient(timeout=5.0, headers={"User-Agent": USER_AGENT}) as client:
                res = await client.get(playlist_url, follow_redirects=True)
                if res.status_code == 200:
                    title_match = re.search(r"<title>(.*?)(?: - YouTube)?</title>", res.text, re.IGNORECASE)
                    title = title_match.group(1).replace(" - YouTube", "").strip() if title_match else "YouTube Playlist"
                    if "404 Not Found" in title or "This playlist is private" in title:
                        return YouTubeValidationResponse(
                            valid=False,
                            source_type="playlist",
                            resource_id=resource_id,
                            error="Playlist is private or does not exist on YouTube.",
                        )
                    return YouTubeValidationResponse(
                        valid=True,
                        source_type="playlist",
                        resource_id=resource_id,
                        title=title,
                        embed_url=embed_url,
                    )
                return YouTubeValidationResponse(
                    valid=False,
                    source_type="playlist",
                    resource_id=resource_id,
                    error=f"Playlist returned HTTP {res.status_code}. It may be deleted or private.",
                )
        except Exception as exc:
            logger.debug("YouTube playlist validation error: %s", exc)
            return YouTubeValidationResponse(
                valid=False,
                source_type="playlist",
                resource_id=resource_id,
                error="Network timeout or unreachable YouTube host.",
            )

    # Validate Video via official oEmbed endpoint
    video_url = f"https://www.youtube.com/watch?v={resource_id}"
    embed_url = f"https://www.youtube-nocookie.com/embed/{resource_id}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(
                "https://www.youtube.com/oembed",
                params={"url": video_url, "format": "json"},
            )
            if res.status_code == 200:
                data = res.json()
                return YouTubeValidationResponse(
                    valid=True,
                    source_type="video",
                    resource_id=resource_id,
                    title=data.get("title") or "YouTube Video",
                    author_name=data.get("author_name"),
                    thumbnail_url=data.get("thumbnail_url"),
                    embed_url=embed_url,
                )
            if res.status_code in (401, 403):
                return YouTubeValidationResponse(
                    valid=False,
                    source_type="video",
                    resource_id=resource_id,
                    error="Embedding has been disabled by the video owner on YouTube.",
                )
            return YouTubeValidationResponse(
                valid=False,
                source_type="video",
                resource_id=resource_id,
                error="Video is unavailable, deleted, or marked private.",
            )
    except Exception as exc:
        logger.debug("YouTube video validation error: %s", exc)
        return YouTubeValidationResponse(
            valid=False,
            source_type="video",
            resource_id=resource_id,
            error="Network timeout verifying YouTube video.",
        )
