"""Geocoding service using Nominatim.

Provides an async function `geocode_place` which queries the Nominatim
search endpoint and returns up to 3 candidate matches. Results are
optionally cached via a TTL cache to reduce rate-limit pressure.

Respecting Nominatim usage policy:
- Provide a descriptive User-Agent header.
- Avoid heavy polling (we add caching layer).

Documentation: https://nominatim.org/release-docs/latest/api/Search/
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import asyncio
import os
import time

import httpx

from ..utils.logging_config import logger

# Attempt to import TTL cache decorator (will be created later).
try:  # pragma: no cover - fallback path
    from ..utils.cache import ttl_cache
except Exception:  # noqa: BLE001
    def ttl_cache(ttl_seconds: int = 300):  # type: ignore
        def decorator(func):
            return func
        return decorator


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
# Provide a more descriptive (and policy-compliant) user agent with contact.
DEFAULT_USER_AGENT = os.getenv(
    "USER_AGENT",
    "tourism-orchestrator/1.0 (+https://example.com/contact)"
)

# Simple local fallback cache (key -> (expiry, value)) if decorator not in use.
_fallback_cache: dict[str, tuple[float, List["GeocodeResult"]]] = {}
_FALLBACK_TTL = 300.0

# Alias mappings for legacy / alternate place names (lowercase -> list of variant queries)
ALIAS_MAP: dict[str, List[str]] = {
    "bangalore": ["bengaluru", "bengaluru, india"],
    "bengaluru": ["bengaluru, india", "bengaluru, karnataka"],
    "bombay": ["mumbai", "mumbai, india"],
    "calcutta": ["kolkata", "kolkata, india"],
    "madras": ["chennai", "chennai, india"],
    "peking": ["beijing", "beijing, china"],
    "saigon": ["ho chi minh city", "ho chi minh city, vietnam"],
    "paris": ["paris, france"],
    "london": ["london, uk", "london, united kingdom"],
    "tokyo": ["tokyo, japan"],
    "new york": ["new york, usa", "new york city"],
    "goa": ["goa, india"],
}

# Static coordinate fallback (for offline / blocked geocoding scenarios). We store
# tuples first because GeocodeResult is defined later; we convert lazily.
STATIC_FALLBACK_RAW: dict[str, tuple[str, float, float]] = {
    "bengaluru": ("Bengaluru, India", 12.9716, 77.5946),
    "bangalore": ("Bengaluru, India", 12.9716, 77.5946),
    "goa": ("Goa, India", 15.2993, 74.1240),
    "mumbai": ("Mumbai, India", 19.0760, 72.8777),
    "delhi": ("Delhi, India", 28.6139, 77.2090),
    "paris": ("Paris, France", 48.8566, 2.3522),
    "london": ("London, United Kingdom", 51.5072, -0.1276),
    "tokyo": ("Tokyo, Japan", 35.6762, 139.6503),
    "new york": ("New York City, USA", 40.7128, -74.0060),
}

def _static_result(key: str) -> Optional["GeocodeResult"]:
    raw = STATIC_FALLBACK_RAW.get(key)
    if not raw:
        return None
    name, lat, lon = raw
    return GeocodeResult(display_name=name, lat=lat, lon=lon, source="static")


@dataclass(slots=True)
class GeocodeResult:
    """Structured geocode result with origin source."""
    display_name: str
    lat: float
    lon: float
    source: str = "nominatim"

    def as_dict(self) -> dict:
        return {"display_name": self.display_name, "lat": self.lat, "lon": self.lon}


async def _perform_request(query: str) -> List[GeocodeResult]:
    """Execute the HTTP request to Nominatim and parse results.

    Args:
        query: Free-text place query.
    Returns:
        List of up to 3 GeocodeResult instances.
    Raises:
        ValueError: If no matches returned.
    """
    params = {
        "q": query,
        "format": "json",
        "addressdetails": 0,
        "limit": 5,  # fetch a few to filter duplicates
    }

    headers = {
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": "application/json",
    }

    logger.info("Geocode request", query=query)
    attempts = 3
    backoff = 0.5
    data = None
    last_exc: Optional[Exception] = None
    async with httpx.AsyncClient(timeout=10.0) as client:
        for attempt in range(1, attempts + 1):
            try:
                resp = await client.get(NOMINATIM_URL, params=params, headers=headers)
                if resp.status_code == 429:
                    raise ValueError("Rate limited by geocoding provider")
                resp.raise_for_status()
                data = resp.json()
                logger.info("Geocode response received", status=resp.status_code, attempt=attempt)
                break
            except Exception as exc:
                last_exc = exc
                logger.warning("Geocode attempt failed", query=query, attempt=attempt, error=str(exc))
                if attempt < attempts:
                    await asyncio.sleep(backoff)
                    backoff *= 2
    if data is None:
        raise ValueError(f"Geocoding service error: {last_exc}")

    # Validate response shape
    if not isinstance(data, list):
        logger.error("Unexpected geocode response type", query=query, response=data)
        raise ValueError("Geocoding service returned unexpected data shape")
    if not data:
        raise ValueError("I don’t know this place exists.")

    results: List[GeocodeResult] = []
    seen_names: set[str] = set()
    for item in data:
        name = item.get("display_name")
        if not name or name in seen_names:
            continue
        seen_names.add(name)
        try:
            lat = float(item.get("lat"))
            lon = float(item.get("lon"))
        except (TypeError, ValueError):
            continue
        results.append(GeocodeResult(display_name=name, lat=lat, lon=lon, source="nominatim"))
        if len(results) >= 3:
            break

    if not results:
        raise ValueError("I don’t know this place exists.")
    logger.info("Geocode parsed", count=len(results))
    return results


@ttl_cache(ttl_seconds=300)
async def geocode_place(query: str) -> List[GeocodeResult]:
    """Public geocode function with TTL caching.

    If caching decorator not available yet, fallback to minimal internal cache.

    Args:
        query: Free-text place query.
    Returns:
        Up to 3 geocode candidate results.
    """
    key = query.strip().lower()
    if not key:
        raise ValueError("Empty geocode query")

    # Fallback manual cache path (only used if decorator stubbed)
    if ttl_cache.__name__ == "geocode_place":  # type: ignore[attr-defined]
        now = time.time()
        cached = _fallback_cache.get(key)
        if cached and cached[0] > now:
            logger.debug("Geocode fallback cache hit", query=query)
            return cached[1]
        results = await _perform_request(query)
        _fallback_cache[key] = (now + _FALLBACK_TTL, results)
        return results

    # Normal path (decorator will have cached if previously called)
    try:
        return await _perform_request(query)
    except ValueError as original_err:
        aliases = ALIAS_MAP.get(key, [])
        if not aliases:
            static = _static_result(key)
            if static:
                logger.warning("Using static geocode fallback", query=query)
                return [static]
            raise original_err
        logger.info("Geocode alias fallback", original=query, variants=aliases)
        for variant in aliases:
            try:
                results = await _perform_request(variant)
                if results:
                    return results
            except ValueError:
                continue
        static = _static_result(key)
        if static:
            logger.warning("Using static geocode fallback after alias failures", query=query)
            return [static]
        raise ValueError("I don’t know this place exists.")


async def geocode_top_match(query: str) -> Optional[GeocodeResult]:
    """Helper returning only top (first) match or None."""
    try:
        results = await geocode_place(query)
        return results[0] if results else None
    except ValueError:
        return None
