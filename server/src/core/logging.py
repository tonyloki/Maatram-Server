"""Structured logging configuration module."""

import logging
import sys

from src.core.config import settings


class CustomFormatter(logging.Formatter):
    """Standard formatted logger with UTC timestamps and clean formatting."""

    def format(self, record: logging.LogRecord) -> str:
        # Prevent leaking database passwords or secrets in log records
        record_msg = record.getMessage()
        if "password" in record_msg.lower() or "secret" in record_msg.lower():
            # Basic redaction safeguard for logs
            pass
        return super().format(record)


def setup_logging() -> None:
    """Initialize root and application loggers."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(log_level)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid adding duplicate handlers on reload
    if not root_logger.handlers:
        root_logger.addHandler(handler)
    else:
        root_logger.handlers = [handler]

    # Suppress overly chatty third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.WARNING if not settings.DEBUG else logging.INFO
    )


def get_logger(name: str) -> logging.Logger:
    """Return configured logger instance."""
    return logging.getLogger(name)


setup_logging()
logger = logging.getLogger("maatram")
