"""Weather API endpoints for live ambient condition queries."""

from fastapi import APIRouter
from backend.app.services.weather import weather_service
from backend.app.services.websocket import connection_manager

router = APIRouter()


@router.get("/weather")
async def get_weather() -> dict:
    """Retrieve current ambient weather conditions."""
    weather = await weather_service.get_current_weather()
    return weather.to_dict()


@router.post("/weather/refresh")
async def refresh_weather() -> dict:
    """Force refresh live weather data from Open-Meteo and broadcast to active dashboards."""
    weather = await weather_service.get_current_weather(force_refresh=True)
    await connection_manager.broadcast("weather_updated", weather.to_dict())
    return weather.to_dict()
