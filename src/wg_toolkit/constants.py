"""
This module defines physical and numerical constants used throughout the folib package.
"""

import numpy as np
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
RAD2DEG = np.rad2deg(1)  # Conversion factor from radians to degrees
DEG2RAD = np.deg2rad(1)  # Conversion factor from degrees to radians
RAD_TO_PI_RAD = 1 / np.pi  # Converts radians to units of pi (e.g., 3.14 rad -> 1.0)
PI_RAD_TO_RAD = np.pi  # Converts units of pi back to radians (e.g., 1.0 -> 3.14 rad)


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

SDV2FWHM = 2 * np.sqrt(2 * np.log(2))
FWHM2SDV = 1.0 / SDV2FWHM
