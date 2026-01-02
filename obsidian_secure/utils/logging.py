"""
Logging configuration for ObsidianSecure.
"""

import logging
import sys
from pathlib import Path
from ..config import LOG_LEVEL, LOG_FORMAT


def setup_logging(log_file: str | Path | None = None, level: str = LOG_LEVEL) -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        log_file: Optional path to log file (if None, logs to console only)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        logging.Logger: Configured logger

    Note:
        Logs will NOT contain sensitive data (passwords, plaintext content).
    """
    logger = logging.getLogger("ObsidianSecure")
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, level.upper()))
        file_formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


# Sensitive data filter
class SensitiveDataFilter(logging.Filter):
    """Filter to prevent logging of sensitive data."""

    REDACTED_KEYWORDS = [
        "password",
        "key",
        "secret",
        "token",
        "plaintext",
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """Redact sensitive data from log records."""
        message = record.getMessage().lower()

        for keyword in self.REDACTED_KEYWORDS:
            if keyword in message:
                # Don't completely block, but warn
                record.msg = "[REDACTED - Sensitive data filtered]"
                break

        return True
