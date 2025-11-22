"""Weather child agent.

Fetches weather data via Open-Meteo service helper with retry logic.
Implements exponential backoff on transient failures.
"""
from __future__ import annotations

from typing import Any, Dict

from ..services.open_meteo import fetch_open_meteo
from ..utils.retry import async_retry
from ..utils.logging_config import logger

# Apply retries: 3 attempts exponential backoff base 0.5s -> 0.5, 1.0, 2.0
@async_retry(retries=3, backoff_factor=0.5)
async def fetch_weather(lat: float, lon: float) -> Dict[str, Any]:
    """Fetch weather information for coordinates.

    Args:
        lat: Latitude.
        lon: Longitude.
    Returns:
        Dict with temperature, precipitation_probability, summary.
    """
    logger.debug("Weather agent fetch", lat=lat, lon=lon)
    data = await fetch_open_meteo(lat, lon)
    return data
