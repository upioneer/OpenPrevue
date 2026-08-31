"""Spotify metadata resolution via official Spotify oEmbed API."""

import httpx
from fastapi import APIRouter, Query
from pydantic import BaseModel
from backend.app.core.logging import logger
from backend.app.db.session import get_db

router = APIRouter(prefix="/spotify")

DEFAULT_SPOTIFY_PLAYLIST_URL = "https://open.spotify.com/playlist/3jiPmIT4RugR8TPhli5Obk"


class SpotifyMetadataResponse(BaseModel):
    """Normalized metadata fetched dynamically from Spotify."""
    title: str
    author_name: str | None = None
    thumbnail_url: str | None = None
    embed_url: str | None = None
    playlist_url: str
    provider: str = "Spotify"


@router.get("/metadata", response_model=SpotifyMetadataResponse)
async def get_spotify_metadata(url: str | None = Query(default=None, description="Spotify playlist or album URL")) -> SpotifyMetadataResponse:
    """Fetch live playlist title, author, and embed details dynamically from Spotify oEmbed API."""
    target_url = url.strip() if url and url.strip() else None

    if not target_url:
        try:
            async with get_db() as db:
                async with db.execute("SELECT value FROM settings WHERE key = 'spotify_playlist_url'") as cursor:
                    row = await cursor.fetchone()
                    if row and row["value"]:
                        target_url = row["value"]
        except Exception as e:
            logger.debug("Failed retrieving spotify_playlist_url from DB: %s", e)

    if not target_url:
        target_url = DEFAULT_SPOTIFY_PLAYLIST_URL

    clean_url = target_url.split("?")[0]

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            res = await client.get(
                "https://open.spotify.com/oembed",
                params={"url": clean_url},
            )
            if res.status_code == 200:
                data = res.json()
                title = data.get("title") or "OpenPrevue"
                author = data.get("author_name")
                if not author and "3jiPmIT4RugR8TPhli5Obk" in clean_url:
                    author = "upioneer"

                thumbnail = data.get("thumbnail_url")
                embed_url = data.get("iframe_url")

                return SpotifyMetadataResponse(
                    title=title,
                    author_name=author,
                    thumbnail_url=thumbnail,
                    embed_url=embed_url,
                    playlist_url=target_url,
                )
    except Exception as exc:
        logger.debug("Spotify oEmbed query error: %s", exc)

    # Graceful fallback if offline
    return SpotifyMetadataResponse(
        title="OpenPrevue",
        author_name="upioneer" if "3jiPmIT4RugR8TPhli5Obk" in clean_url else None,
        playlist_url=target_url,
    )
