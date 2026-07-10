# Helpful notes

## Highest Density Region (HDR)

For a percentile p, the HDR is the **smallest region containing p of the total
probability mass**. Equivalently, it is the set of points above a threshold λ:

$$\text{HDR}(p) = \{x : z(x) \geq \lambda_p\}$$

where λ_p is chosen so that the integrated mass inside the region equals p.

The threshold λ_p is found by sorting points by descending density, accumulating
weighted mass, and reading off the density value where the cumulative sum first
reaches p. The result is always an existing value from z — no interpolation.

### 2D Cases
In **2D**, the HDR extends naturally to a surface z(x, y):

$$\text{HDR}(p) = \{(x, y) : z(x,y) \geq \lambda_p\}$$

The boundary of the 2D HDR is a **contour line** at level λ_p — the same contour
that a plotting library would draw at that intensity level. For a 2D Gaussian,
the 50% HDR boundary is the FWHM ellipse.


## Gaussian Statistics: Percentiles, σ, and FWHM

### Definition of σ

For a 1D Gaussian:

$$z(x) = A \exp\!\left(-\frac{(x-\mu)^2}{2\sigma^2}\right)$$

σ is the **standard deviation** — the distance from the mean to the inflection point.

Computed numerically as the weighted standard deviation:

$$\mu = \frac{\sum_i z_i\, x_i}{\sum_i z_i}, \qquad \sigma = \sqrt{\frac{\sum_i z_i\,(x_i - \mu)^2}{\sum_i z_i}}$$

---

### 1D Gaussian

$$\text{FWHM} = 2\sqrt{2 \ln 2}\;\sigma \approx 2.355\;\sigma$$

The FWHM interval contains **76.15%** of the total integral:

$$\texttt{hdr(x, z, 0.7615)} \;\Rightarrow\; \text{FWHM threshold}$$

---

### 2D Gaussian (any σ_x, σ_y, any correlation)

The FWHM ellipse (contour at z = z_max / 2) contains exactly **50%** of the total volume:

$$\texttt{hdr2d(x, y, z, 0.50)} \;\Rightarrow\; \text{FWHM ellipse}$$

This is exact for **all** 2D Gaussians, regardless of aspect ratio or correlation.

---

### 1D ↔ 2D Percentile Mapping (separable Gaussians only)

For separable Gaussian profiles, convert a 1D central-mass percentile to the
equivalent 2D enclosed-mass percentile with:

$$p_\text{2D} = 1 - \exp\!\left(-\left[\mathrm{erfinv}(p_\text{1D})\right]^2\right)$$

Here, `erfinv` is the inverse error function.

Short derivation (standard Gaussian):

$$p_\text{1D} = \operatorname{erf}\!\left(\frac{k}{\sqrt{2}}\right) \Rightarrow k = \sqrt{2}\,\operatorname{erfinv}(p_\text{1D})$$

For a 2D Gaussian, the enclosed mass inside radius $k$ is:

$$p_\text{2D} = 1 - e^{-k^2/2}$$

Substituting the 1D relation for $k$ gives:

$$p_\text{2D} = 1 - \exp\!\left(-\left[\operatorname{erfinv}(p_\text{1D})\right]^2\right)$$

| p_1D | p_2D | Meaning |
|------|------|---------|
| 0.7615 | 0.50 | FWHM |
| 0.50 | 0.22 | Half-maximum equivalent |

> **Caveat:** For non-Gaussian shapes, 1D and 2D HDR percentiles are incommensurable —
> there is no general mapping between them.
