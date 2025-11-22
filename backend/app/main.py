"""Main FastAPI application entrypoint.

Sets up the API server, configures CORS, logging, health endpoint,
and mounts the plan orchestration endpoint under /api.

Environment variables (.env) supported:
- USER_AGENT: String used for outbound requests to Nominatim/Overpass.
- LOG_LEVEL: Logging level (default: INFO)

Run locally:
    uvicorn app.main:app --reload
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .utils.logging_config import configure_logging, logger
from .api.plan import router as plan_router
from .middleware.rate_limit import RateLimitMiddleware

# Load .env early
load_dotenv()

# Configure structured logging
configure_logging(level=os.getenv("LOG_LEVEL", "INFO"))

app = FastAPI(
    title="Multi-Agent Tourism Orchestrator",
    version="1.0.0",
    description="Tourism planning orchestrator leveraging weather and places agents.",
)

# CORS configuration - restrict to known origins
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:5174").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Mount routers
app.include_router(plan_router, prefix="/api")


@app.get("/health", summary="Health check")
async def health() -> Dict[str, Any]:
    """Simple health endpoint to verify service status."""
    now = datetime.now(timezone.utc).isoformat()
    logger.debug("Health check ping", time=now)
    return {"status": "ok", "time": now}


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("Backend service starting")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    logger.info("Backend service shutting down")
