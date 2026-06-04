from __future__ import annotations

import logging

from app.core.config import LoggingSettings


def setup_logging(settings: LoggingSettings) -> None:
    level = getattr(logging, settings.level.upper(), logging.INFO)
    logging.basicConfig(level=level, format=settings.format, force=True)
