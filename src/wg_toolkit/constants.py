"""
# Description

This module defines physical and numerical constants used throughout the folib package.

# Recommended Example and Usage:

```
import wg_toolkit.constants as cte
ph_EN = cte.HC/ (1*cte.ANGSTROM2M) # Photon Energy of 1 Angstrom photon
print(f"Photon Energy of 1 Angstrom photon: {EngNumber(ph_EN, significant=5)} eV")
```


"""

import numpy as np
from engineering_notation import EngNumber
from scipy import constants as sp_constants

# Define common engineering notation units for convenience
ENG_UNITS = {  # Dictionary of common engineering units
    "length": "m",
    "energy": "eV",
    "frequency": "Hz",
    "time": "s",
    "angle": "rad",
}

# Machine epsilon for float64, the smallest number such that 1.0 + eps != 1.0
EPS = np.finfo(float).eps
NAN = float("NAN")
INF = float("inf")
PI = np.pi
TWOPI = 2 * np.pi


# Constants for physical phenomena
HC = sp_constants.value("inverse meter-electron volt relationship")  # hc, in eV*m
SPEED_OF_LIGHT_C = sp_constants.c  # Speed of light in vacuum (m/s)
PLANCK_CONSTANT_H = sp_constants.h  # Planck constant (J s)
E_CHARGE = sp_constants.e  # Elementary charge (C)
VACUUM_PERMITTIVITY = sp_constants.epsilon_0  # Vacuum permittivity (F/m)
VACUUM_PERMEABILITY = sp_constants.mu_0  # Vacuum permeability (N/A^2)

# Conversion factors for angles
RAD2DEG = float(np.rad2deg(1))  # Conversion factor from radians to degrees
DEG2RAD = float(np.deg2rad(1))  # Conversion factor from degrees to radians
RAD_TO_PI_RAD = 1 / np.pi  # Converts radians to units of pi (e.g., 3.14 rad -> 1.0)
PI_RAD_TO_RAD = np.pi  # Converts units of pi back to radians (e.g., 1.0 -> 3.14 rad)
RAD2MRAD = 1e3  # Conversion factor from radians to milliradians
MRAD2RAD = 1 / RAD2MRAD  # Conversion factor from milliradians to radians
RAD2URAD = 1e6  # Conversion factor from radians to microradians
URAD2RAD = 1 / RAD2URAD  # Conversion factor from microradians to radians


# Conversion factors for length
M2MM = 1e3  # Conversion factor from meters to millimeters
MM2M = 1 / M2MM  # Conversion factor from millimeters to meters
M2MICRON = 1e6  # Conversion factor from meters to microns
MICRON2M = 1 / M2MICRON  # Conversion factor from microns to meters
M2CM = 1e2  # Conversion factor from meters to centimeters
CM2M = 1 / M2CM  # Conversion factor from centimeters to meters
M2NM = 1e9  # Conversion factor from meters to nanometers
NM2M = 1 / M2NM  # Conversion factor from nanometers to meters
M2ANGSTROM = 1e10  # Conversion factor from meters to angstroms
ANGSTROM2M = 1 / M2ANGSTROM  # Conversion factor from angstroms to meters


# Conversion factors for time
SEC_PER_MIN = 60  # Number of seconds in a minute
SEC_PER_HOUR = SEC_PER_MIN * 60  # Number of seconds in an hour
SEC_PER_DAY = SEC_PER_HOUR * 24  # Number of seconds in a day

MIN2SEC = SEC_PER_MIN  # Conversion factor from minutes to seconds
SEC2MIN = 1 / MIN2SEC  # Conversion factor from seconds to minutes
HOUR2SEC = SEC_PER_HOUR  # Conversion factor from hours to seconds
SEC2HOUR = 1 / HOUR2SEC  # Conversion factor from seconds to hours
DAY2SEC = SEC_PER_DAY  # Conversion factor from days to seconds
SEC2DAY = 1 / DAY2SEC  # Conversion factor from seconds to days

# Others

SDV2FWHM = float(2 * np.sqrt(2 * np.log(2)))
FWHM2SDV = 1.0 / SDV2FWHM

_MODULE_CONSTANTS = {k: v for k, v in locals().items() if not callable(v) and k.isupper()}


from tabulate import tabulate  # pip install tabulate


def show_all_constants():
    """Print all constants defined in this module in a tabular layout."""
    print("\n\n### Physical and Numerical Constants:\n")

    rows = []
    for name, value in _MODULE_CONSTANTS.items():
        try:
            # – Convert EngNumber to plain str ahead of Tabulate – #S
            val_str = f"{value:.5g}"
            val_str_eng = str(EngNumber(value, significant=5))
            rows.append([name, type(value).__name__, val_str, val_str_eng])
        except Exception:
            rows.append([name, type(value).__name__, str(value), "N/A"])

    # You’re free to tweak the table format; I’ll keep it “plain”
    print(
        tabulate(
            rows,
            headers=["Name", "Type", "Value", "EngNumber"],
            maxcolwidths=[20, 10, 10, 10],
            tablefmt="fancy_grid",
        )
    )

    print()


if __name__ == "__main__":
    """
    Prints all constants defined in this module.
    """

    print(
        "\n## Recommended usage and example:\n\n"
        "import wg_toolkit.constants as cte\n"
        "ph_EN = cte.HC/ (1*cte.ANGSTROM2M) # Photon Energy of 1 Angstrom photon\n"
        'print(f"Photon Energy of 1 Angstrom photon: {EngNumber(ph_EN, significant=5)} eV")'
    )

    show_all_constants()
