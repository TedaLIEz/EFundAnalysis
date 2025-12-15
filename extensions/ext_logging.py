import logging


def init_logging(level: int = logging.INFO) -> None:
    """Initialize logging configuration for the application.

    Args:
        level: Logging level (default: logging.INFO)

    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
