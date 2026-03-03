# Experiment Setup 3: Revised-Hypothesis Validation Protocol

**Project:** gradient-z-classifier  
**Version:** 1.0  
**Date:** March 3, 2026

---

## Purpose

This protocol defines the revised experiment track after setup_1 evidence did not validate the prior sharp hybrid-window claim.

The objective is to test an evidence-calibrated model where:

1. WLSQ is the default accuracy-optimal baseline.
2. GLSQ is a controlled blend between WLSQ and GG.
3. Mesh-mean z is treated as descriptive, not a sole predictor of sharp hybrid dominance.

---

## 1. Software and Environment

- Python 3.11+
- NumPy
- SciPy
- Matplotlib
- Optional `vtk` Python module (not required if ASCII VTK fallback is used)

Reproducibility:

- Use fixed seed (`np.random.seed(42)` where randomness is involved).
- Archive run outputs under dated folders.

---

## 2. Input Meshes

### Preferred local path

- `setup_3/meshes_v3/`

### Compatibility path

- `setup_1/meshes_v3/` via `--mesh-dir`.

### Optional mixed mesh

- Provide `--mixed-path` to include a production-like mixed case.

---

## 3. Methods Under Test

Exactly three methods:

1. GG (volume-weighted Green-Gauss)
2. WLSQ (inverse-distance weighted least squares)
3. GLSQ(alpha) with alpha in `{0.0, 0.5, 1.0}`

Manufactured field:

- `f(x,y) = sin(pi x) cos(pi y)`

Metrics:

- L2 gradient error (area/volume weighted)
- `|C|_max` normalized monotonicity overshoot
- reconstruction runtime and throughput

---

## 4. Revised Predictions (P1-P6)

- **P1:** For each controlled mesh, `L2(WLSQ) < L2(GLSQ 0.5) < L2(GG)`.
- **P2:** Same ordering for optional mixed mesh.
- **P3:** Hybrid advantage remains bounded (`1 < A < 3`), no strong 5x-style peak.
- **P4:** Maximum advantage does not robustly align with mean `z` in `[3,6]`.
- **P5:** Endpoint identities hold for L2 and `|C|_max`.
- **P6:** Runtime ordering trend holds with small tolerance for timing noise.

---

## 5. Validation and Disconfirmation Rules

### Validate revised hypothesis when:

- P1, P3, P5 pass on controlled set,
- P2 passes when mixed mesh is included,
- P4 indicates no stable transition-window peak rule,
- P6 passes on most meshes (target >=80%).

### Falsify revised hypothesis when any of the following occur:

- GLSQ(0.5) beats WLSQ across a majority of controlled meshes.
- Hybrid advantage frequently approaches/exceeds the old strong-peak behavior.
- Endpoint identities fail.

### Inconclusive condition:

- Required GLSQ-dependent metrics are unavailable (for example scheme-filter runs without GLSQ).

---

## 6. Run Matrix

Minimum matrix:

1. Controlled meshes only (all schemes).
2. Controlled + mixed mesh (all schemes).
3. Controlled with scheme filter (`gg,wlsq`) to verify graceful incomplete analysis handling.
4. Optional VTK-only fallback test.

---

## 7. Output Artifacts

For each run:

- `results/YYYY-MM-DD_run/validation_report.md`
- `results/YYYY-MM-DD_run/raw/metrics_long.csv`
- `results/YYYY-MM-DD_run/raw/summary_by_mesh.csv`
- `results/YYYY-MM-DD_run/plots/error_vs_theta.png`
- `results/YYYY-MM-DD_run/plots/hybrid_advantage_vs_z.png`
- `results/YYYY-MM-DD_run/plots/representative_mesh_z_and_error.png`
- `results/YYYY-MM-DD_run/plots/regime_histogram_summary.png`

---

## 8. Reporting Expectations

`validation_report.md` must include:

1. Controlled-family comparison table.
2. Regime statistics per mesh.
3. Revised-hypothesis checklist (P1-P6) with pass/fail/not-evaluable per item.
4. Explicit overall result: `VALIDATED`, `FALSIFIED`, or `INCONCLUSIVE`.
5. Full artifact paths.
