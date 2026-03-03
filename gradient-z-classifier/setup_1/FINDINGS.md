# Gradient Reconstruction Harness Findings

Date: 2026-03-03  
Scope: Implementation and validation results for [test_gradients.py](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/test_gradients.py) in Setup 1.

## 1. Deliverable Status

Implemented artifact:
- [test_gradients.py](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/test_gradients.py)

Implemented required functions:
- `load_mesh(folder)`
- `green_gauss_grad(...)`
- `wlsq_grad(...)`
- `glsq_hybrid_grad(...)`
- `manufactured_solution_test(mesh_folder, scheme, alpha=0.5)`
- `run_full_validation()`

Implemented CLI:
- `--mesh-dir` (default: `setup_1/meshes_v3`)
- `--output-dir` (default: `setup_1/results`)
- `--schemes` (default: `gg,wlsq,glsq`)
- `--mixed-path` (optional mixed production mesh)

## 2. Execution Matrix

| Run ID | Command Intent | Controlled Meshes | Mixed Mesh | Result |
|---|---|---:|---:|---|
| `2026-03-03_run` | Default smoke run | 6 | 0 | Success |
| `2026-03-03_run_01` | Mixed-path validation | 6 | 1 | Success |
| `2026-03-03_run_02` | Scheme filter (`gg,wlsq`) | 6 | 0 | Success |
| `2026-03-03_run_03` | VTK-only loader fallback | 1 | 0 | Success |

Startup confirmations:
- Default run printed: `Found 6 controlled skewness meshes + 0 mixed.`
- Mixed run printed: `Found 6 controlled skewness meshes + 1 mixed.`

## 3. Primary Controlled-Family Results

Source artifact:
- [2026-03-03_run/validation_report.md](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run/validation_report.md)
- [2026-03-03_run/raw/summary_by_mesh.csv](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run/raw/summary_by_mesh.csv)

Reproduced measured comparison table:

| θ_skew target | z-range (mean) | Pure LSQ error | Pure GG error | GLSQ (α=0.5) error | Hybrid advantage |
|---|---|---:|---:|---:|---:|
| 10° | 1.89-170.35 (6.31) | 4.314e-02 | 8.835e-01 | 4.420e-01 | 1.999x |
| 30° | 1.93-340.00 (7.66) | 3.893e-01 | 2.154e+00 | 1.114e+00 | 1.933x |
| 50° | 1.98-340.00 (13.97) | 2.672e-01 | 3.780e+00 | 1.898e+00 | 1.991x |
| 60° | 1.93-340.00 (15.59) | 2.933e-01 | 3.576e+00 | 1.800e+00 | 1.987x |
| 70° | 1.98-340.00 (17.32) | 3.410e-01 | 3.555e+00 | 1.794e+00 | 1.982x |
| 80° | 1.90-340.00 (15.13) | 4.626e-01 | 5.234e+00 | 2.636e+00 | 1.985x |

Key observations:
- In all 6 controlled meshes, `WLSQ` achieved the lowest L2 error.
- `GLSQ(α=0.5)` consistently outperformed `GG`, but did not beat `WLSQ`.
- Hybrid advantage `max(pure)/GLSQ` stayed near ~2x, not 5–20x.

## 4. Hypothesis Assessment

Deterministic criterion implemented:
- Confirm only if peak hybrid advantage occurs in mean `z ∈ [3,6]` and peak ratio `>= 5`.

Measured outcome:
- Peak hybrid advantage: `2.00x` at mean `z = 6.31`.
- Status: **FALSIFIED**.

Source:
- [2026-03-03_run/validation_report.md](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run/validation_report.md)

## 5. Monotonicity Violation (`|C|_max`) Findings

Source:
- [2026-03-03_run/raw/metrics_long.csv](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run/raw/metrics_long.csv)

Summary over 6 controlled meshes:

| Scheme view | `|C|_max` min | `|C|_max` max | Mean |
|---|---:|---:|---:|
| Pure GG | 184.741 | 255,938.723 | 128,974.853 |
| Pure WLSQ | 26.731 | 791.531 | 343.964 |
| GLSQ (α=0.5) | 92.650 | 127,970.442 | 64,487.768 |

Interpretation:
- Monotonicity overshoot in this setup is largest for GG, smallest for WLSQ.
- GLSQ(α=0.5) is intermediate, matching convex-blend expectations.

## 6. Timing and Throughput Findings

Timing metric definition:
- Per reconstruction call over full field, recorded as `time_ms` and `throughput_cells_per_s`.

Sources:
- [2026-03-03_run/raw/metrics_long.csv](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run/raw/metrics_long.csv)
- [2026-03-03_run_01/raw/metrics_long.csv](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_01/raw/metrics_long.csv)

Controlled-family timing summary (6 meshes):

| Scheme view | time min (ms) | time max (ms) | time mean (ms) | Throughput mean (cells/s) |
|---|---:|---:|---:|---:|
| Pure GG | 0.368 | 1.561 | 0.887 | 11.11M |
| Pure WLSQ | 0.534 | 2.651 | 1.205 | 8.64M |
| GLSQ (α=0.5) | 0.687 | 3.423 | 1.828 | 5.45M |

Full reconstruction-time totals from CSV:
- Default run (`6 × (GG + WLSQ + GLSQ α={0,0.5,1})`): `0.04545 s`
- Mixed run (adds mixed mesh set): `0.06949 s`
- Scheme-filter run (`gg,wlsq` only): `0.01547 s`
- VTK-only single mesh run: `0.00772 s`

Note:
- End-to-end wall time is larger than these totals because plotting/report I/O dominates runtime.

## 7. Additional Scenario Results

### 7.1 Mixed Production Mesh (`--mixed-path`)

Source:
- [2026-03-03_run_01/validation_report.md](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_01/validation_report.md)
- [2026-03-03_run_01/raw/metrics_long.csv](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_01/raw/metrics_long.csv)

Measured mixed mesh regime:
- Mean `z = 2.15`
- High-z: `0.1%`
- Transition: `2.1%`
- Low-z: `97.8%`

Measured mixed mesh errors:
- GG: `1.666e+00`
- WLSQ: `1.050e-01`
- GLSQ(α=0.5): `8.359e-01`

### 7.2 Scheme Filter (`--schemes gg,wlsq`)

Source:
- [2026-03-03_run_02/validation_report.md](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_02/validation_report.md)

Observed behavior:
- Report table shows `GLSQ (α=0.5) error = N/A`.
- Hybrid advantage also `N/A`.
- Run completes without failure and keeps required outputs.

### 7.3 VTK-only Loader Fallback

Source:
- [2026-03-03_run_03/validation_report.md](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_03/validation_report.md)
- [2026-03-03_run_03/raw/metrics_long.csv](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_03/raw/metrics_long.csv)

Setup:
- Used a temporary directory containing only `mesh.vtk` for `skew_50deg` (no `.npy` files).

Outcome:
- Loader fallback succeeded.
- Relative L2 difference vs `.npy`-backed run for same mesh:
  - WLSQ: `2.77e-06`
  - GG: `5.61e-06`
  - GLSQ(α=0.5): `5.58e-06`

### 7.4 GLSQ Endpoint Sanity

Source:
- [2026-03-03_run_03/raw/metrics_long.csv](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_03/raw/metrics_long.csv)

Verified identities:
- `GLSQ(α=0.0)` equals `WLSQ` exactly in reported `L2` and `|C|_max`.
- `GLSQ(α=1.0)` equals `GG` exactly in reported `L2` and `|C|_max`.

Absolute differences:
- `|L2(α=0)-L2(WLSQ)| = 0.0`
- `|L2(α=1)-L2(GG)| = 0.0`
- `||C|_max(α=0)-|C|_max(WLSQ)| = 0.0`
- `||C|_max(α=1)-|C|_max(GG)| = 0.0`

## 8. Plot Artifacts

Default run plots:
- [error_vs_theta.png](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run/plots/error_vs_theta.png)
- [hybrid_advantage_vs_z.png](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run/plots/hybrid_advantage_vs_z.png)
- [representative_mesh_z_and_error.png](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run/plots/representative_mesh_z_and_error.png)
- [regime_histogram_summary.png](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run/plots/regime_histogram_summary.png)

Equivalent plot sets also exist for:
- [2026-03-03_run_01/plots](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_01/plots)
- [2026-03-03_run_02/plots](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_02/plots)
- [2026-03-03_run_03/plots](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_03/plots)

## 9. Task-Criteria Traceability

| Task requirement | Status | Evidence artifact |
|---|---|---|
| Load all controlled meshes in `meshes_v3` | Pass | [2026-03-03_run/validation_report.md](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run/validation_report.md) |
| Optional mixed mesh support | Pass | [2026-03-03_run_01/validation_report.md](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_01/validation_report.md) |
| Implement GG, WLSQ, GLSQ(α) | Pass | [test_gradients.py](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/test_gradients.py) |
| Manufactured field and analytic gradient | Pass | [test_gradients.py](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/test_gradients.py) |
| Compute L2, `|C|_max`, timing | Pass | [2026-03-03_run/raw/metrics_long.csv](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run/raw/metrics_long.csv) |
| Exact comparison table header in markdown report | Pass | [2026-03-03_run/validation_report.md](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run/validation_report.md) |
| Publication-ready plot outputs | Pass | [2026-03-03_run/plots](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run/plots) |
| Include confirmed/falsified statement | Pass | [2026-03-03_run/validation_report.md](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run/validation_report.md) |
| Runtime target (<2 minutes) | Pass | Observed completion in seconds; reconstruction totals from CSV are <0.1 s per run set |

## 10. Artifact Index

Primary implementation:
- [test_gradients.py](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/test_gradients.py)

Primary run:
- [validation_report.md](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run/validation_report.md)
- [metrics_long.csv](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run/raw/metrics_long.csv)
- [summary_by_mesh.csv](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run/raw/summary_by_mesh.csv)

Mixed-path validation run:
- [validation_report.md](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_01/validation_report.md)
- [metrics_long.csv](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_01/raw/metrics_long.csv)

Scheme-filter validation run:
- [validation_report.md](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_02/validation_report.md)
- [metrics_long.csv](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_02/raw/metrics_long.csv)

VTK-only fallback run:
- [validation_report.md](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_03/validation_report.md)
- [metrics_long.csv](/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_03/raw/metrics_long.csv)
