# app/core/logging.py
"""
Logging helpers.

Call configure_logging() during app startup to set a consistent logging format.
"""

import logging
from .config import settings


def configure_logging() -> None:
    """
    Configure the root logger using the LOG_LEVEL defined in settings.
    """
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    logging.basicConfig(level=level, format=fmt)
