"""Commercials and retro video bumpers endpoint with filesystem dropzone support."""

from pathlib import Path
from typing import Any
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from backend.app.core.logging import logger

router = APIRouter(prefix="/commercials", tags=["Commercials"])

COMMERCIALS_DIR = Path("data") / "commercials"
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = {".mp4", ".webm", ".m4v"}


def ensure_commercials_dir() -> Path:
    """Ensure data/commercials directory exists."""
    COMMERCIALS_DIR.mkdir(parents=True, exist_ok=True)
    return COMMERCIALS_DIR


@router.get("", response_model=dict[str, Any])
async def list_commercial_clips() -> dict[str, Any]:
    """List all available commercial clips from the local filesystem dropzone."""
    target_dir = ensure_commercials_dir()
    clips = []

    for file_path in target_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in ALLOWED_EXTENSIONS:
            stat = file_path.stat()
            clips.append({
                "id": file_path.stem,
                "name": file_path.name,
                "filename": file_path.name,
                "size_bytes": stat.st_size,
                "size_formatted": f"{stat.st_size / (1024 * 1024):.1f} MB",
                "url": f"/api/v1/commercials/stream/{file_path.name}",
                "is_user_uploaded": True,
            })

    return {
        "status": "success",
        "dropzone_directory": str(target_dir.resolve()),
        "total_clips": len(clips),
        "clips": clips,
        "specifications": {
            "recommended_resolution": "640x480 (4:3) or 1280x720 (16:9)",
            "video_codec": "H.264 (AVC) / WebM (VP9)",
            "audio_codec": "AAC-LC / MP3 stereo 44.1kHz or 48kHz",
            "max_file_size_mb": 50,
            "recommended_duration_seconds": "5 to 30 seconds",
        },
    }


@router.get("/stream/{filename}")
async def stream_commercial_video(filename: str) -> FileResponse:
    """Stream a commercial video file directly from the local filesystem."""
    target_dir = ensure_commercials_dir()
    file_path = target_dir / filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested commercial clip was not found.",
        )

    if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid video file format.",
        )

    media_type = "video/webm" if file_path.suffix.lower() == ".webm" else "video/mp4"
    return FileResponse(path=file_path, media_type=media_type)


@router.post("/upload")
async def upload_commercial_clip(file: UploadFile = File(...)) -> dict[str, Any]:
    """Upload a new commercial video clip into the local dropzone."""
    target_dir = ensure_commercials_dir()

    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided.")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format: '{ext}'. Please upload an MP4 (.mp4) or WebM (.webm) video.",
        )

    # Read content and validate size limit
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds the 50 MB limit (File is {len(content) / (1024 * 1024):.1f} MB).",
        )

    safe_filename = Path(file.filename).name
    destination = target_dir / safe_filename

    with open(destination, "wb") as f:
        f.write(content)

    logger.info("Saved new commercial clip: %s (%d bytes)", safe_filename, len(content))

    return {
        "status": "success",
        "message": f"Successfully added '{safe_filename}' to commercial queue.",
        "clip": {
            "id": destination.stem,
            "name": safe_filename,
            "filename": safe_filename,
            "size_bytes": len(content),
            "url": f"/api/v1/commercials/stream/{safe_filename}",
        },
    }
