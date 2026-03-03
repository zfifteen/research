# Validation Report

- Run directory: `/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_02`
- Hypothesis status: **FALSIFIED**

## Controlled Skewness Family

| θ_skew target | z-range (mean) | Pure LSQ error | Pure GG error | GLSQ (α=0.5) error | Hybrid advantage |
|---|---|---:|---:|---:|---:|
| 10° | 1.89-170.35 (6.31) | 4.314e-02 | 8.835e-01 | N/A | N/A |
| 30° | 1.93-340.00 (7.66) | 3.893e-01 | 2.154e+00 | N/A | N/A |
| 50° | 1.98-340.00 (13.97) | 2.672e-01 | 3.780e+00 | N/A | N/A |
| 60° | 1.93-340.00 (15.59) | 2.933e-01 | 3.576e+00 | N/A | N/A |
| 70° | 1.98-340.00 (17.32) | 3.410e-01 | 3.555e+00 | N/A | N/A |
| 80° | 1.90-340.00 (15.13) | 4.626e-01 | 5.234e+00 | N/A | N/A |

## Regime Statistics per Mesh

| Mesh | Mean z | High-z (%) | Transition (%) | Low-z (%) |
|---|---:|---:|---:|---:|
| skew_10deg | 6.31 | 38.7 | 59.9 | 1.4 |
| skew_30deg | 7.66 | 43.1 | 50.9 | 6.0 |
| skew_50deg | 13.97 | 52.5 | 40.5 | 7.0 |
| skew_60deg | 15.59 | 52.9 | 36.4 | 10.6 |
| skew_70deg | 17.32 | 56.4 | 37.8 | 5.9 |
| skew_80deg | 15.13 | 54.2 | 38.7 | 7.1 |

## Falsification Assessment

- Phase-transition hypothesis falsified because GLSQ (α=0.5) hybrid-advantage data is unavailable in this run.

## Output File Paths

- Raw long metrics: `/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_02/raw/metrics_long.csv`
- Summary table: `/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_02/raw/summary_by_mesh.csv`
- Plot: `/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_02/plots/error_vs_theta.png`
- Plot: `/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_02/plots/hybrid_advantage_vs_z.png`
- Plot: `/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_02/plots/representative_mesh_z_and_error.png`
- Plot: `/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_02/plots/regime_histogram_summary.png`
