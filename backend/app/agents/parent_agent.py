"""Parent (orchestrator) agent.

Responsible for:
- Extracting a place name from user text using simple heuristics.
- Detecting intent (weather / places / both).
- Coordinating child agents concurrently (weather + places) and composing
  a structured + natural language response with graceful partial failure.
"""
from __future__ import annotations

import asyncio
import re
from typing import Any, Dict, List, Optional, Set

from ..services.geocode import geocode_place, geocode_top_match, GeocodeResult
from ..utils.logging_config import logger

# Child agent imports (implemented separately)
from .weather_agent import fetch_weather  # type: ignore  # noqa: F401,E402
from .places_agent import fetch_places  # type: ignore  # noqa: F401,E402

PLACE_REGEX = re.compile(r"\b(?:in|at|for|to|about)\s+([A-Z][A-Za-z0-9'\- ]{2,})", re.IGNORECASE)
INTENT_WEATHER_KEYWORDS = {"weather", "temperature", "rain", "sunny", "forecast", "climate", "hot", "cold"}
INTENT_PLACES_KEYWORDS = {"place", "places", "attraction", "attractions", "visit", "tour", "tourist", "poi", "park", "about", "tell", "show"}


def extract_place_from_text(message: str) -> Optional[str]:
    """Attempt to extract a place-like token from the message.

    Heuristic: look for prepositions (in/at/for/to/about) followed by a capitalized
    segment. This is intentionally naive but lightweight.

    If not found, we return None and rely on geocoding attempts in orchestrate.
    """
    match = PLACE_REGEX.search(message)
    if match:
        candidate = match.group(1).strip()
        # Basic cleanup: collapse spaces
        candidate = re.sub(r"\s+", " ", candidate)
        logger.debug("Extracted place heuristic", candidate=candidate)
        return candidate
    
    # Fallback: extract capitalized words that might be place names
    words = message.split()
    capitalized = [w for w in words if w and w[0].isupper() and len(w) > 2]
    if capitalized:
        # Join consecutive capitalized words (e.g., "New York")
        place_candidate = " ".join(capitalized)
        logger.debug("Extracted place from capitalized words", candidate=place_candidate)
        return place_candidate
    
    logger.debug("No heuristic place extracted")
    return None


def detect_intent(message: str) -> Set[str]:
    """Detect user intent for weather / places.

    Returns a set containing any of {"weather", "places"}.
    Defaults to empty set if ambiguous; caller may treat empty as both.
    """
    lowered = message.lower()
    intents: Set[str] = set()
    if any(k in lowered for k in INTENT_WEATHER_KEYWORDS):
        intents.add("weather")
    if any(k in lowered for k in INTENT_PLACES_KEYWORDS):
        intents.add("places")
    logger.debug("Detected intent", intents=list(intents))
    return intents


async def _resolve_place(candidate: Optional[str]) -> Optional[GeocodeResult]:
    """Resolve geocode result for candidate or None if unknown.

    If candidate provided, geocode and return top match. If multiple results
    are returned we still choose the first (disambiguation could be extended
    later). If no candidate, return None.
    """
    if not candidate:
        return None
    try:
        results = await geocode_place(candidate)
        return results[0] if results else None
    except ValueError as exc:
        logger.warning("Geocode failed - place not found", candidate=candidate, error=str(exc))
        return None
    except Exception as exc:  # noqa: BLE001
        logger.error("Geocode failed - unexpected error", candidate=candidate, error=str(exc), error_type=type(exc).__name__)
        return None


async def orchestrate(place_candidate: Optional[str], want: List[str]) -> Dict[str, Any]:
    """Coordinate child agents and compose final response.

    Args:
        place_candidate: Optional place string extracted heuristically.
        want: Ordered list of desired components (subset of ["weather", "places"]).
    Returns:
        Structured dictionary consumed by API layer.
    """
    errors: List[str] = []

    # If no place candidate at all, return friendly error
    if not place_candidate or not place_candidate.strip():
        logger.warning("No place candidate provided")
        return {
            "place": None,
            "lat": None,
            "lon": None,
            "weather": None,
            "places": None,
            "text": "I couldn't identify a destination in your message. Please specify a city or place.",
            "errors": ["No destination specified"],
        }

    geocode: Optional[GeocodeResult] = await _resolve_place(place_candidate)
    if not geocode:
        logger.info("Place unresolved - returning structured error", original=place_candidate)
        return {
            "place": place_candidate,
            "lat": None,
            "lon": None,
            "weather": None,
            "places": None,
            "text": f"I couldn't find '{place_candidate}' on the map. Please check the spelling or try a different location.",
            "errors": [f"Location '{place_candidate}' not found"],
        }

    lat, lon = geocode.lat, geocode.lon
    logger.info("Resolved place", place=geocode.display_name, lat=lat, lon=lon)

    # Prepare tasks based on intent
    tasks = {}
    if "weather" in want:
        tasks["weather"] = asyncio.create_task(_run_weather(lat, lon))
    if "places" in want:
        tasks["places"] = asyncio.create_task(_run_places(lat, lon))

    # Await all with exception capture
    await asyncio.gather(*tasks.values(), return_exceptions=True)

    weather_block: Optional[Dict[str, Any]] = None
    places_block: Optional[List[str]] = None
    places_geo: Optional[List[Dict[str, Any]]] = None

    if "weather" in tasks:
        weather_block = tasks["weather"].result()  # type: ignore[assignment]
    if "places" in tasks:
        raw_places: List[Dict[str, Any]] = tasks["places"].result()  # type: ignore[assignment]
        places_geo = raw_places
        places_block = [p.get("name") for p in raw_places]

    # Compose natural language summary
    summary_parts: List[str] = []

    if weather_block:
        if weather_block.get("error"):
            errors.append(weather_block["error"])
        else:
            temp = weather_block.get("temperature")
            precip = weather_block.get("precipitation_probability")
            if temp is not None and precip is not None:
                summary_parts.append(
                    f"It’s currently {temp:.0f}°C with a {precip}% chance of precipitation."
                )
            elif temp is not None:
                summary_parts.append(f"Current temperature is {temp:.0f}°C.")
    elif "weather" in want:
        errors.append("Weather service unavailable")

    if places_block:
        if places_block:
            listed = ", ".join(places_block)
            summary_parts.append(f"Places you can visit: {listed}.")
    elif "places" in want:
        errors.append("Places service unavailable")

    text_summary = " ".join(summary_parts) if summary_parts else "No data available."

    return {
        "place": geocode.display_name,
        "lat": lat,
        "lon": lon,
        "geocode_source": getattr(geocode, "source", None),
        "weather": weather_block,
        "places": places_block,
        "places_geo": places_geo,
        "text": text_summary,
        "errors": errors or None,
    }


async def _run_weather(lat: float, lon: float) -> Dict[str, Any]:
    """Invoke weather child agent with error handling."""
    try:
        data = await fetch_weather(lat, lon)
        return data
    except Exception as exc:  # noqa: BLE001
        logger.warning("Weather child failure", error=str(exc))
        return {"error": "Weather service temporarily unavailable"}


async def _run_places(lat: float, lon: float) -> List[Dict[str, Any]]:
    """Invoke places child agent with error handling, returning full POI dicts."""
    try:
        data = await fetch_places(lat, lon)
        return data
    except Exception as exc:  # noqa: BLE001
        logger.warning("Places child failure", error=str(exc))
        return []
