# PhaseWall at the Gaussian Curvature Boundary: An Exploratory Technical Note

## Abstract
This note evaluates whether a phase-aware update rule at the Gaussian curvature boundary (`r = sigma`) is associated with better optimization outcomes under noisy conditions in the bundled benchmark report artifacts. The release is exploratory and artifact-backed: it includes report-derived result tables, hash verification, and claim recomputation checks, but it does not include seed-level raw logs or a full from-scratch rerun pipeline.

Published DOI references:
- Version DOI: [10.5281/zenodo.18847306](https://doi.org/10.5281/zenodo.18847306)
- Concept DOI: [10.5281/zenodo.18847305](https://doi.org/10.5281/zenodo.18847305)

## 1. Research Question and Scope
### 1.1 Research Question
Can a phase-aware damping rule at the Gaussian curvature transition (`r = sigma`) improve robustness and sample efficiency relative to a vanilla baseline under the reported noisy benchmark conditions?

### 1.2 Scope Boundaries
In scope:
- Geometric boundary claim for the Gaussian graph surface.
- Benchmark claims that can be traced to bundled report-derived artifacts.

Out of scope:
- Universal claims across optimizers, tasks, or noise regimes.
- Production-readiness claims.
- New empirical claims from unbundled experiments.

## 2. Method Definition
### 2.1 Radius Definitions
Isotropic normalized radius:

`r = ||x - mu|| / sigma`

Anisotropic extension (Mahalanobis radius):

`r = sqrt((x - mu)^T Sigma^-1 (x - mu))`

### 2.2 Baseline and Variant
Baseline in this note: Vanilla CMA-ES as defined in the bundled report (`artifacts/reports/PhaseWall_Benchmark_Report.pdf`) under the same evaluation budget, noise model, and seed count.

Variant in this note: PhaseWall (s=0.4), which applies soft radial damping in whitened z-space for samples outside the phase-wall radius.

Reported comparator set in the source report also includes LR-Adapt, 4x Population, and PW 0.4 + LR-Adapt.

## 3. Experimental Protocol (Report-Derived)
The benchmark protocol used for the reported evidence is:
- Functions: Sphere, Rosenbrock, Rastrigin, Ellipsoid
- Dimensions: 10, 20
- Seeds: 20 independent seeds per configuration
- Budget: 1,000 function evaluations per run
- Noise model: additive Gaussian noise with sigma = 0.1
- Metric: median final best value at fixed budget (lower is better)
- Statistical test: one-sided Wilcoxon signed-rank test (as reported)

Machine-auditable artifacts in this repository:
- `artifacts/results/phasewall_report_table.csv`
- `artifacts/results/phasewall_vs_vanilla_claims.csv`
- `artifacts/SHA256SUMS`

## 4. Results (Canonical Claims)
The canonical narrative compares Vanilla CMA-ES and PhaseWall (s=0.4) using `artifacts/results/phasewall_vs_vanilla_claims.csv`.

| Function | Dim | Vanilla Median | PhaseWall Median | ratio_vs_vanilla | improvement_factor | p_value |
|---|---:|---:|---:|---:|---:|---:|
| Sphere | 10 | -0.2133 | -0.1925 | 0.902485 | 1.108052 | 0.9836 |
| Sphere | 20 | -0.0913 | -0.0656 | 0.718510 | 1.391768 | 0.7625 |
| Rosenbrock | 10 | 8.52 | 8.47 | 0.994131 | 1.005903 | 0.5364 |
| Rosenbrock | 20 | 91.93 | 32.44 | 0.352877 | 2.833847 | 0.0120 |
| Rastrigin | 10 | 22.78 | 35.78 | 1.570676 | 0.636669 | 0.8058 |
| Rastrigin | 20 | 144.3 | 141.8 | 0.982675 | 1.017630 | 0.3781 |
| Ellipsoid | 10 | 1466.6 | 1788.4 | 1.219419 | 0.820063 | 0.7021 |
| Ellipsoid | 20 | 63294.2 | 101988 | 1.611332 | 0.620604 | 0.8847 |

Interpretation note:
- `ratio_vs_vanilla < 1.0` indicates lower median final objective for PhaseWall on that problem.
- The table shows mixed outcomes across function families, including improvements on some settings and degradations on others.

## 5. Reproducibility and Integrity Checks
Repository QC command:

```bash
bash scripts/qc_check.sh
```

This command verifies:
- Presence and structure of release-facing metadata/docs.
- Hash integrity for canonical artifacts listed in `artifacts/SHA256SUMS`.
- Numerical consistency of claim metrics in `phasewall_vs_vanilla_claims.csv` by recomputing
  `improvement_factor = vanilla_median / phasewall_median` and
  `ratio_vs_vanilla = phasewall_median / vanilla_median`.

## 6. Limitations
- Evidence is report-derived rather than regenerated from seed-level logs.
- No full rerun pipeline is included in this release.
- Conclusions are limited to the bundled benchmark protocol and should not be generalized beyond it.

## 7. Conclusion
The current artifact-backed evidence supports an exploratory claim: phase-aware damping at the Gaussian boundary is associated with better median final objective on some reported noisy settings (notably Rosenbrock 20D), while it is neutral or worse on others. This package is framed as a conservative evidence release, not a universal performance claim.

## Appendix A: Curvature Sign Derivation for the Gaussian Hill
Let

`z(x, y) = exp(-(x^2 + y^2) / (2 sigma^2))`

and `r^2 = x^2 + y^2`.

For a graph surface `z = f(x, y)`, Gaussian curvature is:

`K = (f_xx f_yy - f_xy^2) / (1 + f_x^2 + f_y^2)^2`

For this `z(x, y)`:

`z_x = -(x / sigma^2) z`

`z_y = -(y / sigma^2) z`

`z_xx = ((x^2 - sigma^2) / sigma^4) z`

`z_yy = ((y^2 - sigma^2) / sigma^4) z`

`z_xy = (xy / sigma^4) z`

Compute the numerator:

`z_xx z_yy - z_xy^2`

`= (z^2 / sigma^8) [ (x^2 - sigma^2)(y^2 - sigma^2) - x^2 y^2 ]`

`= (z^2 / sigma^8) [ sigma^4 - sigma^2 (x^2 + y^2) ]`

`= (z^2 / sigma^6) (sigma^2 - r^2)`

The denominator `(1 + z_x^2 + z_y^2)^2` is strictly positive, so the sign of `K` is the sign of `(sigma^2 - r^2)`:
- `r < sigma` -> `K > 0`
- `r = sigma` -> `K = 0`
- `r > sigma` -> `K < 0`

Therefore, the curvature sign change occurs exactly at `r = sigma`.

## References
1. `artifacts/reports/PhaseWall_Benchmark_Report.pdf`
2. `artifacts/results/phasewall_report_table.csv`
3. `artifacts/results/phasewall_vs_vanilla_claims.csv`
4. `scripts/qc_check.sh`
