"""Open-Meteo live weather data aggregation service."""

from dataclasses import dataclass
from datetime import datetime, timezone
import httpx

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import get_db

WMO_WEATHER_CODE_MAP: dict[int, str] = {
    0: "CLEAR SKY",
    1: "MAINLY CLEAR",
    2: "PARTLY CLOUDY",
    3: "OVERCAST",
    45: "FOG",
    48: "DEPOSITING RIME FOG",
    51: "LIGHT DRIZZLE",
    53: "MODERATE DRIZZLE",
    55: "DENSE DRIZZLE",
    56: "LIGHT FREEZING DRIZZLE",
    57: "DENSE FREEZING DRIZZLE",
    61: "SLIGHT RAIN",
    63: "MODERATE RAIN",
    65: "HEAVY RAIN",
    66: "LIGHT FREEZING RAIN",
    67: "HEAVY FREEZING RAIN",
    71: "SLIGHT SNOW FALL",
    73: "MODERATE SNOW FALL",
    75: "HEAVY SNOW FALL",
    77: "SNOW GRAINS",
    80: "SLIGHT RAIN SHOWERS",
    81: "MODERATE RAIN SHOWERS",
    82: "VIOLENT RAIN SHOWERS",
    85: "SLIGHT SNOW SHOWERS",
    86: "HEAVY SNOW SHOWERS",
    95: "THUNDERSTORM",
    96: "THUNDERSTORM WITH SLIGHT HAIL",
    99: "THUNDERSTORM WITH HEAVY HAIL",
}


@dataclass
class WeatherData:
    """Normalized live weather conditions."""
    temperature: float
    apparent_temperature: float
    weather_code: int
    condition: str
    humidity: int
    wind_speed: float
    temperature_unit: str = "F"
    wind_speed_unit: str = "mph"
    updated_at: str = ""

    def to_dict(self) -> dict:
        return {
            "temperature": self.temperature,
            "apparent_temperature": self.apparent_temperature,
            "weather_code": self.weather_code,
            "condition": self.condition,
            "humidity": self.humidity,
            "wind_speed": self.wind_speed,
            "temperature_unit": self.temperature_unit,
            "wind_speed_unit": self.wind_speed_unit,
            "updated_at": self.updated_at,
        }


class WeatherService:
    """Service consuming free Open-Meteo forecast API with in-memory caching."""

    def __init__(self) -> None:
        self._cached_weather: WeatherData | None = None
        self._last_fetch: datetime | None = None
        self._cache_ttl_seconds: int = 900  # 15 minutes
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    async def get_current_weather(self, force_refresh: bool = False) -> WeatherData:
        """Fetch current weather from Open-Meteo or return cached state."""
        now = datetime.now(timezone.utc)

        if (
            not force_refresh
            and self._cached_weather is not None
            and self._last_fetch is not None
            and (now - self._last_fetch).total_seconds() < self._cache_ttl_seconds
        ):
            return self._cached_weather

        # Fetch coordinates from SQLite settings
        lat = settings.DEFAULT_LATITUDE
        lon = settings.DEFAULT_LONGITUDE

        try:
            async with get_db() as db:
                async with db.execute("SELECT key, value FROM settings WHERE key IN ('latitude', 'longitude')") as cursor:
                    rows = await cursor.fetchall()
                    settings_map = {row["key"]: row["value"] for row in rows}
                    if "latitude" in settings_map:
                        lat = float(settings_map["latitude"])
                    if "longitude" in settings_map:
                        lon = float(settings_map["longitude"])
        except Exception as exc:
            logger.debug("Using default coordinates for weather: %s", exc)

        params = {
            "latitude": str(lat),
            "longitude": str(lon),
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()

            current = data.get("current", {})
            weather_code = int(current.get("weather_code", 0))
            condition = WMO_WEATHER_CODE_MAP.get(weather_code, "UNKNOWN")

            weather = WeatherData(
                temperature=float(current.get("temperature_2m", 72.0)),
                apparent_temperature=float(current.get("apparent_temperature", 72.0)),
                weather_code=weather_code,
                condition=condition,
                humidity=int(current.get("relative_humidity_2m", 50)),
                wind_speed=float(current.get("wind_speed_10m", 5.0)),
                temperature_unit="F",
                wind_speed_unit="mph",
                updated_at=now.isoformat(),
            )

            self._cached_weather = weather
            self._last_fetch = now
            logger.info("Updated live weather from Open-Meteo: %0.1fF %s", weather.temperature, weather.condition)
            return weather

        except Exception as exc:
            logger.warning("Error fetching weather from Open-Meteo: %s. Using fallback.", exc)
            if self._cached_weather:
                return self._cached_weather

            # Fallback default
            return WeatherData(
                temperature=75.0,
                apparent_temperature=76.0,
                weather_code=0,
                condition="CLEAR SKY",
                humidity=55,
                wind_speed=4.0,
                temperature_unit="F",
                wind_speed_unit="mph",
                updated_at=now.isoformat(),
            )


weather_service = WeatherService()
