# TASK: Implement and Validate the Revised Hypothesis Harness (setup_3)

## Context

`setup_3` is a parallel experiment track to re-test gradient scheme selection with revised criteria derived from setup_1 evidence.

The revised claim is not a sharp 5-20x hybrid peak. Instead, for the current manufactured-solution workflow:

1. WLSQ is expected to be the default accuracy winner.
2. GLSQ(alpha) is expected to behave as a smooth blend control between WLSQ and GG.
3. Mesh-mean z is descriptive, not a sole predictor of a sharp hybrid-optimal window.

## Required Deliverables

1. `test_gradients.py` in `setup_3/` with same computation pipeline as setup_1.
2. Dated output folder under `setup_3/results/YYYY-MM-DD_run/`.
3. `validation_report.md` including revised hypothesis assessment (P1-P6).
4. CSVs and plots matching setup_1 artifact pattern.

## Functional Requirements

### Schemes

Implement exactly three core methods:

- Pure Green-Gauss (GG)
- Pure Weighted Least Squares (WLSQ, inverse-distance)
- GLSQ hybrid with alpha in `{0.0, 0.5, 1.0}`

### Manufactured Solution

- Field: `f(x,y) = sin(pi x) cos(pi y)`
- Compute exact analytic gradient.
- Reconstruct at cell centers.

### Metrics

- Volume-weighted L2 gradient error.
- Max monotonicity violation `|C|_max` using normalized overshoot.
- Runtime and throughput.

### Revised Hypothesis Checks

Evaluate and report:

- P1: Controlled-mesh ordering `WLSQ < GLSQ(0.5) < GG`.
- P2: Same ordering on optional mixed mesh.
- P3: Bounded hybrid advantage (`1 < A < 3`, no near-5 behavior).
- P4: No robust mesh-mean-z transition-window peak rule.
- P5: Endpoint identities (`GLSQ(0.0)==WLSQ`, `GLSQ(1.0)==GG`) for L2 and `|C|_max`.
- P6: Runtime ordering (tolerant to small timing noise).

### CLI Compatibility

Keep CLI surface consistent:

- `--mesh-dir`
- `--output-dir`
- `--schemes gg,wlsq,glsq`
- `--mixed-path`

## Success Criteria

1. Script runs end-to-end with setup_3 defaults when meshes exist locally.
2. Script runs with `--mesh-dir ../setup_1/meshes_v3` without code changes.
3. Report includes revised-hypothesis checklist and explicit overall status:
   - `VALIDATED`, `FALSIFIED`, or `INCONCLUSIVE`.
4. Output artifacts follow setup_1 shape for easy comparison.
