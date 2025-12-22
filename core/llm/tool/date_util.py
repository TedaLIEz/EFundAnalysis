"""Date utility functions for use as llama-index function tools."""

from datetime import date


def get_current_date() -> str:
    """Get the current date in ISO format (YYYY-MM-DD).

    Returns:
        The current date as a string in ISO format (YYYY-MM-DD).

    Example:
        >>> get_current_date()
        '2024-01-15'

    """
    return date.today().isoformat()
