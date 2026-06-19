# wg-toolkit

Personal toolkit of reusable utilities — small, focused helpers used across lab software projects.

Link to repository: https://github.com/wgrizolliALS/wg-toolkit.git

## Modules

| Module | Description | Requires |
| --- | --- | --- |
| `wg_toolkit.logprint` | Colored terminal output | *(base)* |
| `wg_toolkit.misc` | Date/time helpers and general utilities | *(base)* |
| `wg_toolkit.analysis` | Highest Density Region thresholds (1D and 2D) | *(base)* |
| `wg_toolkit.constants` | Physical and unit-conversion constants | `[data]` |
| `wg_toolkit.dataio` | DataFrame CSV save/load with metadata persistence | `[data]` |
| `wg_toolkit.ports` | Serial port listing and communication | `[serial]` |
| `wg_toolkit.plotting` | Interactive Plotly figures (profiles, heatmaps) | `[plotting]` |

## Installation using `uv`

**Requirements**: [`git`](https://git-scm.com/install/) and [`uv`](https://docs.astral.sh/uv/getting-started/installation/).

### 1. Clone the repository

```bash
git clone https://github.com/wgrizolliALS/wg-toolkit.git
cd wg-toolkit
```

### 2. Install

Base only (logprint, misc, analysis):
```bash
uv sync
```

With optional extras:
```bash
uv sync --extra data       # adds pandas, scipy, engineering-notation → dataio, constants
uv sync --extra serial     # adds pyserial → ports
uv sync --extra plotting   # adds plotly  → plotting
uv sync --extra all        # everything above
```

Combined extras:
```bash
uv sync --extra plotting --extra serial
```

For development:
```bash
uv sync --extra dev
nbstripout --install  # set up nbstripout once per clone
```

### 3. Activate the environment

```bash
# Linux/Mac
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

#### Check `.venv`

```bash
uv run python -c "import sys; print(sys.executable)"
### Result should be like [CURRENT_DIRECTORY]\.venv\Scripts\python.exe
```

### 4. Verify installation

```bash
uv run python -c "import wg_toolkit; print('wg-toolkit installed successfully!')"
```

Alternativelly, run the script located at `scripts\00_check_installation.py` using your favorite python IDE.

## Recomend Usage

These are a few recomended ways of using the toolkit.

### 1. Importing the whole toolkit and using the module name as a prefix for the functions:

```python
import wg_toolkit as wgtk
import wg_toolkit.constants as cte
wgtk.print_info("This is an info message")
wgtk.print_done(f"Speed of light: {cte.SPEED_OF_LIGHT_C} m/s")
```

### 2. Importing only the needed functions from the modules:

```python
from wg_toolkit.logprint import print_info, print_done, print_error
from wg_toolkit.dataio import load_df_from_csv
from wg_toolkit.ports import list_serial_ports
from wg_toolkit.analysis import hdr, hdr2d

# or import everything from the top level
from wg_toolkit import print_info, load_df_from_csv, hdr, hdr2d

# or alternativelly
import wg_toolkit.constants as cte


```
