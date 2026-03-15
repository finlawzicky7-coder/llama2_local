"""Centralised logging configuration for CREBrokerAI."""

from __future__ import annotations

import logging
import sys

from rich.logging import RichHandler


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Return the package-level logger with Rich handler."""
    logger = logging.getLogger("crebrokerai")
    if not logger.handlers:
        handler = RichHandler(rich_tracebacks=True, show_path=False)
        handler.setFormatter(logging.Formatter("%(message)s", datefmt="[%X]"))
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a child logger under the crebrokerai namespace."""
    setup_logging()
    return logging.getLogger(f"crebrokerai.{name}")
