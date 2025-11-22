"""Open-Meteo weather service helpers.

This module provides an async function to query the Open-Meteo API for
current weather and hourly precipitation probability, then match the
current weather timestamp to the appropriate hourly precipitation value.

Endpoint docs: https://open-meteo.com/en/docs

The weather agent will apply a retry decorator; this module focuses on
request construction and parsing only.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
import httpx

from ..utils.logging_config import logger

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
DEFAULT_TIMEZONE = "Asia/Kolkata"

# Mapping from Open-Meteo weather codes to simple summaries.
# Reference: https://open-meteo.com/en/docs#weathervariables
WEATHER_CODE_MAP: Dict[int, str] = {
    0: "Clear",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    56: "Light Freezing Drizzle",
    57: "Dense Freezing Drizzle",
    61: "Slight Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    66: "Light Freezing Rain",
    67: "Heavy Freezing Rain",
    71: "Slight Snowfall",
    73: "Moderate Snowfall",
    75: "Heavy Snowfall",
    77: "Snow Grains",
    80: "Slight Rain Showers",
    81: "Moderate Rain Showers",
    82: "Violent Rain Showers",
    85: "Slight Snow Showers",
    86: "Heavy Snow Showers",
    95: "Thunderstorm",
    96: "Thunderstorm With Slight Hail",
    99: "Thunderstorm With Heavy Hail",
}


def _extract_precip_probability(data: Dict[str, Any]) -> Optional[int]:
    """Match current hour's precipitation probability.

    The response includes `current_weather.time` (ISO) and hourly arrays:
    `hourly.time` and `hourly.precipitation_probability`.

    We find the index in `hourly.time` that exactly matches `current_weather.time`.
    If match found and precipitation probability present, return int value.

    Args:
        data: Parsed JSON response from Open-Meteo.
    Returns:
        Precipitation probability percentage or None if not found.
    """
    try:
        current_time: str = data["current_weather"]["time"]
        times = data["hourly"]["time"]
        probs = data["hourly"]["precipitation_probability"]
    except (KeyError, TypeError):
        return None

    if not (isinstance(times, list) and isinstance(probs, list)):
        return None

    try:
        idx = times.index(current_time)
    except ValueError:
        logger.debug("Current time not found in hourly time array", current_time=current_time)
        return None

    if idx < 0 or idx >= len(probs):
        return None
    val = probs[idx]
    if val is None:
        return None
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def _weather_summary(data: Dict[str, Any]) -> Optional[str]:
    """Resolve a human-friendly summary from weathercode if present."""
    try:
        code = int(data["current_weather"]["weathercode"])
    except (KeyError, TypeError, ValueError):
        return None
    return WEATHER_CODE_MAP.get(code)


async def fetch_open_meteo(lat: float, lon: float, timezone: str = DEFAULT_TIMEZONE) -> Dict[str, Any]:
    """Fetch current weather and precipitation probability for coordinates.

    Args:
        lat: Latitude.
        lon: Longitude.
        timezone: Timezone string for alignment (defaults Asia/Kolkata).
    Returns:
        Dict with fields: temperature, precipitation_probability, summary, forecast (7-day).
        On partial failures, missing fields may be None.
    Raises:
        httpx.HTTPError for network / protocol issues.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "hourly": "precipitation_probability",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode",
        "forecast_days": 7,
        "timezone": timezone,
    }

    logger.debug("Open-Meteo request", lat=lat, lon=lon, timezone=timezone)
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(OPEN_METEO_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    temperature: Optional[float] = None
    try:
        temperature = float(data["current_weather"]["temperature"])
    except (KeyError, TypeError, ValueError):
        logger.debug("Temperature missing in response")

    precipitation_probability = _extract_precip_probability(data)
    summary = _weather_summary(data)
    
    # Extract 7-day forecast
    forecast = []
    try:
        daily_data = data.get("daily", {})
        times = daily_data.get("time", [])
        max_temps = daily_data.get("temperature_2m_max", [])
        min_temps = daily_data.get("temperature_2m_min", [])
        precip_probs = daily_data.get("precipitation_probability_max", [])
        weather_codes = daily_data.get("weathercode", [])
        
        for i in range(min(7, len(times))):
            forecast.append({
                "date": times[i],
                "temp_max": max_temps[i] if i < len(max_temps) else None,
                "temp_min": min_temps[i] if i < len(min_temps) else None,
                "precipitation_probability": precip_probs[i] if i < len(precip_probs) else None,
                "summary": WEATHER_CODE_MAP.get(int(weather_codes[i]), "Unknown") if i < len(weather_codes) and weather_codes[i] is not None else None,
            })
    except Exception as exc:
        logger.debug("Forecast extraction failed", error=str(exc))

    result = {
        "temperature": temperature,
        "precipitation_probability": precipitation_probability,
        "summary": summary,
        "forecast": forecast if forecast else None,
    }
    logger.debug("Open-Meteo parsed", **{k: v for k, v in result.items() if k != 'forecast'})
    return result
