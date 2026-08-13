from pathlib import Path

import pandas as pd

from wg_toolkit.logprint import print_done, print_error, print_warning
from wg_toolkit.misc import datenow_str

__all__ = [
    "df_to_csv",
    "load_df_from_csv",
    "load_df_from_csv_interactive",
    "local_df_to_csv",
]

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
        if timestamp_fname:
            f_path = Path(f"{folder}/{datenow_str()}{suffix}.csv")
        else:
            f_path = Path(f"{folder}/{suffix}.csv")

    if f_path.exists() and not force_rewrite:
        print_error(f"File {f_path} already exists. Please choose a different name or suffix. NOTHING DONE.")
        raise FileExistsError(f"File {f_path} already exists. Please choose a different name or suffix.")
    elif f_path.exists():
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


def load_df_from_csv(fname: str) -> pd.DataFrame:
    """Load a DataFrame from CSV, restoring df.attrs from comment lines.

    Parameters
    ----------
    fname : str
        Path to the CSV file.

    Returns
    -------
    pd.DataFrame
        DataFrame with attributes restored from comment lines.
    """
    df = pd.read_csv(fname, comment="#")
    with open(fname, "r") as f:
        for line in f:
            if line.startswith("#"):
                key, _, value = line[2:].strip().partition(": ")
                df.attrs[key] = value
    return df


def load_df_from_csv_interactive(pathname=".\\*csv") -> pd.DataFrame | None:
    """Interactively select and load a CSV file from a folder.

    Lists matching files, prompts the user to select by index, or press Enter
    to load the most recently modified file.

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
    import glob

    while True:
        print(f"### Select File to Load: {pathname}")
        flist = glob.glob(pathname)
        if not flist:
            print_error(f"No files found matching '{pathname}'.")
            return None

        for i, f in enumerate(flist):
            print(f"[{i:>2}]: {f}")

        print("Enter the index of the file to load (or press Enter to load the most recent file): ", end="")
        input_str = input()
        print(f"\nINPUT: {input_str}.")

        try:
            if input_str == "":
                selected_file = flist[-1]
            else:
                idx = int(input_str)
                if 0 <= idx < len(flist):
                    selected_file = flist[idx]
                else:
                    print_error("Invalid index. Please enter a valid number.")
                    continue

            print_done(f"Loaded data from {selected_file}")
            return load_df_from_csv(selected_file)

        except ValueError:
            print_error(f"Invalid input: {input_str}. Please enter a valid number.")
            continue

_MODULE_FUNCTIONS = [k for k, v in globals().items() if callable(v) and not k.startswith("_")]

if __name__ == "__main__":
    print("\n### wg-toolkit.dataio functions:")
    for name in _MODULE_FUNCTIONS:
        print(f"  {name}")
