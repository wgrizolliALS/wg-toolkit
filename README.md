# wg-toolkit

Personal toolkit of reusable utilities — small, focused helpers used across lab software projects.

Link to repository: https://github.com/wgrizolliALS/wg-toolkit.git

## Modules

| Module | Description |
| --- | --- |
| `wg_toolkit.logprint` | Colored terminal output |
| `wg_toolkit.dataio` | DataFrame CSV save/load with metadata persistence |
| `wg_toolkit.ports` | Serial port listing and cleanup |
| `wg_toolkit.misc` | Staging area for functions not yet assigned a module |

## Requirements

- Python >= 3.12

All Python dependencies are managed via `pyproject.toml`.

## Installation using 'uv'

***Requirements***: make sure you have [`git`](https://git-scm.com/install/) and [`uv`](https://docs.astral.sh/uv/getting-started/installation/) installed on your system.

### 1. `git clone` repository

```bash
git clone https://github.com/wgrizolliALS/wg-toolkit.git
cd wg-toolkit
```

### 2. Core installation with `uv`

```bash
uv sync
```

### 3. Optional for development

```bash
uv sync --extra dev
nbstripout --install  # Activate nbstripout: Run once to set up nbstripout for this repo
```

### 4. Activate the environment

```bash
# Activate the environment (Linux/Mac)
source .venv/bin/activate
# Activate the environment (Windows)
.venv\Scripts\activate
```

### 5. Verify installation

```bash
uv run python -c "import wg_toolkit; print('wg-toolkit installed successfully!')"
```

## Usage

```python
from wg_toolkit.console import print_info, print_done, print_error
from wg_toolkit.dataio import local_df_to_csv, load_df_from_csv
from wg_toolkit.ports import list_serial_ports

# or import everything from the top level
from wg_toolkit import print_info, local_df_to_csv, list_serial_ports
```
