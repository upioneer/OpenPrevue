"""Asynchronous SQLite database connection session management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
import aiosqlite

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.schema import SCHEMA_SQL


async def init_db(database_path: Path | None = None) -> None:
    """Initialize database tables, migrations, and indices if not present."""
    db_file = database_path or settings.database_path
    db_file.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Initializing database at %s", db_file)
    async with aiosqlite.connect(db_file) as db:
        # Check if events table exists and needs column migration before running schema script
        try:
            async with db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'") as cursor:
                table_exists = await cursor.fetchone()

            if table_exists:
                async with db.execute("PRAGMA table_info(events)") as cursor:
                    columns = [row[1] for row in await cursor.fetchall()]
                    if "has_ticket" not in columns:
                        logger.info("Migrating schema: Adding has_ticket column to existing events table")
                        await db.execute("ALTER TABLE events ADD COLUMN has_ticket INTEGER DEFAULT 0")
        except Exception as exc:
            logger.warning("Pre-schema column migration check error: %s", exc)

        await db.executescript(SCHEMA_SQL)

        # Ensure unique index on ticket_links(event_id, source)
        try:
            await db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_ticket_links_event_source ON ticket_links(event_id, source);")
        except Exception:
            pass

        await db.commit()

        # Verify WAL mode
        async with db.execute("PRAGMA journal_mode;") as cursor:
            row = await cursor.fetchone()
            journal_mode = row[0] if row else "unknown"
            logger.info("Database initialized. Journal mode: %s", journal_mode)


@asynccontextmanager
async def get_db(database_path: Path | None = None) -> AsyncGenerator[aiosqlite.Connection, None]:
    """Provide an asynchronous SQLite connection context with dictionary-like row access."""
    db_file = database_path or settings.database_path
    async with aiosqlite.connect(db_file) as connection:
        connection.row_factory = aiosqlite.Row
        await connection.execute("PRAGMA foreign_keys = ON;")
        yield connection
