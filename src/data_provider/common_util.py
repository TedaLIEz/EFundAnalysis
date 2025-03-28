
import typing
from datetime import datetime

def get_date() -> str:
    """
    Get the current date in the format YYYY-MM-DD
    """
    return datetime.now().strftime("%Y-%m-%d")