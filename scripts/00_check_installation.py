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
    print("## [INFO]: It looks like you are using a .venv environment.")


# %%
_lib_list = ["numpy", "pandas", "scipy"]
_suc_list = []
_fail_list = []

print(f"\n[INFO] Checking imports of the following modules:\n\t - {'\n\t - '.join(_lib_list)}")
print()
for module in _lib_list:
    try:
        __import__(module)

        _suc_list += [module]
    except ImportError as e:
        _fail_list += [module]

if _suc_list:
    print("[SUCCESS] The following modules were imported successfully:")
    for module in _suc_list:
        print(f"\t - {module} version: {sys.modules[module].__version__}")

if _fail_list:
    print("\n[ERROR] The following modules failed to import:")
    for module in _fail_list:
        print(f"\t - {module} failed to import")
else:
    print("\n[SUCCESS] All modules imported successfully.")


# %%

print("\n\n## Checking wg_toolkit installation and version...\n")

try:
    import wg_toolkit as wgtk
    from wg_toolkit.logprint import print_done, print_info

    print("\n")
    print_done("wg_toolkit imported successfully")
    print_info(f"wg_toolkit Library Location: {os.path.dirname(wgtk.__file__)}\n\n")

except ImportError as e:
    print(f"[ERROR] Error importing wg_toolkit: {e}")
    print("[ERROR] Please ensure that wg_toolkit is installed and available in your Python environment.")

    print(f"ImportError: {e}")

# %%
