# Benchmark Analysis (Report-Derived)

## Scope
This note summarizes benchmark evidence that is bundled with this repository. The canonical source is:
- `artifacts/reports/PhaseWall_Benchmark_Report.pdf` (v2.1, 2026-02-28)

This file is intentionally limited to report-derived claims that can be audited from repository artifacts.

## Run Manifest
- Objective functions: Sphere, Rosenbrock, Rastrigin, Ellipsoid
- Dimensions: 10 and 20
- Methods in the report table: Vanilla CMA-ES, LR-Adapt, 4x Population, PhaseWall (s=0.4), PW 0.4 + LR-Adapt
- Seeds: 20 independent seeds per method/function/dimension
- Evaluation budget: 1,000 function evaluations per run
- Noise model: additive Gaussian noise, sigma = 0.1
- Initial mean: `[3, 3, ..., 3]`
- Initial sigma: `2.0`
- Primary metric: median final best value at the fixed budget (lower is better)
- Statistical test in report: one-sided Wilcoxon signed-rank test (reported p-values)

Machine-auditable tables in this repository:
- `artifacts/results/phasewall_report_table.csv`
- `artifacts/results/phasewall_vs_vanilla_claims.csv`

## Verified Results (Report-Derived)
Interpretation for minimization objectives:
- `ratio_vs_vanilla = phasewall_median / vanilla_median`
- `ratio_vs_vanilla < 1.0` indicates lower median final objective for PhaseWall
- `improvement_factor = vanilla_median / phasewall_median`

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

## Limitations
- This repository does not currently include seed-level raw logs.
- This repository does not currently include a full from-scratch rerun pipeline.
- Claims are limited to report-derived outcomes under the listed settings.

## Out-of-Scope / Non-Canonical Data
- Additional stress runs not represented in the bundled report are excluded from DOI-facing claims.
- Production-readiness claims are out of scope for this evidence package.
