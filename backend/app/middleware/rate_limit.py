"""Simple in-memory rate limiter middleware.

Prevents API abuse by limiting requests per IP address.
Production should use Redis or similar distributed cache.
"""
from __future__ import annotations

import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

# Configuration
RATE_LIMIT_REQUESTS = 30  # requests
RATE_LIMIT_WINDOW = 60    # seconds (1 minute)

# In-memory storage: {ip_address: [(timestamp, ...), ...]}
_request_log: dict[str, list[float]] = defaultdict(list)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window counter."""

    async def dispatch(self, request: Request, call_next: Callable):
        """Check rate limit before processing request."""
        # Skip rate limiting for health endpoint
        if request.url.path == "/health":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old requests outside the window
        _request_log[client_ip] = [
            ts for ts in _request_log[client_ip]
            if current_time - ts < RATE_LIMIT_WINDOW
        ]
        
        # Check if limit exceeded
        if len(_request_log[client_ip]) >= RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds.",
                headers={"Retry-After": str(RATE_LIMIT_WINDOW)}
            )
        
        # Log this request
        _request_log[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = RATE_LIMIT_REQUESTS - len(_request_log[client_ip])
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + RATE_LIMIT_WINDOW))
        
        return response
