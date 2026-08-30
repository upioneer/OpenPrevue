"""OpenPrevue FastAPI main application entrypoint."""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.v1.endpoints.ws import dashboard_websocket_endpoint
from backend.app.api.v1.router import api_router
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import init_db
from backend.app.services.scheduler import shutdown_scheduler, start_scheduler
from backend.app.services.seeder import seed_initial_data
from backend.app.services.telegram.bot import telegram_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context handling startup initialization and shutdown cleanup."""
    logger.info("OpenPrevue backend initializing...")
    await init_db()
    await seed_initial_data()
    await start_scheduler()
    await telegram_service.start()
    logger.info("OpenPrevue backend initialized and services running.")
    yield
    logger.info("OpenPrevue backend shutting down...")
    await telegram_service.stop()
    await shutdown_scheduler()


app = FastAPI(
    title="OpenPrevue API",
    version="0.15.0",
    description="Self-hosted local event aggregator and interactive retro display backend.",
    lifespan=lifespan,
)

# CORS middleware for development frontend server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API
app.include_router(api_router)

# Mount root WebSocket endpoint
app.add_api_websocket_route("/ws/dashboard", dashboard_websocket_endpoint)

# Mount static frontend build if present
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists() and (frontend_dist / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )













