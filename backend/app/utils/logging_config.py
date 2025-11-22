"""Structured logging configuration using loguru.

Provides a global `logger` instance and setup function to configure
JSON-like structured logs suitable for cloud deployment debugging.
"""
from __future__ import annotations

import json
import sys
from typing import Any, Dict
from loguru import logger as _logger


def _serialize(record: Dict[str, Any]) -> str:
    base = {
        "time": record["time"].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
    }
    if record.get("extra"):
        base.update(record["extra"])  # type: ignore[arg-type]
    if record.get("exception"):
        base["exception"] = str(record["exception"])
    return json.dumps(base, ensure_ascii=False)


def configure_logging(level: str = "INFO") -> None:
    """Configure global logger sink and level."""
    _logger.remove()
    _logger.add(sys.stderr, level=level.upper(), format="{message}", enqueue=True, serialize=False, backtrace=False, diagnose=False, filter=None)
    # Wrap to produce JSON lines
    def patching(record):  # type: ignore[override]
        record["message"] = _serialize(record)
    _logger.configure(patcher=patching)


logger = _logger
