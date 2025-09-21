from __future__ import annotations

import logging
import sys
from logging import Logger
from typing import Any, Dict

from pythonjsonlogger.json import JsonFormatter

from app.config.settings import AppEnv, Settings


def _json_formatter(extra_fields: Dict[str, Any] | None = None) -> logging.Formatter:
    fields = [
        "asctime",
        "levelname",
        "name",
        "message",
    ]
    if extra_fields:
        fields.extend(extra_fields.keys())
    fmt = " ".join([f"%({f})s" for f in fields])
    return JsonFormatter(fmt)


def configure_logging(settings: Settings) -> Logger:
    logger = logging.getLogger()
    logger.handlers.clear()

    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)

    if settings.env == AppEnv.local:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    elif settings.env == AppEnv.gcp:
        formatter = _json_formatter({"severity": None, "environment": settings.env})
    elif settings.env == AppEnv.aws or settings.env == AppEnv.cloud:
        formatter = _json_formatter({"env": settings.env})
    else:
        formatter = logging.Formatter("%(levelname)s: %(message)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logging.getLogger("uvicorn").setLevel(level)
    logging.getLogger("uvicorn.error").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(level)

    return logger
