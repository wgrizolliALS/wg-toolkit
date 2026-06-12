import numpy as np

__all__ = [
    "hdr",
    "hdr2d",
    "nearest",
    "argnearest",
]


def _hdr_core(
    flat_z: np.ndarray,
    flat_weights: np.ndarray,
    percentiles: tuple[float, ...] | list[float],
) -> dict[float, float]:
    """Core HDR computation shared by both 1D and 2D versions.

    Args:
        flat_z: 1D array of intensity/density values.
        flat_weights: 1D array of weights corresponding to each value in flat_z.
        percentiles: Target probability masses, values in (0, 1).

    Returns:
        Dictionary mapping each percentile to its lambda threshold.
    """
    z_norm = flat_z / (flat_z * flat_weights).sum()
    order = np.argsort(z_norm)[::-1]
    cumsum = np.cumsum(z_norm[order] * flat_weights[order])
    thresholds: dict[float, float] = {}
    for p in sorted(percentiles):
        idx = min(np.searchsorted(cumsum, p), len(flat_z) - 1)
        thresholds[p] = float(flat_z[order[idx]])
    return thresholds


def hdr(
    x: np.ndarray,
    z: np.ndarray,
    percentiles: tuple[float, ...] | list[float] | float = (0.25, 0.50, 0.75),
) -> dict[float, float]:
    """

    ## Compute 1D Highest Density Region thresholds.

    For each percentile p, returns the density level lambda such that the
    region {x : z(x) >= lambda} contains exactly p of the total probability
    mass. Supports non-uniform grids (log-spaced, polynomial, etc.).

    ## Args:
        x: 1D array of x-coordinates, length N. Need not be uniformly spaced.
        z: 1D array of intensity/density values, shape (N,). Need not be
            normalized.
        percentiles: Target probability masses, values in (0, 1).

    ## Returns:
        Dictionary mapping each percentile to its lambda threshold.

    ## Raises:
        ValueError: If z.shape != (len(x),).
        ValueError: If any percentile is not in the open interval (0, 1).

    ## See also:
        wg-toolkit.analysis.hdr2d: 2D version of this function.

    ## Long description:

        An HDR is the smallest region that contains a specified percentile of a
        function's integrated values. It is based on the (mathematical) fact that
        the smallest region enclosing a certain percentile is exactly the region
        where the function is above a single threshold value. In 1D, this region
        is an interval or union of intervals; in 2D, it is a contour of the function.

        For each percentile p, this function returns the density level λ such that
        the region {(x, y) : f(x, y) ≥ λ} contains exactly p of the total
        integrated values and has minimum area. Supports non-uniform but structured
        grids (log-spaced, polynomial, etc.).

        The threshold λ is found such that:
            (sum of f(x,y) values where f(x,y) ≥ λ) / (total sum of all f(x,y) values) = p

        Computation:
        If working with function samples {f(x_i, y_i)}, λ is found by:
        1. Sorting samples in descending order: f(x_1, y_1) ≥ f(x_2, y_2) ≥ ... ≥ f(x_n, y_n)
        2. Computing cumulative sums: S_k = Σ_{i=1}^k f(x_i, y_i)
        3. Finding the index k where S_k / S_n ≥ p for the first time
        4. Setting λ = f(x_k, y_k)


    """
    if isinstance(percentiles, (float, int)):
        percentiles = [percentiles]

    x = np.asarray(x, dtype=float)
    z = np.asarray(z, dtype=float)

    if z.shape != (len(x),):
        raise ValueError(f"z.shape must be (len(x),) = ({len(x)},); got {z.shape}.")
    if any(not (0 < p < 1) for p in percentiles):
        raise ValueError(f"All percentiles must be in (0, 1); got {percentiles}.")

    return _hdr_core(z, np.gradient(x), percentiles)


def hdr2d(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    percentiles: tuple[float, ...] | list[float] | float = (0.25, 0.50, 0.75),
) -> dict[float, float]:
    """

    ## Compute 2D Highest Density Region thresholds on a structured grid.

    For each percentile p, returns the density level lambda such that the
    region {(x, y) : z(x, y) >= lambda} contains exactly p of the total
    probability mass and has minimum area. Supports non-uniform but structured
    grids (log-spaced, polynomial, etc.).

    ## Args:
        x: 1D array of x-coordinates, length N. Need not be uniformly spaced.
        y: 1D array of y-coordinates, length M. Need not be uniformly spaced.
        z: 2D array of intensity/density values, shape (M, N). Need not be
            normalized. Assumes z[i, j] corresponds to (x[j], y[i]).
        percentiles: Target probability masses, values in (0, 1).

    ## Returns:
        Dictionary mapping each percentile to its lambda threshold.

    ## Raises:
        ValueError: If z.shape != (len(y), len(x)).
        ValueError: If any percentile is not in the open interval (0, 1).

    ## See also:
        wg-toolkit.analysis.hdr: 1D version of this function.

    ## Long description:
        See wg-toolkit.analysis.hdr for details.
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
    dy = np.gradient(y)  # shape (M,)
    cell_areas = np.outer(dy, dx)  # cell_areas[i, j] = dy[i] * dx[j]

    return _hdr_core(z.ravel(), cell_areas.ravel(), percentiles)


def nearest(arr: np.ndarray, value: float) -> float:
    """
    ## Return the element of arr nearest to value.

    ## Args:
        arr: Array of values to search. Any shape.
        value: Target value.

    ## Returns:
        The element of arr closest to value.

    ## See also:
        wg-toolkit.analysis.argnearest: returns the index instead of the value.

    ## Usage:
        >>> nearest(np.array([0, 5, 10]), 6)
        5.0
        >>> nearest(np.array([[1, 2], [3, 4]]), 2.5)
        2.0
    """
    return float(arr[argnearest(arr, value)])


def argnearest(arr: np.ndarray, value: float, flat: bool = False) -> tuple[np.intp, ...] | np.intp:
    """
    ## Return the index of the element of arr nearest to value.

    ## Args:
        arr: Array of values to search. Any shape.
        value: Target value.
        flat: If False (default), return a multi-dimensional index tuple.
              If True, return the scalar flat index into the raveled array.

    ## Returns:
        flat=False: tuple of np.intp indices, length == arr.ndim.
                    Use directly as arr[argnearest(arr, v)].
        flat=True:  scalar np.intp flat index into arr.ravel().

    ## Notes:
        Uses ravel() to find the flat index, then unravel_index to convert
        back to the original array shape — works identically for 1D and ND.

    ## Usage:
        >>> argnearest(np.array([0, 5, 10]), 6)
        (1,)
        >>> argnearest(np.array([[1, 2], [3, 4]]), 2.5)
        (0, 1)
        >>> argnearest(np.array([[1, 2], [3, 4]]), 2.5, flat=True)
        1
    """
    flat_arr = arr.ravel()  # ravel is a no-op for 1D; flattens ND without copy
    flat_idx = np.argmin(np.abs(flat_arr - value))
    return flat_idx if flat else np.unravel_index(flat_idx, arr.shape)  # scalar or ND tuple


_MODULE_FUNCTIONS = [k for k, v in globals().items() if callable(v) and not k.startswith("_")]

if __name__ == "__main__":
    print("\n### wg-toolkit.analysis functions:")
    for name in _MODULE_FUNCTIONS:
        print(f"  {name}")
