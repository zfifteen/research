# Revised Hypothesis (Setup 1)

Date: 2026-03-03  
Scope: `gradient-z-classifier/setup_1` manufactured-solution harness (`test_gradients.py`) on current mesh families.

## 1. Revised Core Hypothesis

For the current mesh-generation process and manufactured field
`f(x,y) = sin(pi x) cos(pi y)`, performance is **not** governed by a sharp
`z`-phase transition where GLSQ dominates.

Instead:

1. **WLSQ is the accuracy-optimal baseline across the full tested z-distribution**  
   (controlled skewness meshes + optional mixed mesh).
2. **GLSQ behaves as a controllable interpolation between WLSQ and GG**  
   rather than a distinct superior regime.
3. **The scalar mean-z per mesh is not sufficient to predict a hybrid-only advantage window**  
   for this dataset.

## 2. Why This Should Work

This revised hypothesis matches what the harness already measured:

- WLSQ had the lowest L2 error on every controlled mesh.
- GLSQ at `alpha=0.5` consistently sat between WLSQ and GG.
- Peak hybrid advantage was ~2x, not 5-20x.
- Endpoint behavior was exact (`alpha=0 -> WLSQ`, `alpha=1 -> GG`).

So the updated claim is narrower, testable, and consistent with observed mechanics.

## 3. Falsifiable Predictions

The hypothesis is considered **validated** only if all predictions P1-P6 pass.

### P1: WLSQ Dominance (Controlled Family)

For each controlled mesh in `meshes_v3`,  
`L2(WLSQ) < L2(GLSQ alpha=0.5) < L2(GG)`.

### P2: WLSQ Dominance (Mixed Mesh, if provided)

When `--mixed-path` is used, mixed mesh also satisfies:
`L2(WLSQ) < L2(GLSQ alpha=0.5) < L2(GG)`.

### P3: No Strong Hybrid Window

Across controlled meshes, hybrid advantage
`A = max(L2(WLSQ), L2(GG)) / L2(GLSQ alpha=0.5)` is bounded:
`1.0 < A < 3.0`, and never reaches 5.0.

### P4: Mean-z Non-Predictiveness for Hybrid Peak

The maximum `A` does not reliably align with mean `z` in `[3,6]`.
Equivalent test: highest-advantage mesh has mean `z` outside `[3,6]`
or no statistically meaningful concentration in that band.

### P5: GLSQ Endpoint Identities

Per mesh:
- `L2(GLSQ alpha=0.0) == L2(WLSQ)` (within `1e-10` relative tolerance)
- `L2(GLSQ alpha=1.0) == L2(GG)` (within `1e-10` relative tolerance)
- Same checks for `|C|_max`.

### P6: Runtime Ordering

Per mesh, reconstruction time trend should hold:
`time(GG) <= time(WLSQ) <= time(GLSQ alpha=0.5)`  
with small tolerated inversions due to timing noise (<=10% relative).

## 4. Decision Rule

### Validate if:
- P1, P3, P5 pass on controlled meshes, and
- P2 passes when mixed mesh is included, and
- P4 shows no stable transition-window peak, and
- P6 holds on at least 80% of mesh cases.

### Falsify if any of these occur:
- GLSQ(alpha=0.5) beats WLSQ on a majority of controlled meshes.
- Hybrid advantage exceeds or repeatedly approaches 5x.
- Endpoint identities fail.

## 5. Practical Classifier Update (If Validated)

For Setup 1 workloads:

1. Use **WLSQ as default reconstruction**.
2. Use **GLSQ only as a tunable tradeoff knob** (not a primary winner claim).
3. Keep `z` for descriptive quality reporting and local diagnostics, not as a
   standalone predictor of a sharp hybrid-optimal phase window.

## 6. Minimal Verification Procedure

Run:

```bash
python3 gradient-z-classifier/setup_1/test_gradients.py
python3 gradient-z-classifier/setup_1/test_gradients.py \
  --mixed-path gradient-z-classifier/setup_1/meshes/mixed_production
```

Verify against:

- `results/*/raw/metrics_long.csv`
- `results/*/raw/summary_by_mesh.csv`
- `results/*/validation_report.md`

## 7. Statement to Use in Technical Notes

> In Setup 1, the data supports a WLSQ-dominant regime with GLSQ acting as a
> continuous blend control, and does not support a sharp 5-20x hybrid-advantage
> transition window based on mesh-mean z.
