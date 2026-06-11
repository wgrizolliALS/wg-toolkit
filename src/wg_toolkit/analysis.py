import numpy as np

__all__ = [
    "hdr",
    "hdr2d",
]


def hdr(
    x: np.ndarray,
    z: np.ndarray,
    percentiles: tuple[float, ...] | list[float] | float = (0.25, 0.50, 0.75),
) -> dict[float, float]:
    """Compute 1D Highest Density Region thresholds.

    For each percentile p, returns the density level lambda such that the
    region {x : z(x) >= lambda} contains exactly p of the total probability
    mass. Supports non-uniform grids (log-spaced, polynomial, etc.).

    Args:
        x: 1D array of x-coordinates, length N. Need not be uniformly spaced.
        z: 1D array of intensity/density values, shape (N,). Need not be
            normalized.
        percentiles: Target probability masses, values in (0, 1).

    Returns:
        Dictionary mapping each percentile to its lambda threshold.

    Raises:
        ValueError: If z.shape != (len(x),).
        ValueError: If any percentile is not in the open interval (0, 1).
    """
    if isinstance(percentiles, (float, int)):
        percentiles = [percentiles]

    x = np.asarray(x, dtype=float)
    z = np.asarray(z, dtype=float)

    if z.shape != (len(x),):
        raise ValueError(f"z.shape must be (len(x),) = ({len(x)},); got {z.shape}.")
    if any(not (0 < p < 1) for p in percentiles):
        raise ValueError(f"All percentiles must be in (0, 1); got {percentiles}.")

    dx = np.gradient(x)
    z_norm = z / (z * dx).sum()

    order = np.argsort(z_norm)[::-1]
    cumsum = np.cumsum(z_norm[order] * dx[order])

    thresholds: dict[float, float] = {}
    for p in sorted(percentiles):
        idx = min(np.searchsorted(cumsum, p), len(z) - 1)
        thresholds[p] = float(z[order[idx]])

    return thresholds


def hdr2d(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    percentiles: tuple[float, ...] | list[float] | float = (0.25, 0.50, 0.75),
) -> dict[float, float]:
    """Compute 2D Highest Density Region thresholds on a structured grid.

    For each percentile p, returns the density level lambda such that the
    region {(x, y) : z(x, y) >= lambda} contains exactly p of the total
    probability mass and has minimum area. Supports non-uniform but structured
    grids (log-spaced, polynomial, etc.).

    Args:
        x: 1D array of x-coordinates, length N. Need not be uniformly spaced.
        y: 1D array of y-coordinates, length M. Need not be uniformly spaced.
        z: 2D array of intensity/density values, shape (M, N). Need not be
            normalized. Assumes z[i, j] corresponds to (x[j], y[i]).
        percentiles: Target probability masses, values in (0, 1).

    Returns:
        Dictionary mapping each percentile to its lambda threshold.

    Raises:
        ValueError: If z.shape != (len(y), len(x)).
        ValueError: If any percentile is not in the open interval (0, 1).
    """
    if isinstance(percentiles, (float, int)):
        percentiles = [percentiles]

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    z = np.asarray(z, dtype=float)

    if z.shape != (len(y), len(x)):
        raise ValueError(
            f"z.shape must be (len(y), len(x)) = ({len(y)}, {len(x)}); got {z.shape}."
        )
    if any(not (0 < p < 1) for p in percentiles):
        raise ValueError(f"All percentiles must be in (0, 1); got {percentiles}.")

    dx = np.gradient(x)   # shape (N,)
    dy = np.gradient(y)   # shape (M,)
    cell_areas = np.outer(dy, dx)   # cell_areas[i, j] = dy[i] * dx[j]

    z_norm = z / (z * cell_areas).sum()

    flat_z      = z_norm.ravel()
    flat_z_orig = z.ravel()
    flat_a      = cell_areas.ravel()
    order  = np.argsort(flat_z)[::-1]
    cumsum = np.cumsum(flat_z[order] * flat_a[order])

    thresholds: dict[float, float] = {}
    for p in sorted(percentiles):
        idx = min(np.searchsorted(cumsum, p), len(flat_z) - 1)
        thresholds[p] = float(flat_z_orig[order[idx]])

    return thresholds


_MODULE_FUNCTIONS = [k for k, v in globals().items() if callable(v) and not k.startswith("_")]

if __name__ == "__main__":
    print("\n### wg-toolkit.analysis functions:")
    for name in _MODULE_FUNCTIONS:
        print(f"  {name}")
