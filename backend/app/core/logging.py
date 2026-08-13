"""Structured logging configuration."""

import logging
import sys

import structlog

from app.config.settings import Settings


def configure_logging(settings: Settings) -> None:
    """Configure standard-library and structlog processors once at startup."""
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=settings.log_level.upper())
    structlog.configure(
        processors=[*shared_processors, structlog.processors.JSONRenderer()],
        wrapper_class=structlog.make_filtering_bound_logger(settings.log_level.upper()),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
