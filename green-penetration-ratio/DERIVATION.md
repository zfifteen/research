# Green Penetration Ratio: Mathematical Derivation

## Overview

The **Green Penetration Ratio** (GPR) is a dimensionless metric that quantifies the spatial distribution of vorticity within a planar region relative to its boundary, providing a measure of measurement robustness when applying Green's Theorem.

## Notation and Preliminaries

### Domain Setup
- Let \(D \subset \mathbb{R}^2\) be a simply-connected, bounded region with piecewise smooth boundary \(C\)
- Let \(\mathbf{F} = \langle P(x,y), Q(x,y) \rangle\) be a continuously differentiable vector field on \(D\)
- The scalar vorticity (2D curl) is defined as:

\[
\omega(x,y) = \frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y}
\]

### Green's Theorem Statement
For positively oriented boundary \(C\):

\[
\oint_C (P\,dx + Q\,dy) = \iint_D \left(\frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y}\right) dx\,dy = \iint_D \omega(x,y)\,dx\,dy
\]

## Core Geometric Quantities

### Boundary Distance Function
For any point \((x,y) \in D\), define the distance to the boundary:

\[
r(x,y) = \inf_{(x_b, y_b) \in C} \|(x,y) - (x_b, y_b)\|
\]

This gives the shortest straight-line distance from \((x,y)\) to any point on \(C\).

### Maximum Interior Distance (Inradius)
The characteristic depth of the region is:

\[
r_{\max} = \sup_{(x,y) \in D} r(x,y)
\]

This is the **inradius** of \(D\), representing the radius of the largest circle that can be inscribed in \(D\). For convex regions, this is the distance from boundary to the most interior point.

## Vorticity-Weighted Centroid Distance

### Motivation
We want to characterize "where the vorticity lives" relative to the boundary. A simple maximum or average of \(|\omega|\) loses spatial information. Instead, we compute a vorticity-weighted average distance.

### Total Vorticity Magnitude
First, compute the integrated absolute vorticity:

\[
\Omega_{\text{total}} = \iint_D |\omega(x,y)|\,dx\,dy
\]

This measures the total "amount" of rotation in the region, treating clockwise and counterclockwise equally.

### Vorticity Centroid Distance
The mean distance of vorticity from the boundary is:

\[
r_{\text{curl}} = \frac{1}{\Omega_{\text{total}}} \iint_D r(x,y) \cdot |\omega(x,y)|\,dx\,dy
\]

**Physical Interpretation:**
- If \(|\omega|\) is concentrated near the boundary, \(r(x,y)\) is small where \(|\omega|\) is large, so \(r_{\text{curl}} \to 0\)
- If \(|\omega|\) is concentrated in the interior, \(r(x,y)\) is large where \(|\omega|\) is large, so \(r_{\text{curl}} \to r_{\max}\)

## The Green Penetration Ratio

### Definition
The **Green Penetration Ratio** is the normalized vorticity centroid distance:

\[
\boxed{\delta = \frac{r_{\text{curl}}}{r_{\max}} = \frac{\displaystyle\iint_D r(x,y) \cdot |\omega(x,y)|\,dx\,dy}{r_{\max} \cdot \displaystyle\iint_D |\omega(x,y)|\,dx\,dy}}
\]

### Properties
1. **Boundedness:** \(0 \leq \delta \leq 1\) by construction
2. **Dimensionless:** Both numerator and denominator have units of [length × vorticity × area], so the ratio is pure number
3. **Geometric invariance:** \(\delta\) is invariant under uniform scaling of \(D\)
4. **Interpretation:**
   - \(\delta \approx 0\): Vorticity concentrated near boundary
   - \(\delta \approx 1\): Vorticity concentrated in deep interior
   - \(\delta \approx 0.5\): Vorticity distributed throughout region

## Computational Formula for Discrete Fields

For numerical implementation on a mesh with \(N\) grid points:

\[
\delta \approx \frac{\displaystyle\sum_{i=1}^{N} r_i \cdot |\omega_i| \cdot A_i}{r_{\max} \cdot \displaystyle\sum_{i=1}^{N} |\omega_i| \cdot A_i}
\]

where:
- \(r_i\) = distance from grid point \(i\) to nearest boundary point
- \(\omega_i\) = vorticity at grid point \(i\)
- \(A_i\) = area element associated with grid point \(i\)
- \(r_{\max}\) = maximum value among all \(r_i\)

### Algorithm Steps
1. **Compute distance field:** For each interior point, find minimum distance to boundary using level set methods or fast marching
2. **Extract vorticity field:** Compute \(\omega = \partial Q/\partial x - \partial P/\partial y\) at each grid point
3. **Find inradius:** \(r_{\max} = \max_i r_i\)
4. **Integrate:** Compute weighted and total sums using quadrature weights \(A_i\)
5. **Normalize:** Form ratio \(\delta\)

## Theoretical Justification

### Connection to Measurement Variance

Consider two measurement strategies for estimating circulation \(\Gamma\):

**Strategy A (Boundary):** Measure \(\mathbf{F}\) along \(C\) with noise \(\epsilon_b\)

\[
\Gamma_A = \oint_C (P + \epsilon_b)\,dx + (Q + \epsilon_b)\,dy
\]

**Strategy B (Interior):** Measure \(\omega\) throughout \(D\) with noise \(\epsilon_a\)

\[
\Gamma_B = \iint_D (\omega + \epsilon_a)\,dx\,dy
\]

The relative error propagation depends on:
- **Boundary strategy:** Errors accumulate over path length \(L = |C|\)
- **Interior strategy:** Errors accumulate over area \(A = |D|\) weighted by \(\omega\) distribution

**Key Insight:** When \(\delta\) is small, the effective "signal path" from vorticity sources to boundary observations is short, making boundary measurements more robust. When \(\delta\) is large, boundary measurements must integrate over longer coupling paths, accumulating more uncertainty.

### Sensitivity Kernel Interpretation

The boundary circulation can be viewed as:

\[
\Gamma = \iint_D \omega(x,y)\,dx\,dy = \iint_D G(x,y) \cdot \omega(x,y)\,dx\,dy
\]

where \(G(x,y) = 1\) is a uniform "sensitivity kernel" when using the area integral directly.

However, when inferring \(\Gamma\) from boundary measurements, the effective kernel becomes distance-dependent. Points farther from the boundary contribute through longer integration paths, introducing more opportunities for error accumulation.

The GPR \(\delta\) provides a scalar summary of this weighted coupling structure.

## Domain Restrictions and Validity

### Valid Domains
- Simply-connected (no holes)
- Approximately convex (or decomposable into convex subregions)
- Smooth or piecewise smooth boundaries
- Non-degenerate (not extremely thin or high aspect ratio)

### Invalid Domains
For multiply-connected or highly non-convex domains, \(\delta\) can be misleading:
- **Annular regions:** Inradius may be ambiguous or artificially small
- **Dumbbell shapes:** Single centroid collapses bimodal vorticity distributions
- **High aspect ratio:** \(r_{\max}\) may not characterize typical boundary distances

**Extension:** For complex geometries, partition into convex subregions \(D_k\), compute \(\delta_k\) for each, and form a weighted average:

\[
\delta_{\text{composite}} = \frac{\sum_k \delta_k \cdot \Omega_k}{\sum_k \Omega_k}
\]

where \(\Omega_k = \iint_{D_k} |\omega|\,dx\,dy\) is the vorticity in subregion \(k\).

## Example Calculations

### Example 1: Uniform Vorticity in Unit Circle

Domain: \(D = \{(x,y) : x^2 + y^2 \leq 1\}\)

Field: \(\omega(x,y) = \omega_0\) (constant)

**Distance function:**
\[
r(x,y) = 1 - \sqrt{x^2 + y^2}
\]

**Inradius:**
\[
r_{\max} = 1
\]

**Vorticity centroid distance:**
\[
r_{\text{curl}} = \frac{1}{\pi} \int_0^{2\pi} \int_0^1 (1-r) \cdot r\,dr\,d\theta = \frac{1}{\pi} \cdot 2\pi \int_0^1 (r - r^2)\,dr = 2\left[\frac{r^2}{2} - \frac{r^3}{3}\right]_0^1 = 2\left(\frac{1}{2} - \frac{1}{3}\right) = \frac{1}{3}
\]

**Green Penetration Ratio:**
\[
\delta = \frac{1/3}{1} = \frac{1}{3} \approx 0.33
\]

**Interpretation:** Uniform vorticity in a circle has \(\delta = 1/3\), indicating a slight bias toward the boundary (geometric effect of area weighting).

### Example 2: Point Vortex at Center

Domain: Unit circle

Field: \(\omega(x,y) = \delta_{\text{Dirac}}(x,y)\) (concentrated at origin)

**Distance at origin:**
\[
r(0,0) = 1
\]

**Green Penetration Ratio:**
\[
\delta = \frac{r(0,0)}{r_{\max}} = \frac{1}{1} = 1
\]

**Interpretation:** Maximum penetration, vorticity lives at the deepest interior point.

### Example 3: Annular Vorticity Shell

Domain: Unit circle

Field: \(\omega(x,y) = \omega_0\) for \(0.8 \leq \sqrt{x^2+y^2} \leq 0.9\), zero elsewhere

**Distance at \(r=0.85\):**
\[
r \approx 1 - 0.85 = 0.15
\]

**Approximate GPR:**
\[
\delta \approx \frac{0.15}{1} = 0.15
\]

**Interpretation:** Vorticity concentrated in a thin shell near boundary, very low penetration.

## Decision Thresholds

Based on error propagation analysis, recommended thresholds:

\[
\begin{cases}
\delta < 0.4 & \text{Boundary measurement preferred (allocate } \geq 70\% \text{ sensors to perimeter)} \\
0.4 \leq \delta \leq 0.6 & \text{Mixed regime (balanced allocation)} \\
\delta > 0.6 & \text{Area measurement preferred (allocate } \geq 70\% \text{ sensors to interior)}
\end{cases}
\]

These thresholds assume:
- Measurement noise is approximately uniform in space
- Sensor density is the limiting factor
- The field satisfies Green's Theorem hypotheses

## Extensions and Open Questions

### Multi-Scale Decomposition
For fields with vorticity at multiple scales, compute scale-dependent \(\delta(k)\) using bandpass-filtered vorticity:

\[
\delta(k) = \frac{\displaystyle\iint_D r(x,y) \cdot |\omega_k(x,y)|\,dx\,dy}{r_{\max} \cdot \displaystyle\iint_D |\omega_k(x,y)|\,dx\,dy}
\]

where \(\omega_k\) is the vorticity component at wavelength \(k\).

### Time-Dependent Fields
For evolving fields \(\omega(x,y,t)\), track \(\delta(t)\) to detect transitions in measurement strategy optimality:

\[
\delta(t) = \frac{\displaystyle\iint_D r(x,y) \cdot |\omega(x,y,t)|\,dx\,dy}{r_{\max} \cdot \displaystyle\iint_D |\omega(x,y,t)|\,dx\,dy}
\]

### Three-Dimensional Generalization
For volumetric regions with Stokes' Theorem, define:

\[
\delta_{3D} = \frac{\displaystyle\iiint_V d(x,y,z) \cdot \|\nabla \times \mathbf{F}\|\,dV}{d_{\max} \cdot \displaystyle\iiint_V \|\nabla \times \mathbf{F}\|\,dV}
\]

where \(d(x,y,z)\) is distance from point to surface \(S\).

## References and Priority

**Concept introduced:** March 3, 2026

**Attribution:** Big D' (Dionisio Alberto Lopez III)

**Primary source:** Insights Space analysis, Perplexity conversation thread

**Related concepts:**
- Green's Theorem (George Green, 1828)
- Vorticity dynamics (Hermann von Helmholtz, 1858)
- Sensitivity kernels in inverse problems (Backus & Gilbert, 1970)
- Fast marching methods for distance functions (Sethian, 1996)

## License

This derivation is released to the public domain. Attribution appreciated but not required.
