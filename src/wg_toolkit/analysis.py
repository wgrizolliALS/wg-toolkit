import numpy as np

from wg_toolkit.constants import SDV2FWHM

__all__ = [
    "argnearest",
    "fwhm",
    "hdr",
    "hdr2d",
    "nearest",
    "variance",
]


def _hdr_core(
    flat_z: np.ndarray,
    flat_weights: np.ndarray,
    coverage: float,
) -> float:
    """Core HDR computation shared by hdr and hdr2d.

    Parameters
    ----------
    flat_z : np.ndarray
        1D array of intensity/density values.
    flat_weights : np.ndarray
        1D array of integration weights for each element of flat_z.
    coverage : float
        Target probability mass, value in (0, 1). Must be pre-validated.

    Returns
    -------
    float
        Lambda threshold corresponding to the specified coverage.
    """
    total = (flat_z * flat_weights).sum()
    z_norm = flat_z / total
    # Sort by flat_z, not z_norm: when total < 0 (all-negative data), dividing by
    # a negative total flips z_norm's ordering relative to flat_z, so argsort(z_norm)
    # would put the most-negative value first instead of the highest.
    order = np.argsort(flat_z)[::-1]
    cumsum = np.cumsum(z_norm[order] * flat_weights[order])
    idx = min(np.searchsorted(cumsum, coverage), len(flat_z) - 1)
    return float(flat_z[order[idx]])


def hdr(
    f: np.ndarray,
    x: np.ndarray | None = None,
    coverage: float = 0.5,
) -> float:
    """Compute 1D Highest Density Region thresholds.

    For each coverage p, returns the density level lambda such that the
    region {x : f(x) >= lambda} contains exactly p of the total probability
    mass. Supports non-uniform grids (log-spaced, polynomial, etc.).

    Parameters
    ----------
    f : np.ndarray
        1D array of intensity/density values, shape (N,). Need not be normalized.
    x : np.ndarray, optional
        1D array of x-coordinates, length N. Uniformly or non-uniformly spaced.
        If None, uniform spacing is assumed and only relative density matters.
    coverage : float
        Target probability mass, value in (0, 1). Default is 0.5.

    Returns
    -------
    float
        Lambda threshold corresponding to the specified coverage.

    Raises
    ------
    ValueError
        If x is given and f.shape != (len(x),).
    ValueError
        If coverage is not in the open interval (0, 1).

    See Also
    --------
    hdr2d : 2D version of this function.

    Notes
    -----
    An HDR is the smallest region containing a specified coverage of the
    integrated values. The threshold lambda is found by sorting samples by
    descending density, accumulating weighted mass (f_i * dx_i), and returning
    the f value at the index where cumulative mass first reaches p.

    The returned threshold is always an existing value from f (discrete — no
    interpolation). Cell widths are computed via np.gradient, which supports
    non-uniform spacing.

    Examples
    --------

    ```python
    >>> f = np.exp(-np.linspace(-3, 3, 500)**2 / 2)
    >>> hdr(f, coverage=0.50)
    0.5
    >>> x = np.linspace(-3, 3, 500)
    >>> hdr(f, x, coverage=0.50)
    0.5
    ```

    """

    f = np.asarray(f, dtype=float)

    if x is not None:
        x = np.asarray(x, dtype=float)
        if f.shape != (len(x),):
            raise ValueError(f"f.shape must be (len(x),) = ({len(x)},); got {f.shape}.")
        weights = np.gradient(x)
    else:
        weights = np.ones(f.shape)

    if not (0 < coverage < 1):
        raise ValueError(f"coverage must be in (0, 1); got {coverage}.")

    return _hdr_core(f, weights, coverage)


def hdr2d(
    f: np.ndarray,
    x: np.ndarray | None = None,
    y: np.ndarray | None = None,
    coverage: float = 0.5,
) -> float:
    """Compute 2D Highest Density Region thresholds on a structured grid.

    For each coverage p, returns the density level lambda such that the
    region {(x, y) : f(x, y) >= lambda} contains exactly p of the total
    probability mass and has minimum area. Supports non-uniform but structured
    grids (log-spaced, polynomial, etc.).

    Parameters
    ----------
    f : np.ndarray
        2D array of intensity/density values, shape (M, N). Need not be
        normalized. Assumes f[i, j] corresponds to (x[j], y[i]).
    x : np.ndarray, optional
        1D array of x-coordinates, length N. Uniformly or non-uniformly spaced.
        If None, uniform spacing is assumed.
    y : np.ndarray, optional
        1D array of y-coordinates, length M. Uniformly or non-uniformly spaced.
        If None, uniform spacing is assumed.
    coverage : float
        Target probability mass, value in (0, 1). Default is 0.5.

    Returns
    -------
    float
        Lambda threshold corresponding to the specified coverage.

    Raises
    ------
    ValueError
        If x is given and f.shape[1] != len(x), or y is given and f.shape[0] != len(y).
    ValueError
        If any coverage is not in the open interval (0, 1).

    See Also
    --------
    hdr : 1D version of this function.

    Notes
    -----
    Cell areas are computed as the outer product of np.gradient(y) and
    np.gradient(x), giving cell_areas[i, j] = dy[i] * dx[j]. This correctly
    handles non-uniform grids. The algorithm then delegates to _hdr_core with
    flattened f and cell areas as weights.

    For a 2D Gaussian, the threshold at coverage=0.50 corresponds to the FWHM ellipse.
    See hdr for details of the core algorithm.

    Examples
    --------
    >>> xx, yy = np.meshgrid(np.linspace(-3, 3, 100), np.linspace(-3, 3, 100))
    >>> f = np.exp(-(xx**2 + yy**2) / 2)
    >>> hdr2d(f, coverage=0.50)
    0.5
    """

    f = np.asarray(f, dtype=float)

    if x is not None:
        x = np.asarray(x, dtype=float)
        if f.shape[1] != len(x):
            raise ValueError(
                f"f.shape[1] must equal len(x) = {len(x)}; got {f.shape[1]}."
            )
        dx = np.gradient(x)
    else:
        dx = np.ones(f.shape[1])

    if y is not None:
        y = np.asarray(y, dtype=float)
        if f.shape[0] != len(y):
            raise ValueError(
                f"f.shape[0] must equal len(y) = {len(y)}; got {f.shape[0]}."
            )
        dy = np.gradient(y)
    else:
        dy = np.ones(f.shape[0])

    if not (0 < coverage < 1):
        raise ValueError(f"coverage must be in (0, 1); got {coverage}.")

    cell_areas = np.outer(dy, dx)  # cell_areas[i, j] = dy[i] * dx[j]

    return _hdr_core(f.ravel(), cell_areas.ravel(), coverage)


def argnearest(
    arr: np.ndarray, value: float, flat: bool = False
) -> tuple[np.intp, ...] | np.intp:
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
    return (
        flat_idx if flat else np.unravel_index(flat_idx, arr.shape)
    )  # scalar or ND tuple


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


_MODULE_FUNCTIONS = [
    k
    for k, v in globals().items()
    if callable(v)
    and not k.startswith("_")
    and getattr(v, "__module__", None) == __name__
]

if __name__ == "__main__":
    print("\n### wg-toolkit.analysis functions:")
    for name in _MODULE_FUNCTIONS:
        print(f"  {name}")

    for name in _MODULE_FUNCTIONS:
        if name not in __all__:
            print(f"Error: '{name}' is defined but missing from __all__.")
