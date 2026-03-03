# Revised Hypothesis (Setup 3)

Date: 2026-03-03  
Scope: `gradient-z-classifier/setup_3` manufactured-solution harness (`test_gradients.py`).

## 1. Revised Core Hypothesis

For the current mesh-generation process and manufactured field
`f(x,y) = sin(pi x) cos(pi y)`, behavior is not governed by a sharp
hybrid-dominant phase transition.

Instead:

1. **WLSQ is the accuracy-optimal baseline** across the tested z-distribution.
2. **GLSQ acts as a controllable interpolation** between WLSQ and GG.
3. **Mesh-mean z is not sufficient** to predict a sharp hybrid-only advantage window.

## 2. Why This Is the Working Hypothesis

Setup_1 evidence showed:

- WLSQ best L2 performance on all controlled meshes.
- GLSQ(alpha=0.5) between WLSQ and GG.
- Hybrid advantage around ~2x, not 5-20x.
- Exact endpoint behavior at alpha 0 and 1.

## 3. Falsifiable Predictions

### P1: Controlled dominance

For each controlled mesh:
`L2(WLSQ) < L2(GLSQ alpha=0.5) < L2(GG)`.

### P2: Mixed dominance (if mixed mesh included)

For mixed mesh:
`L2(WLSQ) < L2(GLSQ alpha=0.5) < L2(GG)`.

### P3: Bounded hybrid advantage

`A = max(L2(WLSQ), L2(GG)) / L2(GLSQ alpha=0.5)` remains in a bounded low range
(target `1 < A < 3`) and does not approach 5.

### P4: No robust mean-z transition-window rule

Maximum `A` does not consistently align with mean `z` in `[3,6]`.

### P5: Endpoint identities

Per mesh and for both L2 and `|C|_max`:

- `GLSQ(alpha=0.0) == WLSQ`
- `GLSQ(alpha=1.0) == GG`

(with strict numerical tolerance)

### P6: Runtime ordering trend

Per mesh:
`time(GG) <= time(WLSQ) <= time(GLSQ alpha=0.5)`
with small inversion allowance for timing noise.

## 4. Decision Rule

### Validate when:

- P1, P3, P5 pass on controlled meshes,
- P2 passes when mixed is included,
- P4 supports non-peak interpretation,
- P6 passes on most meshes.

### Falsify when:

- GLSQ(alpha=0.5) outperforms WLSQ broadly,
- Hybrid advantage shows strong old-style peak behavior,
- Endpoint identities fail.

### Inconclusive when:

- Required GLSQ-dependent data is absent.

## 5. Minimal Verification Commands

```bash
python3 gradient-z-classifier/setup_3/test_gradients.py \
  --mesh-dir gradient-z-classifier/setup_1/meshes_v3

python3 gradient-z-classifier/setup_3/test_gradients.py \
  --mesh-dir gradient-z-classifier/setup_1/meshes_v3 \
  --mixed-path gradient-z-classifier/setup_1/meshes/mixed_production
```

Check:

- `setup_3/results/*/raw/metrics_long.csv`
- `setup_3/results/*/raw/summary_by_mesh.csv`
- `setup_3/results/*/validation_report.md`
