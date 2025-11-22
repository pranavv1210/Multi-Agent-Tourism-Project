"""Overpass API service helpers.

Provides async query functionality to fetch tourist-related POIs near a
coordinate. We focus on priority tags: tourism=attraction, leisure=park,
historic=* while filtering unnamed nodes.

Documentation: https://wiki.openstreetmap.org/wiki/Overpass_API
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import httpx

from ..utils.logging_config import logger

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Tag filters chosen for common tourist points of interest.
PRIORITY_FILTERS = [
    "nwr[tourism=attraction]",
    "nwr[leisure=park]",
    "nwr[historic]",
]


def build_overpass_query(lat: float, lon: float, radius: int) -> str:
        """Construct a valid Overpass QL query string.

        Previous implementation concatenated filters then appended a single
        (around:..) clause resulting in invalid syntax. Correct form repeats
        the (around) for each clause inside the union.
        """
        lines = [
                f"{f}(around:{radius},{lat},{lon});" for f in PRIORITY_FILTERS
        ]
        union_block = "\n      ".join(lines)
        query = f"""
        [out:json][timeout:25];
        (
            {union_block}
        );
        out center;
        """.strip()
        logger.debug("Overpass query built", radius=radius, lat=lat, lon=lon)
        return query


async def execute_overpass(query: str) -> Dict[str, Any]:
    """Execute Overpass POST request and return parsed JSON.

    Raises httpx.HTTPError for network-level issues.
    """
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"data": query}
    logger.debug("Overpass request dispatch")
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(OVERPASS_URL, data=data, headers=headers)
        resp.raise_for_status()
        return resp.json()


def parse_overpass_elements(data: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
    """Parse Overpass JSON elements extracting name + category.

    Args:
        data: Raw JSON dict.
        limit: Maximum number of POIs to return.
    Returns:
        List of dicts with 'name' and 'category'.
    """
    elements = data.get("elements", [])
    results: List[Dict[str, Any]] = []
    seen_names: set[str] = set()

    for el in elements:
        tags: Optional[Dict[str, Any]] = el.get("tags")
        if not tags:
            continue
        # name precedence: name, name:en
        name = tags.get("name") or tags.get("name:en")
        if not name:
            continue
        if name in seen_names:
            continue
        seen_names.add(name)

        category = None
        for key in ("tourism", "leisure", "historic"):
            if key in tags:
                category = f"{key}:{tags[key]}"
                break

        # Extract coordinates (node: lat/lon; way/relation: center)
        lat_val: Optional[float] = None
        lon_val: Optional[float] = None
        if "lat" in el and "lon" in el:
            try:
                lat_val = float(el["lat"])
                lon_val = float(el["lon"])
            except (TypeError, ValueError):
                lat_val = None
                lon_val = None
        elif "center" in el and isinstance(el.get("center"), dict):
            c = el["center"]
            try:
                lat_val = float(c.get("lat"))
                lon_val = float(c.get("lon"))
            except (TypeError, ValueError):
                lat_val = None
                lon_val = None

        results.append({"name": name, "category": category, "lat": lat_val, "lon": lon_val})
        if len(results) >= limit:
            break

    logger.debug("Overpass parsed", count=len(results))
    return results


async def fetch_pois(lat: float, lon: float, radius: int, limit: int = 5) -> List[Dict[str, Any]]:
    """High-level convenience function to fetch POIs.

    If fewer than limit results are found, the caller may decide to expand radius
    and retry (handled by places agent).
    """
    query = build_overpass_query(lat, lon, radius)
    data = await execute_overpass(query)
    return parse_overpass_elements(data, limit=limit)
