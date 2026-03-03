# Green Penetration Ratio (GPR)

A geometric diagnostic for choosing whether circulation in a 2D field should be measured primarily from the **boundary** (line integral) or from the **interior** (area integral) under fixed noise and sensor-budget constraints.

## 1. Full Explanation and Derivation

### 1.1 Starting Point: Green's Theorem

For a simply connected planar domain \(D\) with positively oriented boundary \(C\), and vector field \(\mathbf{F}=(P,Q)\):

\[
\oint_C (P\,dx + Q\,dy) = \iint_D \left(\frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y}\right)\,dA
\]

Define vorticity:

\[
\omega(x,y) = \frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y}
\]

The theorem guarantees equality of the two integrals, but not equal robustness under noisy, finite measurements.

### 1.2 Geometric Quantity: Distance to Boundary

Define pointwise interior depth:

\[
r(x,y) = \inf_{(x_b,y_b)\in \partial D}\|(x,y)-(x_b,y_b)\|
\]

and maximum interior depth (inradius-like scale):

\[
r_{\max} = \sup_{(x,y)\in D} r(x,y)
\]

### 1.3 Vorticity-Weighted Depth

Total absolute vorticity:

\[
\Omega_{\text{tot}} = \iint_D |\omega(x,y)|\,dA
\]

Vorticity-depth centroid:

\[
r_{\text{curl}} =
\frac{\iint_D r(x,y)\,|\omega(x,y)|\,dA}
     {\iint_D |\omega(x,y)|\,dA}
\]

### 1.4 Green Penetration Ratio

\[
\delta = \frac{r_{\text{curl}}}{r_{\max}}
=
\frac{\iint_D r(x,y)\,|\omega(x,y)|\,dA}
     {r_{\max}\iint_D |\omega(x,y)|\,dA}
\quad\in[0,1]
\]

Interpretation:
- \(\delta \to 0\): vorticity mass near the boundary
- \(\delta \to 1\): vorticity mass deep in the interior

### 1.5 Why \(0 \le \delta \le 1\)

Because \(0 \le r(x,y)\le r_{\max}\) everywhere in \(D\):
- \(0 \le r(x,y)|\omega(x,y)| \le r_{\max}|\omega(x,y)|\)
- integrating and dividing by \(r_{\max}\Omega_{\text{tot}}\) gives \(0\le \delta \le 1\)

### 1.6 Scale Invariance

If spatial coordinates are scaled by \(s>0\), then \(r\), \(r_{\text{curl}}\), and \(r_{\max}\) all scale by \(s\), so the ratio \(\delta=r_{\text{curl}}/r_{\max}\) is unchanged.

### 1.7 Discrete Computational Form

For grid points \(i\) with area weights \(A_i\):

\[
\delta \approx
\frac{\sum_i r_i |\omega_i| A_i}
     {r_{\max}\sum_i |\omega_i| A_i}
\]

Algorithm:
1. Build domain mask and boundary-distance field \(r_i\).
2. Compute vorticity \(\omega_i\).
3. Compute \(r_{\max}\), weighted numerator, and denominator.
4. Form \(\delta\), then apply decision thresholds.

### 1.8 Decision Rule

- \(\delta < 0.4\): boundary-heavy sensing
- \(0.4 \le \delta \le 0.6\): mixed strategy
- \(\delta > 0.6\): interior-heavy sensing

These thresholds are the working heuristic used across the white-paper scripts/docs.

## 2. Most Relevant Plots: `white_paper_1.py`

Note: this script currently contains scaffold placeholders and does not regenerate all 12 figures from source today; however, the referenced figures exist in `figures/`.

### Plot A: Monte Carlo Error vs GPR

![White Paper 1 - Monte Carlo Error vs GPR](figures/06_montecarlo_error_vs_gpr.png)

File: `figures/06_montecarlo_error_vs_gpr.png`

Why it matters:
- This is the central empirical-style plot for White Paper 1: error trend is shown as a function of \(\delta\), directly linking GPR to expected measurement robustness.
- It visualizes the operational crossover intuition behind the 0.4/0.6 regime split.
- It reframes Green's theorem from pure equality to strategy selection under uncertainty.

### Plot B: Recommended Sensor Allocation

![White Paper 1 - Sensor Allocation](figures/07_sensor_allocation.png)

File: `figures/07_sensor_allocation.png`

Why it matters:
- This plot turns theory into an actionable sensor-budget policy.
- It maps \(\delta\) to boundary/interior allocation percentages, which is what most experiment/design teams actually need.
- Together with Plot A, it provides both the "why" (error behavior) and "what to do" (allocation strategy).

## 3. Most Relevant Plots: `white_paper_2.py`

`white_paper_2.py` is fully executable and regenerates the `assets/` figure set.

### Plot A: GPR Comparison Across Canonical Test Cases

![White Paper 2 - GPR Bar Comparison](assets/whitepaper_fig2_gpr_comparison.png)

File: `assets/whitepaper_fig2_gpr_comparison.png`

Why it matters:
- Establishes that \(\delta\) differentiates physically distinct vorticity layouts (uniform, centered, ring-like, etc.).
- Shows the threshold overlays (\(0.4, 0.6\)) directly on computed results, making regime assignment immediate.
- Serves as the easiest "first proof" that GPR is a usable scalar control variable.

### Plot B: 2D Decision Map (Ring Position vs Width)

![White Paper 2 - 2D Decision Map](assets/whitepaper_fig4_decision_map.png)

File: `assets/whitepaper_fig4_decision_map.png`

Why it matters:
- Extends single-case bars into a continuous design space.
- Shows how both radial location and spread of vorticity jointly move \(\delta\), with explicit contour boundaries at \(0.4\) and \(0.6\).
- This is the most useful plot for planning sensor layouts before data collection.

## 4. Important Companion Docs (Summary + Links)

- [`DERIVATION.md`](DERIVATION.md)
  - Formal mathematical definition, properties, discrete formula, domain-validity discussion, and worked examples.
- [`HYPOTHESIS.md`](HYPOTHESIS.md)
  - High-level thesis: robustness asymmetry between boundary and interior formulations depends on vorticity penetration depth.
- [`WHITE_PAPER_1.md`](WHITE_PAPER_1.md)
  - 12-figure narrative walkthrough and practical interpretation (concept-heavy presentation style).
- [`WHITE_PAPER_2.md`](WHITE_PAPER_2.md)
  - Mathematical and computational walkthrough aligned with `white_paper_2.py` generated assets.
- [`INDUSTRY.md`](INDUSTRY.md)
  - Domain-specific adoption framing and potential ROI across aerospace, energy, biomedical, process, marine, and civil applications.

## 5. How To Run

From `green-penetration-ratio/`:

```bash
python3 white_paper_2.py
python3 white_paper_1.py
```

Expected dependencies:
- `numpy`
- `plotly` (image export path via kaleido-compatible setup)
- `matplotlib`
- `scipy`

## 6. Current Project State Notes

- `white_paper_2.py` is currently the most reproducible script for figure regeneration (`assets/*.png`).
- `white_paper_1.py` currently behaves like a partial scaffold (it prints completion text but does not regenerate all 12 figures by itself).
- Monte Carlo correlation claims should be interpreted carefully unless random seeds and noise model assumptions are fixed for deterministic validation.

## 7. Citation

Lopez III, D.A. (2026). *Green Penetration Ratio: A Novel Metric for Measurement Strategy Selection in Vector Field Analysis*.
