import numpy as np
import plotly.graph_objects as go
import plotly.colors as pc
from plotly.subplots import make_subplots

from wg_toolkit.analysis import nearest, hdr, hdr2d, variance, fwhm
from wg_toolkit.logprint import print_done, print_warning, print_info, print_log

__all__ = [
    "plot_profiles_widget",
    "close_all_FigureWidget",
]

_active_figures: list[go.FigureWidget] = []

def create_colorscale(cmap_name, over_color, under_color):
    """
    Create a Plotly colorscale with custom over/under colors.

    Parameters:
    -----------
    cmap_name : str
        Plotly colorscale name (e.g., 'Viridis', 'Plasma', 'Blues')
    over_color : str
        Color for values above the maximum (e.g., 'pink', 'rgb(255, 0, 0)'). Note that
        you can also use 'rgba(255, 255, 255, 0)' for a transparent color.
    under_color : str
        Color for values below the minimum (e.g., 'white', 'rgb(255, 255, 255)')

    Returns:
    --------
    list
        Plotly colorscale as a list of [position, color] pairs
    """
    import plotly.express as px

    plotly_cmap = px.colors.sequential.__dict__[cmap_name]
    n = len(plotly_cmap)
    eps = 0.01
    colorscale = (
        [[0.0, under_color]]
        + [[eps + (1 - 2 * eps) * i / (n - 1), plotly_cmap[i]] for i in range(n)]
        + [[1.0, over_color]]
    )
    return colorscale


def plot_profiles_widget(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    xlabel: str = "x",
    ylabel: str = "y",
    zlabel: str = "z",
    unitsx: str = "pixels",
    unitsy: str = "pixels",
    unitsz: str = "a.u.",
    interactive: bool = True,
    xo_for_profile: float | None = None,
    yo_for_profile: float | None = None,
    center_at_cm: bool = False,
    profile_fwhm: bool = False,
    profile_coverage: float | None = 0.7615,
    contour_coverages: list = [0.50],
    color_for_contours=["#FF10F0", "#00FFFF", "#00FF00"],
    colorscale: str | list = "Magma",
    zmax_coverage: float | None = None,
    zmin_coverage: float | None = None,
    over_color: str = "magenta",
    under_color: str = "rgba(255, 255, 255, 0)",
    calc_stats_contours: bool = False,
):
    """Create an interactive Plotly figure with a heatmap and linked profiles.

    Displays ``z(x, y)`` as a heatmap with two profiles that update on click.
    Optionally adds contour lines at specified coverages and calculates
    area/centroid stats.

    Parameters
    ----------
    x : np.ndarray
        1D array of x-coordinates, length N.
    y : np.ndarray
        1D array of y-coordinates, length M.
    z : np.ndarray
        2D array of intensity/density values, shape (M, N).
    xlabel : str, optional
        Axis label for x. Default ``"x"``.
    ylabel : str, optional
        Axis label for y. Default ``"y"``.
    zlabel : str, optional
        Axis label for z (intensity). Default ``"z"``.
    unitsx : str, optional
        Units string for x-axis stats output. Default ``"pixels"``.
    unitsy : str, optional
        Units string for y-axis stats output. Default ``"pixels"``.
    unitsz : str, optional
        Units string for z-axis stats output. Default ``"a.u."``.
    interactive : bool, optional
        If True, clicking the heatmap updates the profiles. Default ``True``.
    xo_for_profile : float or None, optional
        x-coordinate for the initial profile slice. If None, no profile is
        drawn on load (unless ``center_at_cm=True``).
    yo_for_profile : float or None, optional
        y-coordinate for the initial profile slice. Defaults to
        ``xo_for_profile`` if None and ``xo_for_profile`` is set.
    center_at_cm: bool, optional
        If True, automatically centers profiles at the centroid of the 50th
        coverage HDR region. Overrides ``xo_for_profile`` and
        ``yo_for_profile``. Default ``False``.
    profile_fwhm : bool, optional
        If True, annotations show FWHM instead of coverage width and forces
        ``profile_coverage=0.7615``. Default ``False``.
    profile_coverage : float | None, optional
        coverage (0-1) used for the filled profile region and width
        annotation. Pass None to disable. Default ``0.7615``.
    contour_coverages : list, optional
        List of coverages (0-1) for HDR contour lines on the heatmap.
        Default ``[0.50]``.
    color_for_contours : list, optional
        Hex color strings for contour lines, one per coverage (cycles if
        shorter). Default ``["#FF10F0", "#00FFFF", "#00FF00"]``.
    colorscale : str or list, optional
        Plotly colorscale for the heatmap. Default ``"Magma"``.
        Other options include ``"Viridis"``, ``"Plasma"``, ``"Cividis"``, ``"Inferno"``,
        ``"Jet"``, ``"Hot"``, ``"Rainbow"``, ``"Spectral"``, ``"RdBu"``, ``"RdGy"``, ``"Greys"``.
        See https://plotly.com/python/builtin-colorscales/#builtin-sequential-color-scales
    zmax_coverage, zmin_coverage : float | None, optional
        If set, the heatmap's zmax and zmin are set to the HDR thresholds at these coverages, respectively. Pass None to disable. Default ``None``.
        *Note* that it is related to the maximum coverage. `zmax_coverage=0.1` means we saturate the top 10% of values to the same color.  `zmin_coverage=0.9` means we saturate the bottom 10% of values to the same color.
    calc_stats_contours : bool, optional
        If True, prints area, diameter, centroid, and projection widths for
        each contour coverage and stores them in the returned state dict.
        Default ``False``.

    Returns
    -------
    fig : go.FigureWidget
        The interactive Plotly figure.
    state : dict
        Live state dict updated on each click. Contains ``'inputs'`` always;
        ``'1d-profile-stat'`` after a click when ``profile_coverage`` is set;
        ``'2D-stat'`` when ``calc_stats_contours=True``.

    Example
    -------

    ```python

    x = np.linspace(-5, 5, 1000)
    y = np.linspace(-5, 5, 800)
    X, Y = np.meshgrid(x, y)
    Z = np.exp(-(X**2 + Y**2) / (2 * 1.0**2)) + 0.1 * np.random.rand(*X.shape)

    fig, state = plot_profiles_widget(
        x,
        y,
        Z,
        xlabel="X (mm)",
        ylabel="Y (mm)",
        zlabel="Intensity (a.u.)",
        unitsx="mm",
        unitsy="mm",
        unitsz="a.u.",
        xo_for_profile=0.0,
        yo_for_profile=0.0,
    )


    if in jupyter notebook:
    ```python
    fig.show()  # <= THIS IS NEEDED TO SHOW THE FIGURE IN A JUPYTER NOTEBOOK, but will not work in a plain Python script or terminal
    ```

    if in non-notebook environment:
    ```python
    go.Figure(fig).show(renderer="browser")  # <= THIS IS NEEDED TO SHOW THE FIGURE IN A BROWSER
    ```

    but the last approach will not have the interactive click callbacks. This is a limitation of Plotly's
    FigureWidget, which relies on Jupyter's comms for interactivity. To have interactive profiles,
    you must be in a Jupyter environment (not plain Python script or terminal).
    """

    state = {}
    state["inputs"] = {
        "xlabel": xlabel,
        "ylabel": ylabel,
        "zlabel": zlabel,
        "unitsx": unitsx,
        "unitsy": unitsy,
        "unitsz": unitsz,
        "xo_for_profile": xo_for_profile,
        "yo_for_profile": yo_for_profile,
        "center_at_cm": center_at_cm,
        "interactive": interactive,
        "contour_coverages": contour_coverages,
        "color_for_contours": color_for_contours,
        "calc_stats_contours": calc_stats_contours,
    }

    xl, yl, zl = x.tolist(), y.tolist(), z.tolist()
    nx, ny = len(x), len(y)

    if not interactive and xo_for_profile is None:
        print_warning("interactive=False but xo_for_profile is None. Forcing center_at_cm=True to enable xy profiles")
        center_at_cm = True

    if not (len(x) == len(z[0]) and len(y) == len(z)):
        raise ValueError("Length of x and y must match dimensions of z")

    if center_at_cm:
        mask = z >= hdr2d(z, x=x, y=y, coverage=0.5)
        z_masked = z * mask
        proj_x = z_masked.sum(axis=0)
        proj_y = z_masked.sum(axis=1)
        center_mass_x = np.sum(x * proj_x) / np.sum(proj_x)
        center_mass_y = np.sum(y * proj_y) / np.sum(proj_y)

        xo_for_profile = nearest(x, center_mass_x)
        yo_for_profile = nearest(y, center_mass_y)
        print_warning(
            f"center_at_cm=True overrides xo_for_profile and yo_for_profile.\n"
            f"Automatically centering profiles at peak"
            f"(x={xo_for_profile:.3f} {unitsx}, y={yo_for_profile:.3f} {unitsy})."
        )

    try:
        print_info("Creating FigureWidget for interactive profiles.")
        fig = go.FigureWidget(  # registered in _active_figures for close_all_figures()
            make_subplots(
                rows=2,
                cols=2,
                column_widths=[0.75, 0.25],
                row_heights=[0.65, 0.35],
                shared_xaxes="columns",  # type: ignore
                shared_yaxes="rows",  # type: ignore
                horizontal_spacing=0.04,
                vertical_spacing=0.04,
            )
        )
        print_done("FigureWidget created successfully.")
    except Exception as e:
        print_warning(f"Failed to create FigureWidget: {e}\nFalling back to go.Figure (non-interactive).")
        fig = go.Figure(
            make_subplots(
                rows=2,
                cols=2,
                column_widths=[0.75, 0.25],
                row_heights=[0.65, 0.35],
                shared_xaxes="columns",  # type: ignore
                shared_yaxes="rows",  # type: ignore
                horizontal_spacing=0.04,
                vertical_spacing=0.04,
            )
        )

    _active_figures.append(fig)  # type: ignore

    fig.update_layout(
        font=dict(family="Georgia", size=14, color="#3B3B3B"),
        title=dict(font=dict(size=16)),
        height=800,
        width=1000,
    )

    _cbar = dict(
        thickness=20,
        len=0.75,
        lenmode="fraction",
        x=1.1,
        title=dict(text="Intensity", side="top"),
    )

    _custom_cmap = create_colorscale(colorscale, over_color, under_color)
    _zmax = None if zmax_coverage is None else hdr(z.ravel(), coverage=zmax_coverage)
    _zmin = None if zmin_coverage is None else hdr(z.ravel(), coverage=zmin_coverage)

    print_log(
        f"[DEBUG] Using colorscale={colorscale} with zmin={_zmin} and zmax={_zmax} based on coverages "
        f"{zmin_coverage} and {zmax_coverage}."
    )
    heatmap = go.Heatmap(
        x=xl,
        y=yl,
        z=zl,
        colorscale=_custom_cmap,
        colorbar=_cbar,
        # cmin=_zmin,
        # cmax=_zmax,
        zmin=_zmin,
        zmax=_zmax,
        zsmooth=False,
        hovertemplate="x: %{x:.3f}<br>y: %{y:.3f}<br>z: %{z:.4f}<extra></extra>",
    )
    x_prof = go.Scatter(
        x=xl,
        y=[0.0] * nx,
        mode="lines+markers",
        line=dict(color="rgba(70, 130, 180, 0.5)", width=1.5),
        name="X profile",
        marker=dict(size=4, color="#4682B4", symbol="x"),
        hoverinfo="x+y",
    )
    y_prof = go.Scatter(
        x=[0.0] * ny,
        y=yl,
        mode="lines+markers",
        line=dict(color="rgba(255, 99, 71, 0.5)", width=1.5),
        name="Y profile",
        marker=dict(size=4, color="#FF6347", symbol="x"),
        hoverinfo="x+y",
    )

    fig.add_trace(heatmap, row=1, col=1)
    fig.add_trace(x_prof, row=2, col=1)
    fig.add_trace(y_prof, row=1, col=2)
    _x_prof_trace = fig.data[-2]
    _y_prof_trace = fig.data[-1]

    if profile_fwhm:
        profile_coverage = 0.7615
        print_warning("Using profile_fwhm=True. This forces profile_coverage=0.7615.")

    if profile_coverage is not None:
        _fc = "rgba({},{},{},0.5)".format(*pc.hex_to_rgb("#FF404092"))
        x_prof_fill = go.Scatter(
            x=xl,
            y=[None] * nx,
            mode="none",
            fill="tozeroy",
            fillcolor=_fc,
            showlegend=True,
            name=f"Line Profile {profile_coverage * 100:.2f}% coverage",
        )
        y_prof_fill = go.Scatter(
            x=[None] * ny,
            y=yl,
            mode="none",
            fill="tozerox",
            fillcolor=_fc,
            showlegend=False,
        )

        fig.add_trace(x_prof_fill, row=2, col=1)
        fig.add_trace(y_prof_fill, row=1, col=2)

        _x_prof_fill_trace = fig.data[-2]
        _y_prof_fill_trace = fig.data[-1]
    else:
        _x_prof_fill_trace = None
        _y_prof_fill_trace = None

    if calc_stats_contours:
        fwhm_x = fwhm(x, z.sum(axis=0))
        fwhm_y = fwhm(y, z.sum(axis=1))

        print_info(
            f"FWHM from numerical 1D variances of projections = "
            f"{xlabel}: {fwhm_x:.3f} {unitsx}, {ylabel}: {fwhm_y:.3f} {unitsy}"
        )

        step_for_clines = max(1, min(nx, ny) // 100)
        _colors = list(color_for_contours)
        if len(_colors) < len(contour_coverages):
            _colors *= len(contour_coverages)

        state["2D-stat"] = {}

        for _covrg, _lc in zip(contour_coverages, _colors):
            _z_thresh = hdr2d(z, x=x, y=y, coverage=_covrg)
            fig.add_trace(
                go.Contour(
                    x=x[::step_for_clines].tolist(),
                    y=y[::step_for_clines].tolist(),
                    z=z[::step_for_clines, ::step_for_clines].tolist(),
                    showscale=False,
                    showlegend=True,
                    hoverinfo="skip",
                    name=f"Area {int(_covrg * 100)}% coverage",
                    contours=dict(coloring="none", start=_z_thresh, end=_z_thresh),
                    line=dict(color=_lc, width=2, dash="dash"),
                ),
                row=1,
                col=1,
            )

            if unitsx == unitsy:
                area_units = f"{unitsx}²" if unitsx else "area-units"
            else:
                area_units = f"{unitsx} x {unitsy}" if unitsx and unitsy else "area-units"
            mask = z >= _z_thresh
            cell_areas = np.outer(np.gradient(y), np.gradient(x))
            area = np.sum(cell_areas[mask])
            center_mass_x = np.sum(x[None, :] * mask * cell_areas) / area
            center_mass_y = np.sum(y[:, None] * mask * cell_areas) / area
            diamter_x = np.ptp(x[mask.any(axis=0)]) if np.any(mask.any(axis=0)) else 0.0
            diamter_y = np.ptp(y[mask.any(axis=1)]) if np.any(mask.any(axis=1)) else 0.0
            proj_x, proj_y = z.max(axis=0), z.max(axis=1)
            integrated_width_x = np.ptp(x[proj_x >= hdr(proj_x, x=x, coverage=_covrg)])
            integrated_width_y = np.ptp(y[proj_y >= hdr(proj_y, x=y, coverage=_covrg)])

            print_info(
                f"\n\t*** {int(_covrg * 100)}% coverage:\n"
                f"\t\t- Area = {area:.3f} {area_units}\n"
                f"\t\t- Diameter = {xlabel}: {diamter_x:.3f} {unitsx}, {ylabel}: {diamter_y:.3f} {unitsy}\n"
                f"\t\t- Centroid = {xlabel}: {center_mass_x:.3f} {unitsx}, {ylabel}: {center_mass_y:.3f} {unitsy}\n"
                f"\t\t- Projection width:\n"
                f"\t\t\t* {xlabel}: {integrated_width_x:.3f} {unitsx}\n"
                f"\t\t\t* {ylabel}: {integrated_width_y:.3f} {unitsy}\n"
            )

            state["2D-stat"][f"p{_covrg:.4g}"] = {
                "area": area,
                "area_units": area_units,
                "diameter_x": diamter_x,
                "diameter_y": diamter_y,
                "diameter_units": (unitsx, unitsy),
                "centroid_x": center_mass_x,
                "centroid_y": center_mass_y,
                "centroid_units": (unitsx, unitsy),
            }

    fig.update_layout(
        template="plotly_white",
        title="Click the heatmap to show profiles",
        showlegend=True,
        legend=dict(x=0.72, y=0.32, xanchor="left", yanchor="top", bgcolor="rgba(255,255,255,0.8)"),
    )
    fig.update_yaxes(title_text=ylabel, row=1, col=1)
    fig.update_xaxes(showticklabels=True, title_text=xlabel, side="top", row=1, col=1)
    fig.update_xaxes(title_text=zlabel, row=1, col=2)
    fig.update_yaxes(showticklabels=True, side="right", row=1, col=2)
    fig.update_xaxes(showticklabels=True, title_text=zlabel, side="top", row=1, col=2)
    fig.update_yaxes(title_text=zlabel, row=2, col=1)

    def _on_heatmap_click(trace, points, selector):
        if not points.xs:
            return
        _plot_profiles_at_point(points.xs[0], points.ys[0])

    def _plot_profiles_at_point(xo, yo):
        xi = int(np.argmin(np.abs(x - xo)))
        yi = int(np.argmin(np.abs(y - yo)))
        state["xi"] = xi
        state["yi"] = yi
        state["x_profile"] = z[yi, :]
        state["y_profile"] = z[:, xi]

        with fig.batch_update():
            _x_prof_trace.y = z[yi, :].tolist()
            _y_prof_trace.x = z[:, xi].tolist()
            if profile_coverage is not None:
                _thresh_x = hdr(z[yi, :], x=x, coverage=profile_coverage)
                _thresh_y = hdr(z[:, xi], x=y, coverage=profile_coverage)
                _x_prof_fill_trace.y = [v if v >= _thresh_x else None for v in z[yi, :].tolist()]  # type: ignore
                _y_prof_fill_trace.x = [v if v >= _thresh_y else None for v in z[:, xi].tolist()]  # type: ignore

                _mask_x = z[yi, :] >= _thresh_x
                _mask_y = z[:, xi] >= _thresh_y
                _width_x = float(np.ptp(x[_mask_x])) if _mask_x.any() else 0.0
                _width_y = float(np.ptp(y[_mask_y])) if _mask_y.any() else 0.0

                _fwhm_x_profile = fwhm(x, z[yi, :])
                _fwhm_y_profile = fwhm(y, z[:, xi])

                state["1d-profile-stat"] = {
                    "coverage": profile_coverage,
                    "width_x": _width_x,
                    "width_y": _width_y,
                    "size_units": (unitsx, unitsy),
                    "fwhm_x_profile": _fwhm_x_profile,
                    "fwhm_y_profile": _fwhm_y_profile,
                }

                _ann_x = float((x[_mask_x].max() + x[_mask_x].min()) / 2) if _mask_x.any() else 0.0
                _ann_y = float((_thresh_x) / 2) if _mask_x.any() else 0.0
                _ann_xr = float((_thresh_y) / 2) if _mask_y.any() else 0.0
                _ann_yr = float((y[_mask_y].max() + y[_mask_y].min()) / 2) if _mask_y.any() else 0.0

                if profile_fwhm:
                    fig.layout.annotations = [
                        dict(
                            x=_ann_xr,
                            y=_ann_yr,
                            xref=_y_prof_trace.xaxis,  # type: ignore
                            yref=_y_prof_trace.yaxis,  # type: ignore
                            text=f"Profile FWHM<br>y={_fwhm_y_profile:.3f} {unitsy}",
                            showarrow=False,
                            font=dict(size=12),
                        ),
                        dict(
                            x=_ann_x,
                            y=_ann_y,
                            xref=_x_prof_trace.xaxis,  # type: ignore
                            yref=_x_prof_trace.yaxis,  # type: ignore
                            text=f"Profile FWHM<br>x={_fwhm_x_profile:.3f} {unitsx}",
                            showarrow=False,
                            font=dict(size=12),
                        ),
                    ]
                else:
                    fig.layout.annotations = [
                        dict(
                            x=_ann_xr,
                            y=_ann_yr,
                            xref=_y_prof_trace.xaxis,  # type: ignore
                            yref=_y_prof_trace.yaxis,  # type: ignore
                            text=f"{profile_coverage * 100:.1f}% coverage<br>width y={_width_y:.3f} {unitsy}",
                            showarrow=False,
                            font=dict(size=12),
                        ),
                        dict(
                            x=_ann_x,
                            y=_ann_y,
                            xref=_x_prof_trace.xaxis,  # type: ignore
                            yref=_x_prof_trace.yaxis,  # type: ignore
                            text=f"{profile_coverage * 100:.1f}% coverage<br>width x={_width_x:.3f} {unitsx}",
                            showarrow=False,
                            font=dict(size=12),
                        ),
                    ]

            fig.layout.shapes = [
                dict(
                    type="line",
                    xref="x",
                    yref="y",
                    x0=x[xi],
                    x1=x[xi],
                    y0=float(y[0]),
                    y1=float(y[-1]),
                    line=dict(color="#FF6347", width=1.5, dash="dash"),
                ),
                dict(
                    type="line",
                    xref="x",
                    yref="y",
                    x0=float(x[0]),
                    x1=float(x[-1]),
                    y0=y[yi],
                    y1=y[yi],
                    line=dict(color="#4682B4", width=1.5, dash="dash"),
                ),
            ]
            fig.layout.title.text = f"Profiles at x={x[xi]:.3f}, y={y[yi]:.3f}"
            _x_prof_trace.name = f"X profile @ y={y[yi]:.2f}"
            _y_prof_trace.name = f"Y profile @ x={x[xi]:.2f}"

    if xo_for_profile is not None:
        if yo_for_profile is None:
            yo_for_profile = xo_for_profile
        print_log(
            f"xo_for_profile={xo_for_profile:.3f} and yo_for_profile={yo_for_profile:.3f} "
            f"provided, plotting profiles at this x-coordinate."
        )
        _plot_profiles_at_point(xo_for_profile, yo_for_profile)

    if not interactive:
        return fig, state

    for trace in fig.data:
        trace.on_click(_on_heatmap_click)  # type: ignore

    return fig, state


def close_all_FigureWidget() -> None:
    """Close all FigureWidget instances created by plot_profiles_widget.

    Notes
    -----
    Tears down the kernel comm object for each widget, releasing any pending
    click callbacks. Equivalent to ``plt.close('all')`` for Plotly widgets.
    """

    print_info(f"Closing FigureWidget instances.")
    if not _active_figures:
        print_info("No active FigureWidget instances to close.")
    else:
        print_info(f"Found {len(_active_figures)} active FigureWidget(s) to close.")

    for fig in _active_figures:
        print_info(f"Closing FigureWidget: {fig.layout.title.text!r}")
        fig.close()
    _active_figures.clear()


_MODULE_FUNCTIONS = [k for k, v in globals().items() if callable(v) and not k.startswith("_")]


def _example_usage(interactive=True):
    x = np.linspace(-5, 5, 1000)
    y = np.linspace(-5, 5, 800)
    X, Y = np.meshgrid(x, y)
    Z = np.exp(-(X**2 + Y**2) / (2 * 1.0**2))
    Z = Z / Z.max() * 100  # normalize to 1.0 max
    Z += 1 * np.random.rand(*X.shape)

    fig, state = plot_profiles_widget(
        x,
        y,
        Z,
        xlabel="X (mm)",
        ylabel="Y (mm)",
        zlabel="Intensity (a.u.)",
        unitsx="mm",
        unitsy="mm",
        unitsz="a.u.",
        xo_for_profile=0.0,
        yo_for_profile=0.0,
        interactive=interactive,
        zmax_coverage=0.25,
        zmin_coverage=0.75,
        over_color="magenta",
        under_color="rgba(255, 255, 255, 0)",
    )

    return fig, state


if __name__ == "__main__":
    print("\n### wg-toolkit.visualization functions:")
    for name in _MODULE_FUNCTIONS:
        print(f"  {name}")

    print("\n### Example usage of plot_profiles_widget:")
    x = np.linspace(-5, 5, 1000)
    y = np.linspace(-5, 5, 800)
    X, Y = np.meshgrid(x, y)
    Z = np.exp(-(X**2 + Y**2) / (2 * 1.0**2)) + 0.1 * np.random.rand(*X.shape)

    fig, state = _example_usage(interactive=False)
    print_done("Example figure created. Opening in browser...")

    go.Figure(fig).show(renderer="browser")  # FigureWidget cannot render to browser directly
    print_done("END of the script.")
