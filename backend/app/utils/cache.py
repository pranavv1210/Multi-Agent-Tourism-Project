"""Simple TTL caching utilities.

Provides a lightweight async-capable decorator `ttl_cache` storing results
in-memory keyed by function name + arguments. Not thread-safe but adequate
for demo usage to reduce external API calls.
"""
from __future__ import annotations

from functools import wraps
from typing import Any, Awaitable, Callable, Dict, Tuple
import time

CacheKey = Tuple[str, Tuple[Any, ...], Tuple[Tuple[str, Any], ...]]

_store: Dict[CacheKey, Tuple[float, Any]] = {}


def _make_key(func: Callable[..., Any], args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> CacheKey:
    kw_items = tuple(sorted(kwargs.items()))
    return (func.__qualname__, args, kw_items)


def ttl_cache(ttl_seconds: int = 300) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Cache decorator supporting sync or async callables.

    Args:
        ttl_seconds: Time-to-live for cached entries.
    Returns:
        Wrapped callable using in-memory TTL cache.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            key = _make_key(func, args, kwargs)
            now = time.time()
            entry = _store.get(key)
            if entry and entry[0] > now:
                # Return cached result (not coroutine)
                return entry[1]
            # Execute async function and cache the result
            result = await func(*args, **kwargs)
            _store[key] = (now + ttl_seconds, result)
            return result

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            key = _make_key(func, args, kwargs)
            now = time.time()
            entry = _store.get(key)
            if entry and entry[0] > now:
                return entry[1]
            result = func(*args, **kwargs)
            _store[key] = (now + ttl_seconds, result)
            return result

        # Detect async function properly using asyncio.iscoroutinefunction
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
