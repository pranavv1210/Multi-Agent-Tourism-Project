"""Plan API router.

Exposes POST /api/plan accepting a natural-language message and returns a
structured tourism planning response composed by the parent agent.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field

from ..agents.parent_agent import (
    extract_place_from_text,
    detect_intent,
    orchestrate,
)
from ..utils.logging_config import logger

router = APIRouter(tags=["plan"])


@router.options("/plan")
async def plan_options():
    """Handle CORS preflight for /api/plan endpoint."""
    return Response(status_code=200)


class PlanRequest(BaseModel):
    """Incoming request payload for the planning endpoint."""
    message: str = Field(
        ..., 
        min_length=2, 
        max_length=500,
        description="User natural language message",
        example="Weather and places in Paris"
    )
    intents: Optional[List[str]] = Field(
        None,
        description="Explicit list of requested intent blocks (weather / places). If omitted, heuristics decide."
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "I'm going to Bangalore, what's the weather?",
                "intents": ["weather", "places"]
            }
        }


class WeatherPayload(BaseModel):
    temperature: Optional[float] = Field(None, description="Current temperature in °C")
    precipitation_probability: Optional[int] = Field(
        None, description="Precipitation probability (%) matched to current hour"
    )
    summary: Optional[str] = Field(None, description="Short weather summary if available")
    forecast: Optional[List[Dict[str, Any]]] = Field(None, description="7-day weather forecast")
    error: Optional[str] = Field(None, description="Weather retrieval error (if partial)")


class PlanResponse(BaseModel):
    place: Optional[str] = Field(None, description="Resolved place display name")
    lat: Optional[float] = Field(None, description="Latitude of resolved place")
    lon: Optional[float] = Field(None, description="Longitude of resolved place")
    geocode_source: Optional[str] = Field(None, description="Origin of geocode data (nominatim|static)")
    intents: Optional[List[str]] = Field(None, description="List of requested intents (weather/places)")
    weather: Optional[WeatherPayload] = Field(None, description="Weather data block")
    places: Optional[List[str]] = Field(None, description="List of POI names")
    places_geo: Optional[List[Dict[str, Any]]] = Field(
        None, description="Detailed POI entries with coordinates"
    )
    text: Optional[str] = Field(None, description="Composed natural language summary")
    errors: Optional[List[str]] = Field(None, description="List of non-fatal errors")


@router.post("/plan", response_model=PlanResponse, summary="Create tourism plan")
async def plan(request: PlanRequest) -> PlanResponse:
    """Primary planning entrypoint.

    Steps:
    1. Extract candidate place from text.
    2. Detect intent (weather, places, both).
    3. Orchestrate child agent calls concurrently.
    4. Compose natural-language response plus structured JSON.
    """
    message = request.message.strip()
    if not message:
        raise HTTPException(
            status_code=400, 
            detail="🗺️ Please enter a destination to plan your trip"
        )

    logger.info("Received planning request", message=message)

    try:
        place_candidate: Optional[str] = extract_place_from_text(message)
        # If no heuristic match, try using the entire message as place candidate
        if not place_candidate:
            place_candidate = message
            logger.debug("Using entire message as place candidate", candidate=message)
        
        if request.intents:
            intent = {i for i in request.intents if i in {"weather", "places"}}
        else:
            intent = detect_intent(message)
        if not intent:
            # Default to both if user ambiguous
            intent = {"weather", "places"}

        result: Dict[str, Any] = await orchestrate(place_candidate, sorted(intent))
    except ValueError as exc:
        # User-facing errors (e.g., geocoding failures)
        logger.warning("User error during planning", error=str(exc))
        raise HTTPException(
            status_code=400,
            detail=f"🌍 {str(exc)}"
        ) from exc
    except Exception as exc:
        # System errors
        logger.exception("Planning orchestration failed")
        error_msg = "⚠️ Our travel planning service is temporarily unavailable. Please try again in a moment."
        raise HTTPException(status_code=500, detail=error_msg) from exc

    weather_block: Optional[WeatherPayload] = None
    if "weather" in result:
        wb = result.get("weather") or {}
        weather_block = WeatherPayload(
            temperature=wb.get("temperature"),
            precipitation_probability=wb.get("precipitation_probability"),
            summary=wb.get("summary"),
            forecast=wb.get("forecast"),
            error=wb.get("error"),
        )

    response = PlanResponse(
        place=result.get("place"),
        lat=result.get("lat"),
        lon=result.get("lon"),
        geocode_source=result.get("geocode_source"),
        intents=sorted(intent),
        weather=weather_block,
        places=result.get("places"),
        places_geo=result.get("places_geo"),
        text=result.get("text"),
        errors=result.get("errors"),
    )

    logger.info(
        "Responding planning result",
        place=response.place,
        lat=response.lat,
        lon=response.lon,
        have_weather=bool(response.weather),
        places_count=len(response.places or []),
        errors=response.errors,
    )
    return response
