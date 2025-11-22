"""Places child agent.

Fetches tourist points of interest using Overpass with radius expansion
retry if initial results fewer than desired limit.
"""
from __future__ import annotations

from typing import Any, Dict, List

from ..services.overpass import fetch_pois
from ..utils.cache import ttl_cache
from ..utils.retry import async_retry
from ..utils.logging_config import logger

DEFAULT_RADIUS = 5000  # meters
RADIUS_EXPANSION_FACTOR = 2
MAX_EXPANSIONS = 1
POI_LIMIT = 5


@ttl_cache(ttl_seconds=600)
@async_retry(retries=3, backoff_factor=0.4)
async def _fetch(lat: float, lon: float, radius: int, limit: int) -> List[Dict[str, Any]]:
    return await fetch_pois(lat, lon, radius=radius, limit=limit)


async def fetch_places(lat: float, lon: float, radius: int = DEFAULT_RADIUS, limit: int = POI_LIMIT) -> List[Dict[str, Any]]:
    """Fetch places with minimal retry plus radius expansion if needed.

    Args:
        lat: Latitude.
        lon: Longitude.
        radius: Initial search radius.
        limit: Desired number of POIs.
    Returns:
        List of POI dicts with 'name' and optional 'category'.
    """
    current_radius = radius
    expansions = 0
    all_places: List[Dict[str, Any]] = []

    while expansions <= MAX_EXPANSIONS:
        logger.debug("Places fetch attempt", radius=current_radius, expansions=expansions)
        try:
            places = await _fetch(lat, lon, current_radius, limit)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Places fetch error", error=str(exc))
            places = []
        # Deduplicate across expansions
        dedup: Dict[str, Dict[str, Any]] = {p["name"]: p for p in (all_places + places) if p.get("name")}
        all_places = list(dedup.values())
        if len(all_places) >= limit:
            break
        current_radius *= RADIUS_EXPANSION_FACTOR
        expansions += 1

    # Truncate to limit
    all_places = all_places[:limit]
    logger.debug("Places final", count=len(all_places))
    return all_places
