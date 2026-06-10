from pathlib import Path

import pandas as pd

from wg_toolkit.logprint import print_done, print_error, print_warning

__all__ = [
    "local_df_to_csv",
    "load_df_from_csv",
    "load_df_from_csv_interactive",
]


def local_df_to_csv(
    df: pd.DataFrame, folder: str = "Results", suffix: str = "", force_rewrite: bool = False
):
    """Save a DataFrame to CSV, writing df.attrs as comment lines in the header.

    Args:
        df: DataFrame to save. Must have a 'Time and Date Label' attribute.
        folder: Output directory.
        suffix: String appended to the filename before the .csv extension.
        force_rewrite: If True, overwrite an existing file without warning.
    """
    fname = Path(f"{folder}/{df.attrs['Time and Date Label']}{suffix}.csv")

    if fname.exists() and not force_rewrite:
        print_error(f"File {fname} already exists. Please choose a different name or suffix. NOTHING DONE.")
        raise FileExistsError(f"File {fname} already exists. Please choose a different name or suffix.")
    elif fname.exists():
        print_warning(f"File {fname} already exists. It will be overwritten.")

    fname.parent.mkdir(parents=True, exist_ok=True)

    with open(fname, "w") as f:
        for _attr, _value in df.attrs.items():
            f.write(f"# {_attr}: {_value}\n")

    df.to_csv(fname, index=False, float_format="%.9f", mode="a")
    print_done(f"Data saved to {fname}")


def load_df_from_csv(fname: str) -> pd.DataFrame:
    """Load a DataFrame from CSV, restoring df.attrs from comment lines.

    Args:
        fname: Path to the CSV file.

    Returns:
        DataFrame with attributes restored from comment lines.
    """
    df = pd.read_csv(fname, comment="#")
    with open(fname, "r") as f:
        for line in f:
            if line.startswith("#"):
                key, _, value = line[2:].strip().partition(": ")
                df.attrs[key] = value
    return df


def load_df_from_csv_interactive(folder: str = "Results", suffix: str = "") -> pd.DataFrame:
    """Interactively select and load a CSV file from a folder.

    Lists matching files, prompts the user to select by index, or press Enter
    to load the most recently modified file.

    Args:
        folder: Directory to search for CSV files.
        suffix: Filter files by this suffix before the .csv extension.

    Returns:
        Loaded DataFrame with attributes restored.
    """
    import glob

    while True:
        print("### Select File to Load:")
        flist = glob.glob(f"{folder}/*{suffix}.csv")
        if not flist:
            print_error(f"No files found in {folder} with suffix '{suffix}'.")
            raise FileNotFoundError(f"No files found in {folder} with suffix '{suffix}'.")

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
