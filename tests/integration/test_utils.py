"""Shared utilities for integration tests."""

import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """Set up logging configuration for integration tests.

    This function can be called from pytest conftest.py or from test main() functions.
    It will only configure logging if it hasn't been configured yet.

    Args:
        level: Logging level (default: logging.INFO)
    """
    # Check if logging is already configured
    if logging.getLogger().handlers:
        # Logging already configured, just set the level
        logging.getLogger().setLevel(level)
        return

    # Configure logging to output to console
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True,
    )

    # Set specific loggers to desired levels if needed
    # Reduce verbosity of third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
