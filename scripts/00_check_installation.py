# %% Check python installation and .venv environment (if in use)
import os
import sys


# %%

try:
    import wg_toolkit as wgtk
    from wg_toolkit.logprint import (
        printc,
        print_log,
        print_info,
        print_warning,
        print_attention,
        print_error,
        print_done,
    )

    print("\n")
    print_info(f"## Python version: {sys.version}")
    print_info(f"Python executable: {sys.executable}")
    if ".venv" in sys.executable:
        print_warning("It looks like you are using a .venv environment.")

    print("\n")
    print_done("wg_toolkit imported successfully")
    print_info(f"wg_toolkit Library Location: {os.path.dirname(wgtk.__file__)}\n\n")

except ImportError as e:
    print(f"[ERROR] Error importing wg_toolkit: {e}")
    print("[ERROR] Please ensure that wg_toolkit is installed and available in your Python environment.")
