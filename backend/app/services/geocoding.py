"""Geocoding service resolving city names and postal codes to geographic coordinates."""

import re
import httpx
from pydantic import BaseModel
from backend.app.core.logging import logger

FALLBACK_POPULAR_CITIES = {
    "new york": {"metro_label": "NEW YORK CITY", "latitude": 40.7128, "longitude": -74.0060, "postal_code": "10001", "admin1": "New York", "country": "United States"},
    "nyc": {"metro_label": "NEW YORK CITY", "latitude": 40.7128, "longitude": -74.0060, "postal_code": "10001", "admin1": "New York", "country": "United States"},
    "los angeles": {"metro_label": "LOS ANGELES, CA", "latitude": 34.0522, "longitude": -118.2437, "postal_code": "90012", "admin1": "California", "country": "United States"},
    "chicago": {"metro_label": "CHICAGO, IL", "latitude": 41.8781, "longitude": -87.6298, "postal_code": "60601", "admin1": "Illinois", "country": "United States"},
    "houston": {"metro_label": "HOUSTON, TX", "latitude": 29.7604, "longitude": -95.3698, "postal_code": "77002", "admin1": "Texas", "country": "United States"},
    "austin": {"metro_label": "AUSTIN, TX", "latitude": 30.2672, "longitude": -97.7431, "postal_code": "78701", "admin1": "Texas", "country": "United States"},
    "seattle": {"metro_label": "SEATTLE, WA", "latitude": 47.6062, "longitude": -122.3321, "postal_code": "98101", "admin1": "Washington", "country": "United States"},
    "miami": {"metro_label": "MIAMI, FL", "latitude": 25.7617, "longitude": -80.1918, "postal_code": "33101", "admin1": "Florida", "country": "United States"},
    "san francisco": {"metro_label": "SAN FRANCISCO, CA", "latitude": 37.7749, "longitude": -122.4194, "postal_code": "94102", "admin1": "California", "country": "United States"},
    "boston": {"metro_label": "BOSTON, MA", "latitude": 42.3601, "longitude": -71.0589, "postal_code": "02108", "admin1": "Massachusetts", "country": "United States"},
    "denver": {"metro_label": "DENVER, CO", "latitude": 39.7392, "longitude": -104.9903, "postal_code": "80202", "admin1": "Colorado", "country": "United States"},
    "atlanta": {"metro_label": "ATLANTA, GA", "latitude": 33.7490, "longitude": -84.3880, "postal_code": "30303", "admin1": "Georgia", "country": "United States"},
    "nashville": {"metro_label": "NASHVILLE, TN", "latitude": 36.1627, "longitude": -86.7816, "postal_code": "37201", "admin1": "Tennessee", "country": "United States"},
    "new orleans": {"metro_label": "NEW ORLEANS, LA", "latitude": 29.9511, "longitude": -90.0715, "postal_code": "70112", "admin1": "Louisiana", "country": "United States"},
    "las vegas": {"metro_label": "LAS VEGAS, NV", "latitude": 36.1699, "longitude": -115.1398, "postal_code": "89101", "admin1": "Nevada", "country": "United States"},
    "london": {"metro_label": "LONDON, UK", "latitude": 51.5074, "longitude": -0.1278, "postal_code": "EC1A", "admin1": "England", "country": "United Kingdom"},
    "tokyo": {"metro_label": "TOKYO, JP", "latitude": 35.6762, "longitude": 139.6503, "postal_code": "100-0001", "admin1": "Tokyo", "country": "Japan"},
    "toronto": {"metro_label": "TORONTO, ON", "latitude": 43.6532, "longitude": -79.3832, "postal_code": "M5H", "admin1": "Ontario", "country": "Canada"},
}


class GeocodeResult(BaseModel):
    """Structured geocoding search hit."""
    name: str
    admin1: str | None = None
    country: str | None = None
    metro_label: str
    latitude: float
    longitude: float
    postal_code: str | None = None
    display_label: str


async def resolve_location_query(query: str) -> list[GeocodeResult]:
    """Resolve a user-provided city name or postal ZIP code to coordinates."""
    clean_query = query.strip()
    if not clean_query:
        return []

    results: list[GeocodeResult] = []

    # 1. Check if query is a 5-digit US ZIP code
    is_zip = bool(re.match(r"^\d{5}$", clean_query))
    if is_zip:
        try:
            async with httpx.AsyncClient(timeout=3.5) as client:
                zip_res = await client.get(f"https://api.zippopotam.us/us/{clean_query}")
                if zip_res.status_code == 200:
                    data = zip_res.json()
                    places = data.get("places", [])
                    if places:
                        p = places[0]
                        place_name = p.get("place name", "Area")
                        state_abbr = p.get("state abbreviation", "")
                        state_full = p.get("state", "")
                        lat = float(p.get("latitude", 0))
                        lon = float(p.get("longitude", 0))
                        metro_label = f"{place_name.upper()}, {state_abbr}".strip(", ")
                        results.append(
                            GeocodeResult(
                                name=place_name,
                                admin1=state_full,
                                country="United States",
                                metro_label=metro_label,
                                latitude=lat,
                                longitude=lon,
                                postal_code=clean_query,
                                display_label=f"{place_name}, {state_abbr} {clean_query}",
                            )
                        )
                        return results
        except Exception as e:
            logger.debug("Zippopotam lookup skipped: %s", e)

    # 2. Query Open-Meteo Geocoding API
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            geo_res = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": clean_query, "count": 6, "language": "en", "format": "json"},
            )
            if geo_res.status_code == 200:
                data = geo_res.json()
                raw_results = data.get("results", [])
                for r in raw_results:
                    city_name = r.get("name", clean_query)
                    admin1 = r.get("admin1")
                    country = r.get("country")
                    country_code = r.get("country_code", "")
                    lat = float(r.get("latitude", 0))
                    lon = float(r.get("longitude", 0))
                    postcodes = r.get("postcodes", [])
                    p_code = postcodes[0] if postcodes else (clean_query if is_zip else None)

                    if country_code.upper() == "US" and admin1:
                        metro_label = f"{city_name.upper()}, {admin1[:2].upper()}"
                    elif admin1:
                        metro_label = f"{city_name.upper()}, {admin1.upper()}"
                    else:
                        metro_label = city_name.upper()

                    display_parts = [city_name]
                    if admin1:
                        display_parts.append(admin1)
                    if country:
                        display_parts.append(country)

                    results.append(
                        GeocodeResult(
                            name=city_name,
                            admin1=admin1,
                            country=country,
                            metro_label=metro_label,
                            latitude=lat,
                            longitude=lon,
                            postal_code=p_code,
                            display_label=", ".join(display_parts),
                        )
                    )

                if results:
                    return results

    except Exception as e:
        logger.debug("Open-Meteo Geocoding query failed: %s", e)

    # 3. Local Popular City Dictionary Fallback
    query_lower = clean_query.lower()
    for key, city in FALLBACK_POPULAR_CITIES.items():
        if (
            query_lower == key
            or query_lower in key
            or key in query_lower
            or query_lower == str(city.get("postal_code", "")).lower()
        ):
            results.append(
                GeocodeResult(
                    name=city["metro_label"].split(",")[0],
                    admin1=city["admin1"],
                    country=city["country"],
                    metro_label=city["metro_label"],
                    latitude=city["latitude"],
                    longitude=city["longitude"],
                    postal_code=city["postal_code"],
                    display_label=f"{city['metro_label']}, {city['country']}",
                )
            )
            return results

    return results
