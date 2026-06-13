import numpy as np

from wg_toolkit.constants import SDV2FWHM

__all__ = [
    "hdr",
    "hdr2d",
    "nearest",
    "argnearest",
    "variance",
    "fwhm",
]


def _hdr_core(
    flat_z: np.ndarray,
    flat_weights: np.ndarray,
    percentile: float,
) -> float:
    """Core HDR computation shared by hdr and hdr2d.

    Parameters
    ----------
    flat_z : np.ndarray
        1D array of intensity/density values.
    flat_weights : np.ndarray
        1D array of integration weights for each element of flat_z.
    percentile : float
        Target probability mass, value in (0, 1). Must be pre-validated.

    Returns
    -------
    float
        Lambda threshold corresponding to the specified percentile.
    """
    z_norm = flat_z / (flat_z * flat_weights).sum()
    order = np.argsort(z_norm)[::-1]
    cumsum = np.cumsum(z_norm[order] * flat_weights[order])
    idx = min(np.searchsorted(cumsum, percentile), len(flat_z) - 1)
    return float(flat_z[order[idx]])


def hdr(
    x: np.ndarray,
    z: np.ndarray,
    percentile: float = 0.5,
) -> float:
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
    percentile : float
        Target probability mass, value in (0, 1). Default is 0.5.

    Returns
    -------
    float
        Lambda threshold corresponding to the specified percentile.

    Raises
    ------
    ValueError
        If z.shape != (len(x),).
    ValueError
        If percentile is not in the open interval (0, 1).

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
    0.5
    """

    x = np.asarray(x, dtype=float)
    z = np.asarray(z, dtype=float)

    if z.shape != (len(x),):
        raise ValueError(f"z.shape must be (len(x),) = ({len(x)},); got {z.shape}.")
    if not (0 < percentile < 1):
        raise ValueError(f"Percentile must be in (0, 1); got {percentile}.")

    return _hdr_core(z, np.gradient(x), percentile)


def hdr2d(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    percentile: float = 0.5,
) -> float:
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
    percentile : float
        Target probability mass, value in (0, 1). Default is 0.5.

    Returns
    -------
    float
        Lambda threshold corresponding to the specified percentile.

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
    0.5
    """


    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    z = np.asarray(z, dtype=float)

    if z.shape != (len(y), len(x)):
        raise ValueError(
            f"z.shape must be (len(y), len(x)) = ({len(y)}, {len(x)}); got {z.shape}."
        )
    if not (0 < percentile < 1):
        raise ValueError(f"Percentile must be in (0, 1); got {percentile}.")

    dx = np.gradient(x)  # shape (N,)
    dy = np.gradient(y)  # shape (M,)
    cell_areas = np.outer(dy, dx)  # cell_areas[i, j] = dy[i] * dx[j]

    return _hdr_core(z.ravel(), cell_areas.ravel(), percentile)


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


def variance(x_arr: np.ndarray, w_arr: np.ndarray) -> float:
    """Calculate the weighted variance of a distribution.

    Uses explicit weighted variance instead of ``numpy.cov`` to support
    negative weights.

    Parameters
    ----------
    x_arr : np.ndarray
        1D array of coordinates (x or y).
    w_arr : np.ndarray
        1D array of weights (intensity values) corresponding to ``x_arr``.

    Returns
    -------
    float
        Weighted variance in the same units as ``x_arr`` squared.
    """
    mu = np.average(x_arr, weights=w_arr)
    return float(np.average((x_arr - mu) ** 2, weights=w_arr))


def fwhm(x_arr: np.ndarray, w_arr: np.ndarray) -> float:
    """Calculate FWHM from weighted variance assuming a Gaussian distribution.

    Uses the relation ``FWHM = 2 * sqrt(2 * ln(2)) * sigma`` where
    ``sigma**2`` is the weighted variance of the distribution.

    Parameters
    ----------
    x_arr : np.ndarray
        1D array of coordinates (x or y).
    w_arr : np.ndarray
        1D array of weights (intensity values) corresponding to ``x_arr``.

    Returns
    -------
    float
        FWHM in the same units as ``x_arr``.
    """
    return SDV2FWHM * np.sqrt(variance(x_arr, w_arr))


_MODULE_FUNCTIONS = [k for k, v in globals().items() if callable(v) and not k.startswith("_")]

if __name__ == "__main__":
    print("\n### wg-toolkit.analysis functions:")
    for name in _MODULE_FUNCTIONS:
        print(f"  {name}")
