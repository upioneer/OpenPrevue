"""Activity and system diagnostic event viewer API endpoints."""

from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, Query
from pydantic import BaseModel
from backend.app.db.session import get_db

router = APIRouter(prefix="/system")


class ActivityLogEntry(BaseModel):
    id: int | str
    timestamp: str
    component: str
    action: str
    status: str
    details: str | None = None


@router.get("/activity", response_model=list[ActivityLogEntry])
async def list_activity_logs(
    limit: int = Query(50, ge=1, le=200),
    component: str | None = None,
) -> list[ActivityLogEntry]:
    """Retrieve combined real-time activity and ingestion audit events."""
    entries: list[ActivityLogEntry] = []

    async with get_db() as db:
        # 1. Fetch from activity_log
        if component:
            query = "SELECT * FROM activity_log WHERE component = ? ORDER BY id DESC LIMIT ?"
            params = (component.upper(), limit)
        else:
            query = "SELECT * FROM activity_log ORDER BY id DESC LIMIT ?"
            params = (limit,)

        try:
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    entries.append(
                        ActivityLogEntry(
                            id=f"act-{row['id']}",
                            timestamp=str(row["timestamp"]),
                            component=row["component"],
                            action=row["action"],
                            status=row["status"],
                            details=row["details"],
                        )
                    )
        except Exception:
            pass

        # 2. If fewer than 15 entries, synthesize from ingestion_log to ensure rich history
        if len(entries) < 15:
            try:
                async with db.execute(
                    "SELECT * FROM ingestion_log ORDER BY id DESC LIMIT ?", (15 - len(entries),)
                ) as cursor:
                    ingest_rows = await cursor.fetchall()
                    for row in ingest_rows:
                        summary = (
                            f"Synced {row['provider']} ({row['status']}): "
                            f"{row['events_fetched']} fetched, {row['events_inserted']} added, "
                            f"{row['events_updated']} updated"
                        )
                        if row["error_message"]:
                            summary += f" - Error: {row['error_message']}"
                        entries.append(
                            ActivityLogEntry(
                                id=f"ingest-{row['id']}",
                                timestamp=str(row["started_at"]),
                                component="INGESTION",
                                action=f"sync_{row['provider']}",
                                status="success" if row["status"] in ("success", "partial") else "error",
                                details=summary,
                            )
                        )
            except Exception:
                pass

    # Sort descending by timestamp
    entries.sort(key=lambda x: str(x.timestamp), reverse=True)
    return entries[:limit]


@router.post("/activity/clear", response_model=dict[str, Any])
async def clear_activity_logs() -> dict[str, Any]:
    """Clear recorded activity logs."""
    async with get_db() as db:
        try:
            await db.execute("DELETE FROM activity_log")
            await db.commit()
        except Exception:
            pass
    return {"status": "success", "message": "Activity logs cleared"}
