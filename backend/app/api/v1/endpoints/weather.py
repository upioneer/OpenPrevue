"""Weather and Geocoding API endpoints for live ambient condition queries and city resolution."""

from fastapi import APIRouter, Query
from backend.app.services.weather import weather_service
from backend.app.services.geocoding import resolve_location_query, GeocodeResult
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


@router.get("/weather/geocode", response_model=list[GeocodeResult])
async def geocode_location(query: str = Query(..., min_length=2, description="City name or 5-digit ZIP code")) -> list[GeocodeResult]:
    """Resolve a city name or postal ZIP code to coordinates and metro label."""
    results = await resolve_location_query(query)
    return results
