from datetime import datetime
import os

__all__ = [
    "datenow_str",
    "timenow_str",
    "get_unique_fname",
]


def datenow_str() -> str:
    """Return the current date and time as a sortable string: YYYYMMDD_HHMMSS."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def timenow_str() -> str:
    """Return the current time as HH:MM:SS.mmm."""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def get_unique_fname(base_name: str, extension: str = "png", verbose: bool = True) -> str:
    """Return a unique filename by appending an index to the base name.

    Args:
        base_name (str): The base name of the file (without extension).
        extension (str, optional): The file extension (default is "png").
        verbose (bool, optional): If True, print the unique filename (default is True).

    Returns:
        str: A unique filename in the format "{base_name}_{index:02d}.{extension}".
    """

    index = 0
    while os.path.exists(f"{base_name}_{index:02d}.{extension}"):
        index += 1
    if verbose:
        print(f"# unique filename: {base_name}_{index:02d}.{extension}")
    return f"{base_name}_{index:02d}.{extension}"
