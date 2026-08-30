"""Structured logging configuration."""

import logging
import sys
from backend.app.core.config import settings


def setup_logging() -> logging.Logger:
    """Configure application logging formatting and log level."""
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    logger = logging.getLogger("openprevue")
    logger.setLevel(level)
    return logger


logger = setup_logging()
