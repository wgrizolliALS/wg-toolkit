from importlib.metadata import version as _get_version

from wg_toolkit.misc import *
from wg_toolkit.logprint import *

__version__ = _get_version("wg-toolkit")

try:
    from wg_toolkit.dataio import *
except ImportError:
    print_warning("wg_toolkit.dataio unavailable — this is optional, to install use: uv sync --extra data")

try:
    from wg_toolkit.ports import *
except ImportError:
    print_warning("wg_toolkit.ports unavailable — this is optional, to install use: uv sync --extra serial")

try:
    from wg_toolkit.analysis import *
except ImportError:
    print_warning("wg_toolkit.analysis unavailable — this is optional, to install use: uv sync --extra data")

try:
    from wg_toolkit.visualization import *
except ImportError:
    print_warning("wg_toolkit.visualization unavailable — this is optional, to install use: uv sync --extra plotting")


_MODULE_FUNCTIONS = [k for k, v in globals().items() if callable(v) and not k.startswith("_")]

if __name__ == "__main__":
    print("\n### wg-toolkit functions:")
    for name in _MODULE_FUNCTIONS:
        print(f"  {name}")
