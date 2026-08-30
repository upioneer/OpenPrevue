"""API v1 master router aggregating sub-routers."""

from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    eas,
    events,
    health,
    mcp,
    settings,
    speech,
    sync,
    telegram,
    updates,
    venues,
    weather,
    ws,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(events.router, tags=["Events"])
api_router.include_router(venues.router, tags=["Venues"])
api_router.include_router(settings.router, tags=["Settings"])
api_router.include_router(sync.router, tags=["Sync"])
api_router.include_router(weather.router, tags=["Weather"])
api_router.include_router(ws.router, tags=["WebSocket"])
api_router.include_router(telegram.router, tags=["Telegram"])
api_router.include_router(speech.router, tags=["Speech"])
api_router.include_router(eas.router, tags=["Emergency Alert System"])
api_router.include_router(mcp.router, tags=["Model Context Protocol"])
api_router.include_router(updates.router, tags=["Updates"])
