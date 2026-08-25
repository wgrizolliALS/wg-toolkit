# ruff: noqa: DTZ005

from datetime import datetime
from pathlib import Path

from .logprint import *

__all__ = [
    "datenow",
    "datenow_str",
    "get_unique_fname",
    "mkdir_dated",
    "print_path",
    "select_file_interactive",
    "timenow",
    "timenow_str",
]


def print_path(path: str | Path) -> None:
    """Print the given path as a URI."""
    print(Path(path).as_uri())


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


def mkdir_dated(
    base_path: str,
    addTime: bool = False,
    suffix: str = "",
    prefix: str = "",
    verbose: bool = True,
) -> str:
    """Create a folder with the current date in the format YYYYMMDD or YYYYMMDD_HHMMSS.

    Parameters
    ----------
    base_path : str
        The base path where the date folder will be created.
    addTime : bool, optional
        If True, include the current time in the folder name. Default is False.

    Returns
    -------
    str
        The full path to the created date folder.

    See Also
    --------
    wg_toolkit.misc.get_unique_fname: Return a unique filename by appending an index to the base name.

    """
    if addTime:
        date_folder = (
            Path(base_path)
            / f"{prefix}{datetime.now().strftime('%Y%m%d_%H%M%S')}{suffix}"
        )
    else:
        date_folder = (
            Path(base_path) / f"{prefix}{datetime.now().strftime('%Y%m%d')}{suffix}"
        )

    if date_folder.exists():
        print_warning(f"Directory already exists: {date_folder}", verbose=verbose)
    else:
        print_log(f"Creating directory: {date_folder}", verbose=verbose)
        date_folder.mkdir(parents=True, exist_ok=True)
    return str(date_folder)


def get_unique_fname(
    base_name: str,
    extension: str = "png",
    base_path: str = "",
    time_prefix: bool = False,
    create_folder: bool = False,
    verbose: bool = False,
) -> str:
    """Return a unique filename by appending an index to the base name.

    Parameters
    ----------
    base_name : str
        The base name of the file (without extension).
    extension : str, optional
        The file extension. Default is ``"png"``.
    base_path : str, optional
        The base path where the file will be saved.
    time_prefix : bool, optional
        If True, prepend the current date and time to the filename.
    create_folder : bool, optional
        If True, create the parent directory if it doesn't exist.
    verbose : bool, optional
        If True, print the unique filename.

    Returns
    -------
    str
        A unique filename in the format ``"{base_name}_{index:02d}.{extension}"``.
    See Also
    --------
    wg_toolkit.misc.mkdir_dated: Create a directory with the current date and time.

    """

    path = Path(base_name)
    parent_dir = path.parent
    if base_path:
        parent_dir = Path(base_path) / parent_dir

    if create_folder:
        if parent_dir.exists():
            print_warning(f"Directory already exists: {parent_dir}", verbose=verbose)
        else:
            print_log(f"Creating directory: {parent_dir}", verbose=verbose)
            parent_dir.mkdir(parents=True, exist_ok=True)

    if time_prefix:
        filename_with_timestamp = f"{datenow_str()}_{path.name}"
        unique_path = parent_dir / filename_with_timestamp
        _res_str = str(unique_path.with_suffix(f".{extension}"))
    else:
        index = 0
        while (
            (parent_dir / f"{path.stem}_{index:02d}")
            .with_suffix(f".{extension}")
            .exists()
        ):
            index += 1
        _res_str = parent_dir / f"{path.stem}_{index:02d}".replace(f".{extension}", "")
        _res_str = str(_res_str.with_suffix(f".{extension}"))

    print_log(f"Unique filename: {_res_str}", verbose=verbose)
    return _res_str


# def get_unique_fname(
#     base_name: str, extension: str = "png", base_path: str = "", time_prefix: bool = True, verbose: bool = True
# ) -> str:
#     """Return a unique filename by appending an index to the base name.

#     Parameters
#     ----------
#     base_name : str
#         The base name of the file (without extension).
#     extension : str, optional
#         The file extension. Default is ``"png"``.
#     base_path : str, optional
#         The base path where the file will be saved.
#     time_prefix : bool, optional
#         If True, prepend the current date and time to the filename.
#     verbose : bool, optional
#         If True, print the unique filename.

#     Returns
#     -------
#     str
#         A unique filename in the format ``"{base_name}_{index:02d}.{extension}"``.
#     """

#     os.makedirs(base_name.rsplit("\\", 1)[0], exist_ok=True)

#     if time_prefix:
#         _name_splitted = base_name.rsplit("\\", 1)
#         _name_splitted[-1] = f"{datenow_str()}_{_name_splitted[-1]}"
#         base_name = "\\".join(_name_splitted)
#         return base_name + f".{extension}"
#     else:
#         index = 0
#         while os.path.exists(f"{base_name}_{index:02d}.{extension}"):
#             index += 1
#         if verbose:
#             print(f"# unique filename: {base_name}_{index:02d}.{extension}")
#         return f"{base_name}_{index:02d}.{extension}"


def select_file_interactive(
    pattern: str = "*",
    message_to_print: str | None = None,
    recursive: bool = True,
) -> str:
    """Interactively select a file matching a glob pattern.

    If exactly one file matches, it is returned immediately. Otherwise, the
    matches are listed and the user is prompted to pick one by index,
    re-prompting on invalid input. The prompt can be cancelled with an empty
    line, ``"q"``, Ctrl-D (EOF) or Ctrl-C.

    Parameters
    ----------
    pattern : str, optional
        Glob pattern to search for files. See
        https://docs.python.org/3/library/glob.html#glob.glob for pattern syntax.
    message_to_print : str, optional
        Message printed before the numbered file list. If None, a default
        message is used.
    recursive : bool, optional
        If True, ``"**"`` in pattern matches any files and zero or more
        directories. See :py:func:`glob.glob`.

    Returns
    -------
    str
        Path of the selected file, or an empty string if no files match
        ``pattern`` or the user cancels the prompt.

    Examples
    --------
    >>> select_file_interactive("*.csv")
    """
    import glob

    file_list = sorted(glob.glob(pattern, recursive=recursive))

    if not file_list:
        print_error(f"No files found matching pattern '{pattern}'.")
        return ""

    if len(file_list) == 1:
        print_log(f"Only one match. Loading {file_list[0]}")
        return file_list[0]

    print(message_to_print or "Enter the index of the file to select:")
    for i, fname in enumerate(file_list):
        print(f"[{i:>2}]: {fname}")
    print("(press Enter, 'q', Ctrl-D or Ctrl-C to cancel)")

    while True:
        try:
            input_str = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            print_log("Selection cancelled.")
            return ""

        if input_str == "" or input_str.lower() in ("q", "quit"):
            print_log("Selection cancelled.")
            return ""

        try:
            idx = int(input_str)
        except ValueError:
            print_error(f"Invalid input: '{input_str}'. Please enter a valid number.")
            continue

        if 0 <= idx < len(file_list):
            return file_list[idx]

        print_error(
            f"Invalid index: {idx}. Choose a number between 0 and {len(file_list) - 1}."
        )


_MODULE_FUNCTIONS = [
    k
    for k, v in globals().items()
    if callable(v)
    and not k.startswith("_")
    and getattr(v, "__module__", None) == __name__
]

if __name__ == "__main__":
    print("\n### wg-toolkit.misc functions:")
    for name in _MODULE_FUNCTIONS:
        print(f"  {name}")

    for name in _MODULE_FUNCTIONS:
        if name not in __all__:
            print(f"Error: '{name}' is defined but missing from __all__.")
