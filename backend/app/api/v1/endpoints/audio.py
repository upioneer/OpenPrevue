"""Audio presets, radio streams, and background source endpoints."""

from fastapi import APIRouter
from backend.app.core.config import settings

router = APIRouter(prefix="/audio")

OFFICIAL_SPOTIFY_PLAYLIST_URL = "https://open.spotify.com/playlist/3jiPmIT4RugR8TPhli5Obk"

AUDIO_PRESETS = [
    {
        "id": "spotify",
        "name": "Spotify Playlist (Curated Retro Muzak)",
        "type": "spotify",
        "default_url": OFFICIAL_SPOTIFY_PLAYLIST_URL,
        "is_default": True,
        "description": 'Official curated vintage 90s cable jazz and weather channel playlist by upioneer.',
    },
    {
        "id": "weatherscan",
        "name": "1990s WeatherScan Smooth Jazz",
        "type": "icecast",
        "stream_url": "https://stream.zeno.fm/f3wvbbqmdg8uv",
        "is_default": False,
        "description": "Continuous live stream of classic 1990s cable weather channel smooth jazz.",
    },
    {
        "id": "somafm_groovesalad",
        "name": "SomaFM Groove Salad (Ambient / Downtempo)",
        "type": "icecast",
        "stream_url": "https://ice1.somafm.com/groovesalad-128-mp3",
        "is_default": False,
        "description": "A nicely chilled plate of ambient/downtempo beats and grooves.",
    },
    {
        "id": "somafm_dronezone",
        "name": "SomaFM Drone Zone (Atmospheric)",
        "type": "icecast",
        "stream_url": "https://ice1.somafm.com/dronezone-128-mp3",
        "is_default": False,
        "description": "Atmospheric ambient audio for deep relaxation and monitoring.",
    },
    {
        "id": "nightwave_plaza",
        "name": "Nightwave Plaza (Retro Vaporwave & Synth)",
        "type": "icecast",
        "stream_url": "https://plaza.one/mp3",
        "is_default": False,
        "description": "24/7 online retro vaporwave and future funk internet radio.",
    },
    {
        "id": "custom",
        "name": "Custom Icecast / MP3 Stream URL",
        "type": "custom",
        "stream_url": "",
        "is_default": False,
        "description": "Specify any custom direct MP3 / AAC / Icecast live audio stream.",
    },
    {
        "id": "synth",
        "name": "Turnkey Retro Synthesizer Chimes (Offline)",
        "type": "synth",
        "is_default": False,
        "description": "Local Web Audio procedural chimes and tones with zero network dependencies.",
    },
    {
        "id": "muted",
        "name": "Mute / Disabled",
        "type": "muted",
        "is_default": False,
        "description": "Disable background music playback.",
    },
]


@router.get("/presets")
async def get_audio_presets() -> list[dict]:
    """Retrieve available audio streaming presets and sources."""
    return AUDIO_PRESETS
