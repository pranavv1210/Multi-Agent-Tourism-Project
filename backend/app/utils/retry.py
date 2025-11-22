"""Retry utilities with exponential backoff for async functions."""
from __future__ import annotations

import asyncio
from functools import wraps
from typing import Any, Callable, Type

DEFAULT_EXCEPTIONS: tuple[Type[Exception], ...] = (Exception,)


def async_retry(retries: int = 3, backoff_factor: float = 0.5, exceptions: tuple[Type[Exception], ...] = DEFAULT_EXCEPTIONS) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Retry decorator for async functions.

    Args:
        retries: Number of attempts (total including first).
        backoff_factor: Base multiplier for exponential backoff.
        exceptions: Tuple of exception types to catch.
    Returns:
        Wrapped coroutine function with retry logic.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if not asyncio.iscoroutinefunction(func):  # pragma: no cover
            raise TypeError("async_retry requires an async function")

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            last_exc: Exception | None = None
            while attempt < retries:
                try:
                    return await func(*args, **kwargs)
                except exceptions as exc:  # noqa: BLE001
                    last_exc = exc
                    attempt += 1
                    if attempt >= retries:
                        raise
                    sleep_for = backoff_factor * (2 ** (attempt - 1))
                    await asyncio.sleep(sleep_for)
            if last_exc:
                raise last_exc

        return wrapper

    return decorator
