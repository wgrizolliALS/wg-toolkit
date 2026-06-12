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
    """Core HDR computation shared by hdr and hdr2d.

    Parameters
    ----------
    flat_z : np.ndarray
        1D array of intensity/density values.
    flat_weights : np.ndarray
        1D array of integration weights for each element of flat_z.
    percentiles : list[float] or tuple[float, ...]
        Target probability masses, values in (0, 1). Must be pre-validated.

    Returns
    -------
    dict[float, float]
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
    """Compute 1D Highest Density Region thresholds.

    For each percentile p, returns the density level lambda such that the
    region {x : z(x) >= lambda} contains exactly p of the total probability
    mass. Supports non-uniform grids (log-spaced, polynomial, etc.).

    Parameters
    ----------
    x : np.ndarray
        1D array of x-coordinates, length N. Need not be uniformly spaced.
    z : np.ndarray
        1D array of intensity/density values, shape (N,). Need not be normalized.
    percentiles : float or list[float] or tuple[float, ...]
        Target probability masses, values in (0, 1). Default is (0.25, 0.50, 0.75).

    Returns
    -------
    dict[float, float]
        Dictionary mapping each percentile to its lambda threshold.

    Raises
    ------
    ValueError
        If z.shape != (len(x),).
    ValueError
        If any percentile is not in the open interval (0, 1).

    See Also
    --------
    hdr2d : 2D version of this function.

    Notes
    -----
    An HDR is the smallest region containing a specified percentile of the
    integrated values. The threshold lambda is found by sorting samples by
    descending density, accumulating weighted mass (z_i * dx_i), and returning
    the z value at the index where cumulative mass first reaches p.

    The returned threshold is always an existing value from z (discrete — no
    interpolation). Cell widths are computed via np.gradient, which supports
    non-uniform spacing.

    Examples
    --------
    >>> x = np.linspace(-3, 3, 500)
    >>> z = np.exp(-x**2 / 2)
    >>> hdr(x, z, 0.50)
    {0.5: ...}
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
    """Compute 2D Highest Density Region thresholds on a structured grid.

    For each percentile p, returns the density level lambda such that the
    region {(x, y) : z(x, y) >= lambda} contains exactly p of the total
    probability mass and has minimum area. Supports non-uniform but structured
    grids (log-spaced, polynomial, etc.).

    Parameters
    ----------
    x : np.ndarray
        1D array of x-coordinates, length N. Need not be uniformly spaced.
    y : np.ndarray
        1D array of y-coordinates, length M. Need not be uniformly spaced.
    z : np.ndarray
        2D array of intensity/density values, shape (M, N). Need not be
        normalized. Assumes z[i, j] corresponds to (x[j], y[i]).
    percentiles : float or list[float] or tuple[float, ...]
        Target probability masses, values in (0, 1). Default is (0.25, 0.50, 0.75).

    Returns
    -------
    dict[float, float]
        Dictionary mapping each percentile to its lambda threshold.

    Raises
    ------
    ValueError
        If z.shape != (len(y), len(x)).
    ValueError
        If any percentile is not in the open interval (0, 1).

    See Also
    --------
    hdr : 1D version of this function.

    Notes
    -----
    Cell areas are computed as the outer product of np.gradient(y) and
    np.gradient(x), giving cell_areas[i, j] = dy[i] * dx[j]. This correctly
    handles non-uniform grids. The algorithm then delegates to _hdr_core with
    flattened z and cell areas as weights.

    For a 2D Gaussian, the threshold at p=0.50 corresponds to the FWHM ellipse.
    See hdr for details of the core algorithm.

    Examples
    --------
    >>> x = np.linspace(-3, 3, 100)
    >>> y = np.linspace(-3, 3, 100)
    >>> xx, yy = np.meshgrid(x, y)
    >>> z = np.exp(-(xx**2 + yy**2) / 2)
    >>> hdr2d(x, y, z, 0.50)
    {0.5: ...}
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

    dx = np.gradient(x)  # shape (N,)
    dy = np.gradient(y)  # shape (M,)
    cell_areas = np.outer(dy, dx)  # cell_areas[i, j] = dy[i] * dx[j]

    return _hdr_core(z.ravel(), cell_areas.ravel(), percentiles)


def argnearest(arr: np.ndarray, value: float, flat: bool = False) -> tuple[np.intp, ...] | np.intp:
    """Return the index of the element of arr nearest to value.

    Parameters
    ----------
    arr : np.ndarray
        Array of values to search. Any shape.
    value : float
        Target value.
    flat : bool, optional
        If False (default), return a multi-dimensional index tuple.
        If True, return the scalar flat index into arr.ravel().

    Returns
    -------
    tuple[np.intp, ...] or np.intp
        flat=False: tuple of indices with length == arr.ndim.
                    Can be used directly as arr[argnearest(arr, v)].
        flat=True:  scalar flat index into arr.ravel().

    See Also
    --------
    nearest : returns the value instead of the index.

    Notes
    -----
    Uses ravel() to find the flat argmin, then unravel_index to convert back
    to the original array shape. ravel() is a no-op for 1D arrays, so both
    1D and ND inputs are handled identically.

    Examples
    --------
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


def nearest(arr: np.ndarray, value: float) -> float:
    """Return the element of arr nearest to value.

    Parameters
    ----------
    arr : np.ndarray
        Array of values to search. Any shape.
    value : float
        Target value.

    Returns
    -------
    float
        The element of arr closest to value.

    See Also
    --------
    argnearest : returns the index instead of the value.

    Examples
    --------
    >>> nearest(np.array([0, 5, 10]), 6)
    5.0
    >>> nearest(np.array([[1, 2], [3, 4]]), 2.5)
    2.0
    """
    return float(arr[argnearest(arr, value)])


_MODULE_FUNCTIONS = [k for k, v in globals().items() if callable(v) and not k.startswith("_")]

if __name__ == "__main__":
    print("\n### wg-toolkit.analysis functions:")
    for name in _MODULE_FUNCTIONS:
        print(f"  {name}")
