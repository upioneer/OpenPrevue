"""Asynchronous Telegram bot worker runner and push notification dispatcher."""

import asyncio
from datetime import datetime, timedelta, timezone
from telegram import Bot
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import get_db
from backend.app.providers.base import RawEvent
from backend.app.services.telegram.formatters import format_bulletin, format_error_box
from backend.app.services.telegram.handlers import (
    add_command,
    help_command,
    pair_command,
    pin_command,
    plain_text_message_handler,
    search_command,
    start_command,
    status_command,
    today_command,
    tonight_command,
    unknown_command_handler,
    unpin_command,
    unwatch_command,
    voice_message_handler,
    watch_command,
    watchlist_command,
    weekend_command,
)


class TelegramBotService:
    """Manages Telegram bot lifecycle, polling loop, and outbound push notifications."""

    def __init__(self) -> None:
        self.app: Application | None = None
        self._is_running: bool = False
        self._bot_token: str | None = settings.TELEGRAM_BOT_TOKEN

    @property
    def is_running(self) -> bool:
        return self._is_running

    async def get_active_token(self) -> str | None:
        """Fetch configured bot token from database or settings."""
        if self._bot_token:
            return self._bot_token

        try:
            async with get_db() as db:
                async with db.execute("SELECT value FROM settings WHERE key = 'telegram_bot_token'") as cursor:
                    row = await cursor.fetchone()
                    if row and row["value"]:
                        return row["value"].strip()
        except Exception as exc:
            logger.debug("Error fetching Telegram bot token: %s", exc)

        return None

    async def start(self) -> None:
        """Initialize and start async polling bot worker if token is configured."""
        token = await self.get_active_token()
        if not token:
            logger.info("Telegram bot token not configured. Bot worker is idle.")
            return

        if self._is_running:
            return

        try:
            logger.info("Initializing Telegram bot worker...")
            self.app = ApplicationBuilder().token(token).build()

            # Register standard commands
            self.app.add_handler(CommandHandler("start", start_command))
            self.app.add_handler(CommandHandler("pair", pair_command))
            self.app.add_handler(CommandHandler("add", add_command))
            self.app.add_handler(CommandHandler("today", today_command))
            self.app.add_handler(CommandHandler("tonight", tonight_command))
            self.app.add_handler(CommandHandler("weekend", weekend_command))
            self.app.add_handler(CommandHandler("search", search_command))
            self.app.add_handler(CommandHandler("pin", pin_command))
            self.app.add_handler(CommandHandler("unpin", unpin_command))
            self.app.add_handler(CommandHandler("watch", watch_command))
            self.app.add_handler(CommandHandler("unwatch", unwatch_command))
            self.app.add_handler(CommandHandler("watchlist", watchlist_command))
            self.app.add_handler(CommandHandler("status", status_command))
            self.app.add_handler(CommandHandler("help", help_command))

            # Register voice memo handler
            self.app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, voice_message_handler))

            # Register boxed interaction fallback error guards
            self.app.add_handler(MessageHandler(filters.COMMAND, unknown_command_handler))
            self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, plain_text_message_handler))

            await self.app.initialize()
            await self.app.start()
            if self.app.updater:
                await self.app.updater.start_polling(drop_pending_updates=True)

            self._is_running = True
            logger.info("Telegram bot worker is active and polling.")

        except Exception as exc:
            logger.warning("Failed starting Telegram bot worker: %s", exc)
            self._is_running = False

    async def stop(self) -> None:
        """Gracefully stop polling and terminate Telegram bot worker."""
        if not self._is_running or not self.app:
            return

        try:
            logger.info("Shutting down Telegram bot worker...")
            if self.app.updater and self.app.updater.running:
                await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()
            self._is_running = False
            logger.info("Telegram bot worker terminated.")
        except Exception as exc:
            logger.debug("Error during Telegram bot shutdown: %s", exc)

    async def send_notification(self, chat_id: int, message_text: str) -> bool:
        """Send a direct message to a specific chat ID."""
        token = await self.get_active_token()
        if not token:
            return False

        try:
            bot = Bot(token=token)
            await bot.send_message(chat_id=chat_id, text=message_text, parse_mode="MarkdownV2")
            return True
        except Exception as exc:
            logger.warning("Failed sending Telegram push notification to %d: %s", chat_id, exc)
            return False

    async def broadcast_weekend_digest(self) -> None:
        """Scheduled task: send weekend event digest to all paired users."""
        now = datetime.now(timezone.utc)
        days_until_friday = (4 - now.weekday()) % 7
        friday = (now + timedelta(days=days_until_friday)).strftime("%Y-%m-%d")
        sunday = (now + timedelta(days=days_until_friday + 2)).strftime("%Y-%m-%d")

        async with get_db() as db:
            async with db.execute(
                """
                SELECT e.*, v.name AS venue_name
                FROM events e
                LEFT JOIN venues v ON e.venue_id = v.id
                WHERE date(e.start_time) BETWEEN ? AND ? AND e.status = 'active'
                ORDER BY e.start_time ASC LIMIT 10
                """,
                (friday, sunday),
            ) as cursor:
                events = [dict(row) for row in await cursor.fetchall()]

            if not events:
                return

            async with db.execute("SELECT chat_id FROM telegram_users WHERE is_active = 1") as cursor:
                users = await cursor.fetchall()

        digest_card = format_bulletin("WEEKEND PUSH DIGEST", events, "OPENPREVUE")

        for user in users:
            await self.send_notification(user["chat_id"], digest_card)

    async def scan_watchlist_and_alert(self, new_events: list[RawEvent]) -> None:
        """Scan newly ingested events against active user watchlists."""
        if not new_events:
            return

        async with get_db() as db:
            async with db.execute("SELECT chat_id, keyword FROM watchlist") as cursor:
                watchlist_rows = await cursor.fetchall()

        if not watchlist_rows:
            return

        for row in watchlist_rows:
            chat_id = row["chat_id"]
            kw = row["keyword"].lower()

            matches = [
                evt for evt in new_events
                if kw in evt.title.lower() or (evt.description and kw in evt.description.lower())
            ]

            if matches:
                event_items = [
                    {
                        "title": m.title,
                        "venue_name": m.venue_name,
                        "category": m.category,
                        "start_time": m.start_time,
                        "price_min": m.price_min,
                        "price_max": m.price_max,
                        "has_ticket": 0,
                    }
                    for m in matches[:5]
                ]
                alert_card = format_bulletin(f"WATCHLIST MATCH: {kw.upper()}", event_items, "ALERT")
                await self.send_notification(chat_id, alert_card)


telegram_service = TelegramBotService()
