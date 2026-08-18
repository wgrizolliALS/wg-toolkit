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

## Installation

**Requirements**: [`uv`](https://docs.astral.sh/uv/getting-started/installation/) ([`git`](https://git-scm.com/install/) is also needed for Option B).

wg-toolkit is used in two main ways — pick the one that matches what you're doing:

- **[Option A — Install to use](#option-a--install-to-use)**: you just want the utilities in your own project's scripts/notebooks.
- **[Option B — Install to develop](#option-b--install-to-develop)**: you're adding/modifying code in this toolkit itself.

### Option A — Install to use

From your own uv project, add wg-toolkit straight from GitHub:

```bash
uv add git+https://github.com/wgrizolliALS/wg-toolkit.git
```

With optional extras:

```bash
uv add git+https://github.com/wgrizolliALS/wg-toolkit.git --extra data       # adds pandas, scipy, engineering-notation → dataio, constants
uv add git+https://github.com/wgrizolliALS/wg-toolkit.git --extra serial     # adds pyserial → ports
uv add git+https://github.com/wgrizolliALS/wg-toolkit.git --extra plotting   # adds plotly  → plotting
uv add git+https://github.com/wgrizolliALS/wg-toolkit.git --extra all        # everything above
```

This adds the following to your project's `pyproject.toml`:

```toml
dependencies = ["wg-toolkit[data]"]

[tool.uv.sources]
wg-toolkit = { git = "https://github.com/wgrizolliALS/wg-toolkit.git" }
```

To pin to a specific branch, tag, or commit instead of the latest, add `--branch <name>`, `--tag <name>`, or `--rev <sha>` to the `uv add` command.

Verify installation:

```bash
uv run python -c "import wg_toolkit; print('wg-toolkit installed successfully!')"
```

#### Keeping up to date

A git dependency installs a pinned commit, so `uv sync` alone won't pick up new commits. To upgrade to the latest:

```bash
uv lock --upgrade-package wg-toolkit
uv sync
```

**Explanation**:
* `uv lock --upgrade-package wg-toolkit` updates the pinned commit for the `wg-toolkit` dependency in your `uv.lock` file, ensuring that the next `uv sync` installs the latest version from the tracked branch, tag, or commit.
* `uv sync` then installs this updated version into your `.venv`.

### Option B — Install to develop

```bash
git clone https://github.com/wgrizolliALS/wg-toolkit.git
cd wg-toolkit
uv sync --extra dev
nbstripout --install  # set up nbstripout once per clone
```

This installs `wg_toolkit` in editable mode, so local edits to the Python files take effect immediately — you only need to re-run `uv sync` if you change dependencies in `pyproject.toml`.

Verify installation by running the script located at `scripts\00_check_installation.py` using your favorite python IDE, or:

```bash
uv run python -c "import wg_toolkit; print('wg-toolkit installed successfully!')"
```

Commit and push your changes as usual:

```bash
git add .
git commit -m "Your commit message"
git push origin master
```

### Activate the environment (optional)

`uv run ...` works without activating the environment, but you can activate it manually if you prefer:

```bash
# Linux/Mac
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

Check which interpreter is active:

```bash
uv run python -c "import sys; print(sys.executable)"
### Result should be like [CURRENT_DIRECTORY]\.venv\Scripts\python.exe
```

## Recommended usage

A few recommended ways of using the toolkit:

### 1. Importing the whole toolkit and using the module name as a prefix for the functions

```python
import wg_toolkit as wgtk
import wg_toolkit.constants as cte
wgtk.print_info("This is an info message")
wgtk.print_done(f"Speed of light: {cte.SPEED_OF_LIGHT_C} m/s")
```

### 2. Importing only the needed functions from the modules

```python
from wg_toolkit.logprint import print_info, print_done, print_error
from wg_toolkit.dataio import load_df_from_csv
from wg_toolkit.ports import list_serial_ports
from wg_toolkit.analysis import hdr, hdr2d

# or import everything from the top level
from wg_toolkit import print_info, load_df_from_csv, hdr, hdr2d

# or alternatively
import wg_toolkit.constants as cte
```
