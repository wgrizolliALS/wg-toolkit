from datetime import datetime
import os

__all__ = [
    "datenow",
    "datenow_str",
    "timenow",
    "timenow_str",
    "get_unique_fname",
]

def datenow() -> str:
    """Return the current date and time as a sortable string: YYYY:MM:DD HH:MM:SS."""
    return datetime.now().strftime("%Y:%m:%d %H:%M:%S")

def datenow_str() -> str:
    """Return the current date and time as a sortable string: YYYYMMDD_HHMMSS."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def timenow() -> str:
    """Return the current time as HH:MM:SS.mmm."""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def timenow_str() -> str:
    """Return the current time as HHMMSS.mmm."""
    return datetime.now().strftime("%H%M%S.%f")[:-3]


def get_unique_fname(base_name: str, extension: str = "png", time_prefix: bool = True, verbose: bool = True) -> str:
    """Return a unique filename by appending an index to the base name.

    Args:
        base_name (str): The base name of the file (without extension).
        extension (str, optional): The file extension (default is "png").
        time_prefix (bool, optional): If True, prepend the current date and time to the filename (default is True).
        verbose (bool, optional): If True, print the unique filename (default is True).

    Returns:
        str: A unique filename in the format "{base_name}_{index:02d}.{extension}".
    """

    os.makedirs(base_name.rsplit("\\", 1)[0], exist_ok=True)

    if time_prefix:
        _name_splitted = base_name.rsplit("\\", 1)
        _name_splitted[-1] = f"{datenow_str()}_{_name_splitted[-1]}"
        base_name = "\\".join(_name_splitted)
        return base_name + f".{extension}"
    else:
        index = 0
        while os.path.exists(f"{base_name}_{index:02d}.{extension}"):
            index += 1
        if verbose:
            print(f"# unique filename: {base_name}_{index:02d}.{extension}")
        return f"{base_name}_{index:02d}.{extension}"
