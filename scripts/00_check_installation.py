"""
Simple script to verify the python and a few library installation and version.
"""

# %%
import os
import sys


# %%

print(f"\n## Python version: {sys.version}")
print(f"## Python executable:\n\t- {sys.executable}")
if ".venv" in sys.executable:
    print("## WARNING: It looks like you are using a .venv environment.")

# %%

try:
    import numpy as np

    print("\n## numpy imported successfully")
    print(f"## numpy version: {np.__version__}")
except ImportError as e:
    print(f"[ERROR] Error importing numpy: {e}")
    print("[ERROR] Please ensure that numpy is installed and available in your Python environment.")
    raise e

# %%

try:
    import wg_toolkit as wgtk
    from wg_toolkit.logprint import print_info, print_warning, print_done

    print("\n")
    print_done("wg_toolkit imported successfully")
    print_info(f"wg_toolkit Library Location: {os.path.dirname(wgtk.__file__)}\n\n")

except ImportError as e:
    print(f"[ERROR] Error importing wg_toolkit: {e}")
    print("[ERROR] Please ensure that wg_toolkit is installed and available in your Python environment.")
    raise e
