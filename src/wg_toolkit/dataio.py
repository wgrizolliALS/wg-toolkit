from pathlib import Path

import numpy as np
import pandas as pd

from wg_toolkit.logprint import print_done, print_error, print_warning
from wg_toolkit.misc import datenow_str, select_file_interactive

__all__ = [
    "array_to_csv",
    "df_to_csv",
    "load_array_from_csv",
    "load_df_from_csv",
    "load_df_from_csv_interactive",
    "local_df_to_csv",
]

def array_to_csv(
    arrayList: list[np.ndarray] | np.ndarray,
    fname: str = "output.csv",
    folder: str = "./",
    headerList: list[str] | None = None,
    comments: str = "",
    force_rewrite: bool = False,
):
    """Save one or more 1D arrays (or a 2D array) as a CSV file.

    Parameters
    ----------
    arrayList : list of ndarray or ndarray
        Data to save. If a list of 1D arrays, each array becomes a column.
        If a 2D ndarray, it is saved as-is.
    fname : str, optional
        Output file name.
    folder : str, optional
        Output directory.
    headerList : list of str, optional
        Column names, written as the CSV header row.
    comments : str, optional
        Text written as ``# ``-prefixed comment lines before the header row.
        Multi-line strings are split so each line gets its own ``#`` prefix.
    force_rewrite : bool, optional
        If True, overwrite an existing file without raising an error.

    Raises
    ------
    FileExistsError
        If the file already exists and force_rewrite is False.
    TypeError
        If arrayList is not a list or an ndarray.

    Examples
    --------
    >>> array_csv_file([x, y], folder="Results", headerList=["x", "y"])
    """

    f_path = Path(folder) / fname

    if f_path.exists() and not force_rewrite:
        print_error(f"File {f_path} already exists. Please choose a different name or suffix. NOTHING DONE.")
        raise FileExistsError(f"File {f_path} already exists. Please choose a different name or suffix.")
    elif f_path.exists():
        print_warning(f"File {f_path} already exists. It will be overwritten.")
    else:
        f_path.parent.mkdir(parents=True, exist_ok=True)
        print_done(f"Saving data to {f_path}...")

    if isinstance(arrayList, list):
        data2save = np.column_stack(arrayList)
    elif isinstance(arrayList, np.ndarray):
        data2save = arrayList
    else:
        raise TypeError(f"arrayList must be a list or an ndarray, got {type(arrayList)}.")

    if np.issubdtype(data2save.dtype, np.integer):
        fmt = "%d"
    else:
        fmt = "%.9f"

    with open(f_path, "w") as f:
        if comments:
            f.writelines(f"# {line}\n" for line in comments.splitlines())
        if headerList:
            f.write(",".join(headerList) + "\n")

    with open(f_path, "a") as f:
        np.savetxt(f, data2save, fmt=fmt, delimiter=",")

    print_done(f"Data saved to {f_path}")


def df_to_csv(
    df: pd.DataFrame,
    fname: str | Path = "",
    folder: str = "./",
    suffix: str = "",
    timestamp_fname=True,
    force_rewrite: bool = False,
):
    """Save a DataFrame to CSV, writing df.attrs as comment lines in the header.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to save.
    fname : str or Path, optional
        Full file path. If empty, the path is constructed from folder, suffix,
        and timestamp.
    folder : str, optional
        Output directory. Used when fname is not provided.
    suffix : str, optional
        String appended to the filename before the .csv extension.
    timestamp_fname : bool, optional
        If True, prepend the current date and time to the filename.
    force_rewrite : bool, optional
        If True, overwrite an existing file without raising an error.

    Raises
    ------
    FileExistsError
        If the file already exists and force_rewrite is False.

    Examples
    --------
    >>> df_to_csv(df, folder="Results", suffix="_mydata", timestamp_fname=True)
    """

    if fname:
        f_path = Path(fname)
    else:
        stem = f"{datenow_str()}{suffix}" if timestamp_fname else suffix
        f_path = Path(folder) / f"{stem}.csv"

    if f_path.exists():
        if not force_rewrite:
            print_error(f"File {f_path} already exists. Please choose a different name or suffix. NOTHING DONE.")
            raise FileExistsError(f"File {f_path} already exists. Please choose a different name or suffix.")
        print_warning(f"File {f_path} already exists. It will be overwritten.")
    else:
        f_path.parent.mkdir(parents=True, exist_ok=True)
        print_done(f"Saving data to {f_path}...")

    with open(f_path, "w") as f:
        f.writelines(f"# {_attr}: {_value}\n" for _attr, _value in df.attrs.items())

    df.to_csv(f_path, index=False, float_format="%.9f", mode="a")
    print_done(f"Data saved to {f_path}")


def local_df_to_csv(  # FIXME: Remove in a future release. Use df_to_csv instead.
    df: pd.DataFrame, folder: str = "Results", suffix: str = "", force_rewrite: bool = False
):
    """Removed. Use :func:`df_to_csv` instead.

    Raises
    ------
    RuntimeError
        Always. This function has been removed.
    """
    raise RuntimeError("local_df_to_csv was removed; use df_to_csv instead.")

def load_array_from_csv(fname: str, delimiter: str = ",", comment_str: str = "#", header: int | None = 0):
    """
    Load a CSV file into a numpy array and return the data, comments, and column names.

    This is a wrapper for :func:`load_df_from_csv` that unpacks the DataFrame it
    returns into plain arrays/lists, for callers that want array data without
    working with a DataFrame directly.

    Parameters
    ----------
    fname : str
        Path to the CSV file.
    delimiter : str, optional
        Delimiter used in the CSV file. Default is ``","``.
    comment_str : str, optional
        String marking comment lines. Default is ``"#"``.
    header : int or None, optional
        Same semantics as :func:`load_df_from_csv`'s ``header``. Default is
        ``0``, matching files written by :func:`df_to_csv`. Pass ``-1`` for
        files whose header row is itself a comment line (e.g. from other
        tools), with the header taken as the LAST comment line.

    Returns
    -------
    data : np.ndarray
        The data from the CSV file.
    comments : list of str
        Comment lines from the header, reconstructed as ``"key: value"`` strings.
    colNames : list of str
        Column names of the data.

    Example
    -------
    >>> import wg_toolkit as wgtk
    >>> data, comments, colNames = wgtk.load_array_from_csv("data.csv")
    >>> # for a foreign file with a commented header line:
    >>> data, comments, colNames = wgtk.load_array_from_csv("legacy.csv", header=-1)

    """

    _df = load_df_from_csv(fname, delimiter=delimiter, comment_str=comment_str, header=header)
    _data = _df.to_numpy()
    _colNames = list(_df.columns)
    _comments = [f"{_key}: {_value}" for _key, _value in _df.attrs.items()]

    return _data, _comments, _colNames


def load_df_from_csv(fname: str, delimiter: str = ",", comment_str: str = "#", header: int | None = 0) -> pd.DataFrame:
    """Load a DataFrame from CSV, restoring df.attrs from comment lines.

    Parameters
    ----------
    fname : str
        Path to the CSV file.
    delimiter : str, optional
        Delimiter used in the CSV file. Default is ``","``.
    comment_str : str, optional
        String marking comment lines. Default is ``"#"``.
    header : int or None, optional
        Row to use as column names, same semantics as :func:`pandas.read_csv`'s
        ``header`` (``0`` means the first non-comment row is a real,
        uncommented header row; ``None`` means no header). The special value
        ``-1`` means the header is instead the LAST comment line (i.e., it is
        itself prefixed by ``comment_str``) - the convention used by many
        other tools, where pandas' own header inference would silently
        discard that line and misread the first data row as the header.
        Default is ``0``, matching files written by :func:`df_to_csv`.

    Returns
    -------
    pd.DataFrame
        DataFrame with attributes restored from comment lines.
    """
    comment_lines = []
    with open(fname, "r") as f:
        for line in f:
            if not line.startswith(comment_str):
                break
            comment_lines.append(line[len(comment_str) :].strip())

    if header == -1:
        col_names, metadata = (comment_lines[-1].split(delimiter), comment_lines[:-1]) if comment_lines else (None, [])
        df = pd.read_csv(fname, delimiter=delimiter, skiprows=len(comment_lines), header=None, names=col_names)
    else:
        metadata = comment_lines
        df = pd.read_csv(fname, delimiter=delimiter, skiprows=len(comment_lines), header=header)

    for line in metadata:
        key, _, value = line.partition(": ")
        df.attrs[key] = value

    return df


def load_df_from_csv_interactive(pathname=".\\*csv") -> pd.DataFrame | None:
    """Interactively select and load a CSV file from a folder.

    Thin wrapper around :func:`wg_toolkit.misc.select_file` and
    :func:`load_df_from_csv`.

    Parameters
    ----------
    pathname : str, optional
        Glob pattern to search for CSV files. See
        https://docs.python.org/3/library/glob.html#glob.glob for pattern syntax.

    Returns
    -------
    pd.DataFrame or None
        Loaded DataFrame with attributes restored, or None if no files found.
    """
    fname = select_file_interactive(pathname)
    return load_df_from_csv(fname) if fname else None

_MODULE_FUNCTIONS = [
    k for k, v in globals().items() if callable(v) and not k.startswith("_") and getattr(v, "__module__", None) == __name__
]

if __name__ == "__main__":
    print("\n### wg-toolkit.dataio functions:")
    for name in _MODULE_FUNCTIONS:
        print(f"  {name}")

    for name in _MODULE_FUNCTIONS:
        if name not in __all__:
            print(f"Error: '{name}' is defined but missing from __all__.")
