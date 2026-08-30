"""Telegram bot management and pairing REST API endpoints."""

import random
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.db.session import get_db
from backend.app.services.telegram.bot import telegram_service
from backend.app.services.telegram.formatters import format_bulletin

router = APIRouter()


class PairCodeResponse(BaseModel):
    pair_code: str
    expires_in_seconds: int = 600


class TelegramStatusResponse(BaseModel):
    is_configured: bool
    is_running: bool
    paired_users_count: int


@router.get("/telegram/status", response_model=TelegramStatusResponse)
async def get_telegram_status() -> TelegramStatusResponse:
    """Retrieve Telegram bot configuration and worker status."""
    token = await telegram_service.get_active_token()
    paired_count = 0

    async with get_db() as db:
        async with db.execute("SELECT COUNT(*) FROM telegram_users WHERE is_active = 1") as cursor:
            row = await cursor.fetchone()
            if row:
                paired_count = row[0]

    return TelegramStatusResponse(
        is_configured=bool(token),
        is_running=telegram_service.is_running,
        paired_users_count=paired_count,
    )


@router.post("/telegram/pair-code", response_model=PairCodeResponse)
async def generate_pair_code() -> PairCodeResponse:
    """Generate a random 6-character pairing code for onboarding in Telegram."""
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(4)])
    code = f"PREVUE-{random_digits}"

    async with get_db() as db:
        await db.execute(
            """
            INSERT INTO settings (key, value, updated_at)
            VALUES ('telegram_pair_code', ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = CURRENT_TIMESTAMP
            """,
            (code,),
        )
        await db.commit()

    return PairCodeResponse(pair_code=code, expires_in_seconds=600)


@router.get("/telegram/users")
async def list_paired_users() -> list[dict]:
    """List all paired Telegram accounts."""
    async with get_db() as db:
        async with db.execute("SELECT chat_id, username, pair_code, paired_at, is_active FROM telegram_users") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


@router.delete("/telegram/users/{chat_id}")
async def unpair_user(chat_id: int) -> dict:
    """Unpair and deactivate a Telegram account."""
    async with get_db() as db:
        await db.execute("DELETE FROM telegram_users WHERE chat_id = ?", (chat_id,))
        await db.execute("DELETE FROM watchlist WHERE chat_id = ?", (chat_id,))
        await db.commit()
    return {"status": "unpaired", "chat_id": chat_id}


@router.post("/telegram/test-message")
async def send_test_message(chat_id: int) -> dict:
    """Dispatch a test bulletin message to verify Telegram delivery."""
    sample_events = [
        {
            "title": "Preservation Hall Jazz Band",
            "venue_name": "Preservation Hall",
            "category": "music",
            "start_time": "2026-09-01T20:00:00Z",
            "price_min": 25.0,
            "price_max": 25.0,
            "has_ticket": 1,
        }
    ]
    card = format_bulletin("TELEGRAM TEST CARD", sample_events, "OPENPREVUE")
    success = await telegram_service.send_notification(chat_id, card)
    if not success:
        raise HTTPException(status_code=400, detail="Failed delivering Telegram notification")

    return {"status": "sent", "chat_id": chat_id}
