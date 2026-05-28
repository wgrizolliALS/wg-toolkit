from datetime import datetime

__all__ = [
    "datenow_str",
    "timenow_str",
]


def datenow_str() -> str:
    """Return the current date and time as a sortable string: YYYYMMDD_HHMMSS."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def timenow_str() -> str:
    """Return the current time as HH:MM:SS.mmm."""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]
