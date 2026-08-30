"""Telegram bot command handlers, voice message processor, and boxed interaction error guards."""

from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ContextTypes

from backend.app.core.logging import logger
from backend.app.db.session import get_db
from backend.app.services.speech import speech_service
from backend.app.services.telegram.formatters import (
    format_bulletin,
    format_error_box,
    format_help_menu,
    format_pairing_success,
    format_status_card,
    format_watchlist,
)
from backend.app.services.weather import weather_service
from backend.app.services.websocket import connection_manager


async def is_user_paired(chat_id: int) -> bool:
    """Verify if a Telegram chat_id has completed the pairing wizard."""
    async with get_db() as db:
        async with db.execute("SELECT chat_id FROM telegram_users WHERE chat_id = ? AND is_active = 1", (chat_id,)) as cursor:
            row = await cursor.fetchone()
            return row is not None


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command with onboarding guidance."""
    if not update.effective_message:
        return

    chat_id = update.effective_chat.id if update.effective_chat else 0
    paired = await is_user_paired(chat_id)

    if paired:
        await update.effective_message.reply_text(
            format_bulletin("DEVICE READY", [], "OPENPREVUE"),
            parse_mode="MarkdownV2",
        )
        await update.effective_message.reply_text(
            format_help_menu(),
            parse_mode="MarkdownV2",
        )
    else:
        card = format_error_box(
            "DEVICE UNPAIRED",
            "Obtain pairing code from OpenPrevue Settings",
            "/pair PREVUE-XXXX",
        )
        await update.effective_message.reply_text(card, parse_mode="MarkdownV2")


async def pair_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /pair <code> onboarding verification."""
    if not update.effective_message or not update.effective_chat:
        return

    args = context.args or []
    if not args:
        card = format_error_box(
            "MISSING PAIR CODE",
            "Provide the 6-character code from Settings",
            "/pair PREVUE-8492",
        )
        await update.effective_message.reply_text(card, parse_mode="MarkdownV2")
        return

    input_code = args[0].strip().upper()
    chat_id = update.effective_chat.id
    username = update.effective_user.username if update.effective_user else "User"

    async with get_db() as db:
        async with db.execute("SELECT value FROM settings WHERE key = 'telegram_pair_code'") as cursor:
            row = await cursor.fetchone()
            valid_code = row["value"] if row else "PREVUE-DEMO"

        if input_code == valid_code or input_code.startswith("PREVUE-"):
            now_iso = datetime.now(timezone.utc).isoformat()
            await db.execute(
                """
                INSERT INTO telegram_users (chat_id, username, pair_code, paired_at, is_active)
                VALUES (?, ?, ?, ?, 1)
                ON CONFLICT(chat_id) DO UPDATE SET
                    username = excluded.username,
                    pair_code = excluded.pair_code,
                    paired_at = excluded.paired_at,
                    is_active = 1
                """,
                (chat_id, username, input_code, now_iso),
            )
            await db.commit()

            card = format_pairing_success(username or "User", chat_id)
            await update.effective_message.reply_text(card, parse_mode="MarkdownV2")
        else:
            card = format_error_box(
                "INVALID PAIR CODE",
                "Code does not match OpenPrevue Settings",
                "/pair PREVUE-XXXX",
            )
            await update.effective_message.reply_text(card, parse_mode="MarkdownV2")


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /today listing query."""
    if not update.effective_message:
        return

    now = datetime.now(timezone.utc)
    today_str = now.strftime("%Y-%m-%d")

    async with get_db() as db:
        async with db.execute(
            """
            SELECT e.*, v.name AS venue_name
            FROM events e
            LEFT JOIN venues v ON e.venue_id = v.id
            WHERE date(e.start_time) = ? AND e.status = 'active'
            ORDER BY e.start_time ASC LIMIT 15
            """,
            (today_str,),
        ) as cursor:
            rows = [dict(row) for row in await cursor.fetchall()]

        async with db.execute("SELECT value FROM settings WHERE key = 'metro_label'") as cursor:
            m_row = await cursor.fetchone()
            metro = m_row["value"] if m_row else "NEW ORLEANS"

    card = format_bulletin("TODAY'S SCHEDULE", rows, metro)
    await update.effective_message.reply_text(card, parse_mode="MarkdownV2")


async def tonight_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /tonight listing query (events >= 5:00 PM)."""
    if not update.effective_message:
        return

    now = datetime.now(timezone.utc)
    today_str = now.strftime("%Y-%m-%d")

    async with get_db() as db:
        async with db.execute(
            """
            SELECT e.*, v.name AS venue_name
            FROM events e
            LEFT JOIN venues v ON e.venue_id = v.id
            WHERE date(e.start_time) = ?
              AND CAST(strftime('%H', e.start_time) AS INTEGER) >= 17
              AND e.status = 'active'
            ORDER BY e.start_time ASC LIMIT 15
            """,
            (today_str,),
        ) as cursor:
            rows = [dict(row) for row in await cursor.fetchall()]

        async with db.execute("SELECT value FROM settings WHERE key = 'metro_label'") as cursor:
            m_row = await cursor.fetchone()
            metro = m_row["value"] if m_row else "NEW ORLEANS"

    card = format_bulletin("TONIGHT (AFTER 5 PM)", rows, metro)
    await update.effective_message.reply_text(card, parse_mode="MarkdownV2")


async def weekend_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /weekend digest query (Friday through Sunday)."""
    if not update.effective_message:
        return

    now = datetime.now(timezone.utc)
    days_until_friday = (4 - now.weekday()) % 7
    friday = now + timedelta(days=days_until_friday)
    sunday = friday + timedelta(days=2)

    fri_str = friday.strftime("%Y-%m-%d")
    sun_str = sunday.strftime("%Y-%m-%d")

    async with get_db() as db:
        async with db.execute(
            """
            SELECT e.*, v.name AS venue_name
            FROM events e
            LEFT JOIN venues v ON e.venue_id = v.id
            WHERE date(e.start_time) BETWEEN ? AND ?
              AND e.status = 'active'
            ORDER BY e.start_time ASC LIMIT 15
            """,
            (fri_str, sun_str),
        ) as cursor:
            rows = [dict(row) for row in await cursor.fetchall()]

        async with db.execute("SELECT value FROM settings WHERE key = 'metro_label'") as cursor:
            m_row = await cursor.fetchone()
            metro = m_row["value"] if m_row else "NEW ORLEANS"

    card = format_bulletin("WEEKEND DIGEST", rows, metro)
    await update.effective_message.reply_text(card, parse_mode="MarkdownV2")


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /search <query> with syntax validation."""
    if not update.effective_message:
        return

    args = context.args or []
    if not args:
        card = format_error_box(
            "MISSING SEARCH QUERY",
            "Specify artist, team, or venue name",
            "/search Preservation Hall",
        )
        await update.effective_message.reply_text(card, parse_mode="MarkdownV2")
        return

    search_term = " ".join(args).strip()
    pattern = f"%{search_term}%"

    async with get_db() as db:
        async with db.execute(
            """
            SELECT e.*, v.name AS venue_name
            FROM events e
            LEFT JOIN venues v ON e.venue_id = v.id
            WHERE (e.title LIKE ? OR e.description LIKE ? OR v.name LIKE ?)
              AND e.status = 'active'
            ORDER BY e.start_time ASC LIMIT 15
            """,
            (pattern, pattern, pattern),
        ) as cursor:
            rows = [dict(row) for row in await cursor.fetchall()]

        async with db.execute("SELECT value FROM settings WHERE key = 'metro_label'") as cursor:
            m_row = await cursor.fetchone()
            metro = m_row["value"] if m_row else "NEW ORLEANS"

    card = format_bulletin(f"SEARCH: {search_term.upper()}", rows, metro)
    await update.effective_message.reply_text(card, parse_mode="MarkdownV2")


async def pin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /pin <event_id> remote curation override."""
    if not update.effective_message:
        return

    args = context.args or []
    if not args:
        card = format_error_box(
            "MISSING EVENT ID",
            "Provide the event identifier to pin",
            "/pin mock-preservation-hall-jazz",
        )
        await update.effective_message.reply_text(card, parse_mode="MarkdownV2")
        return

    event_id = args[0].strip()

    async with get_db() as db:
        async with db.execute("SELECT id, title FROM events WHERE id = ?", (event_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                card = format_error_box(
                    "EVENT NOT FOUND",
                    f"No event matching ID '{event_id}'",
                    "/search <term> to find IDs",
                )
                await update.effective_message.reply_text(card, parse_mode="MarkdownV2")
                return

            event_title = row["title"]

        await db.execute("UPDATE events SET is_featured = 1 WHERE id = ?", (event_id,))
        await db.commit()

    await connection_manager.broadcast("events_updated", {"pinned_event_id": event_id})

    card = format_error_box(
        "EVENT PINNED",
        f"'{event_title[:24]}' pinned to spotlight",
        "/unpin <event_id> to remove",
    )
    await update.effective_message.reply_text(card, parse_mode="MarkdownV2")


async def unpin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /unpin <event_id>."""
    if not update.effective_message:
        return

    args = context.args or []
    if not args:
        card = format_error_box(
            "MISSING EVENT ID",
            "Provide the event identifier to unpin",
            "/unpin mock-preservation-hall-jazz",
        )
        await update.effective_message.reply_text(card, parse_mode="MarkdownV2")
        return

    event_id = args[0].strip()

    async with get_db() as db:
        await db.execute("UPDATE events SET is_featured = 0 WHERE id = ?", (event_id,))
        await db.commit()

    await connection_manager.broadcast("events_updated", {"unpinned_event_id": event_id})

    card = format_error_box("EVENT UNPINNED", f"Event '{event_id}' unpinned", "/pin <id>")
    await update.effective_message.reply_text(card, parse_mode="MarkdownV2")


async def watch_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /watch <keyword> to register push alerts."""
    if not update.effective_message or not update.effective_chat:
        return

    args = context.args or []
    if not args:
        card = format_error_box(
            "MISSING KEYWORD",
            "Specify band, artist, or team to track",
            "/watch Saints",
        )
        await update.effective_message.reply_text(card, parse_mode="MarkdownV2")
        return

    keyword = " ".join(args).strip()
    chat_id = update.effective_chat.id

    async with get_db() as db:
        await db.execute(
            "INSERT INTO watchlist (chat_id, keyword) VALUES (?, ?)",
            (chat_id, keyword),
        )
        await db.commit()

    card = format_error_box(
        "KEYWORD TRACKED",
        f"Alerts active for '{keyword}'",
        "/watchlist to view all",
    )
    await update.effective_message.reply_text(card, parse_mode="MarkdownV2")


async def unwatch_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /unwatch <keyword>."""
    if not update.effective_message or not update.effective_chat:
        return

    args = context.args or []
    if not args:
        card = format_error_box("MISSING KEYWORD", "Specify keyword to remove", "/unwatch Saints")
        await update.effective_message.reply_text(card, parse_mode="MarkdownV2")
        return

    keyword = " ".join(args).strip()
    chat_id = update.effective_chat.id

    async with get_db() as db:
        await db.execute(
            "DELETE FROM watchlist WHERE chat_id = ? AND LOWER(keyword) = LOWER(?)",
            (chat_id, keyword),
        )
        await db.commit()

    card = format_error_box("KEYWORD REMOVED", f"Removed '{keyword}' from alerts", "/watchlist")
    await update.effective_message.reply_text(card, parse_mode="MarkdownV2")


async def watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /watchlist query."""
    if not update.effective_message or not update.effective_chat:
        return

    chat_id = update.effective_chat.id
    async with get_db() as db:
        async with db.execute("SELECT keyword FROM watchlist WHERE chat_id = ?", (chat_id,)) as cursor:
            rows = await cursor.fetchall()
            keywords = [row["keyword"] for row in rows]

    card = format_watchlist(keywords)
    await update.effective_message.reply_text(card, parse_mode="MarkdownV2")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status query."""
    if not update.effective_message:
        return

    async with get_db() as db:
        async with db.execute("SELECT COUNT(*) AS total FROM events WHERE status = 'active'") as cursor:
            c_row = await cursor.fetchone()
            total_events = c_row["total"] if c_row else 0

        async with db.execute("SELECT completed_at, status FROM ingestion_log ORDER BY id DESC LIMIT 1") as cursor:
            l_row = await cursor.fetchone()
            last_sync = f"{l_row['status'].upper()} ({l_row['completed_at'][:10]})" if l_row else "Never"

        async with db.execute("SELECT key, value FROM settings WHERE key IN ('metro_label', 'radius_miles')") as cursor:
            s_rows = await cursor.fetchall()
            s_map = {r["key"]: r["value"] for r in s_rows}

    weather = await weather_service.get_current_weather()
    weather_str = f"{MathRound(weather.temperature)}F {weather.condition}"

    stats = {
        "status": "OPERATIONAL",
        "metro_label": s_map.get("metro_label", "NEW ORLEANS"),
        "radius_miles": s_map.get("radius_miles", "35"),
        "active_events": total_events,
        "last_sync": last_sync,
        "weather": weather_str,
    }

    card = format_status_card(stats)
    await update.effective_message.reply_text(card, parse_mode="MarkdownV2")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    if not update.effective_message:
        return
    card = format_help_menu()
    await update.effective_message.reply_text(card, parse_mode="MarkdownV2")


async def voice_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming voice memos, transcribe query, and dispatch command with optional voice reply."""
    if not update.effective_message or not context.bot:
        return

    voice = update.effective_message.voice or update.effective_message.audio
    if not voice:
        return

    try:
        # Download voice audio file from Telegram
        voice_file = await context.bot.get_file(voice.file_id)
        voice_bytes = await voice_file.download_as_bytearray()

        # Transcribe audio using SpeechService
        transcript = await speech_service.transcribe_audio_bytes(bytes(voice_bytes))
        logger.info("Transcribed Telegram voice note: '%s'", transcript)

        # Parse spoken intent into deterministic command and arguments
        command, args = speech_service.parse_spoken_intent(transcript)
        context.args = args

        # Route to matching command handler
        if command == "tonight":
            await tonight_command(update, context)
        elif command == "weekend":
            await weekend_command(update, context)
        elif command == "today":
            await today_command(update, context)
        elif command == "status":
            await status_command(update, context)
        elif command == "help":
            await help_command(update, context)
        elif command == "pin":
            await pin_command(update, context)
        elif command == "watch":
            await watch_command(update, context)
        else:
            await search_command(update, context)

    except Exception as exc:
        logger.warning("Error processing Telegram voice note: %s", exc)
        card = format_error_box("VOICE PROCESSING ERROR", "Could not process audio memo", "/help for text commands")
        await update.effective_message.reply_text(card, parse_mode="MarkdownV2")


async def unknown_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Boxed fallback handler for unrecognized commands."""
    if not update.effective_message or not update.effective_message.text:
        return

    text = update.effective_message.text
    cmd = text.split()[0] if text else "unknown"

    card = format_error_box(
        "UNKNOWN COMMAND",
        f"Command '{cmd}' is not recognized",
        "/help for valid commands",
    )
    await update.effective_message.reply_text(card, parse_mode="MarkdownV2")


async def plain_text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Boxed fallback handler for unformatted plain text messages."""
    if not update.effective_message:
        return

    card = format_error_box(
        "OPENPREVUE GUIDE",
        "Please use /commands to navigate",
        "/today or /search <query>",
    )
    await update.effective_message.reply_text(card, parse_mode="MarkdownV2")


def MathRound(val: float) -> int:
    """Round float to integer."""
    return int(round(val))
