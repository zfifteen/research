# Technical Note 3: Revised Regime Model for Gradient Reconstruction on Unstructured Grids

**From Sharp Hybrid-Window Theory to WLSQ-Dominant, Evidence-Calibrated Selection**

*Big D'*  
*March 3, 2026*

---

## Abstract

Technical Note 2 proposed a sharp phase-transition hypothesis: a narrow `3 < z < 6` band where GLSQ hybrids should outperform pure methods by `5-20x`. Setup 1 results did not validate that claim for the current mesh family and manufactured-solution protocol. The observed behavior was consistent and different: WLSQ was best on all controlled meshes, GLSQ (alpha=0.5) remained between WLSQ and GG, and hybrid advantage stayed near `~2x` rather than `5-20x`.

This note introduces a revised, falsifiable framework for this project line. The updated model treats WLSQ as the default accuracy baseline, GLSQ as a controllable blend between WLSQ and GG, and mesh-mean `z` as descriptive rather than a standalone predictor of a sharp hybrid-optimal window. The revised framework is codified in setup_3 as a parallel experiment track with explicit P1-P6 criteria and deterministic validation/falsification logic.

---

## 1. Problem Reframing

### 1.1 What changed

The prior claim in Technical Note 2 depended on three strong expectations:

1. Hybrid advantage peaks sharply and strongly (`5-20x`).
2. The peak occurs in a mesh-mean transition window (`3 < z < 6`).
3. That behavior is robust enough to drive scheme preselection.

Setup 1 data did not support these assumptions under the current mesh generation and 2D manufactured field.

### 1.2 Key methodological distinction

This revision separates:

- **Mesh-mean z interpretation**: global descriptor, useful for summarization.
- **Local-regime behavior**: cellwise mechanism where reconstruction quality is actually realized.

The prior setup used mesh-level summaries in a way that may obscure local behavior. The revised claim avoids overinterpreting mesh-mean `z` as a direct trigger for a hybrid-only winner regime.

---

## 2. Evidence Summary from Setup 1

Primary evidence artifacts:

- `setup_1/FINDINGS.md`
- `setup_1/results/2026-03-03_run/validation_report.md`
- `setup_1/results/2026-03-03_run/raw/metrics_long.csv`
- `setup_1/results/2026-03-03_run/raw/summary_by_mesh.csv`

### 2.1 Controlled-family measured results

| theta_skew target | z-range (mean) | Pure LSQ error | Pure GG error | GLSQ (alpha=0.5) error | Hybrid advantage |
|---|---|---:|---:|---:|---:|
| 10 deg | 1.89-170.35 (6.31) | 4.314e-02 | 8.835e-01 | 4.420e-01 | 1.999x |
| 30 deg | 1.93-340.00 (7.66) | 3.893e-01 | 2.154e+00 | 1.114e+00 | 1.933x |
| 50 deg | 1.98-340.00 (13.97) | 2.672e-01 | 3.780e+00 | 1.898e+00 | 1.991x |
| 60 deg | 1.93-340.00 (15.59) | 2.933e-01 | 3.576e+00 | 1.800e+00 | 1.987x |
| 70 deg | 1.98-340.00 (17.32) | 3.410e-01 | 3.555e+00 | 1.794e+00 | 1.982x |
| 80 deg | 1.90-340.00 (15.13) | 4.626e-01 | 5.234e+00 | 2.636e+00 | 1.985x |

### 2.2 Observed pattern

1. WLSQ had the lowest L2 error on every controlled mesh.
2. GLSQ(alpha=0.5) consistently improved over GG but did not outperform WLSQ.
3. Hybrid advantage was bounded near `~2x`.
4. The measured peak did not satisfy the previous confirmation rule.

### 2.3 Immediate implication

For this dataset and harness, the previous sharp phase-transition claim is overfit relative to evidence. A revised, narrower, test-first hypothesis is required.

---

## 3. Revised Hypothesis (Setup 3 Canonical)

The revised hypothesis for this project line is:

1. **WLSQ is the accuracy-optimal baseline** across the tested skewness family.
2. **GLSQ acts as a controllable interpolation** between WLSQ and GG, not a distinct winner regime under current conditions.
3. **Mesh-mean z is insufficient** as a sole predictor of a sharp hybrid-optimal window.

### 3.1 Falsifiable predictions (P1-P6)

- **P1 (Controlled dominance):** For each controlled mesh, `L2(WLSQ) < L2(GLSQ alpha=0.5) < L2(GG)`.
- **P2 (Mixed dominance, optional):** Same ordering for mixed mesh when provided.
- **P3 (Bounded hybrid advantage):** `1 < A < 3` where `A = max(pure)/GLSQ(alpha=0.5)`, and `A` never approaches 5.
- **P4 (No robust mean-z peak rule):** Maximum `A` does not reliably concentrate in mesh-mean `3 <= z <= 6`.
- **P5 (Endpoint identities):** `GLSQ(0.0)` equals WLSQ and `GLSQ(1.0)` equals GG (within strict tolerance) for both L2 and `|C|_max`.
- **P6 (Runtime ordering, tolerant):** `time(GG) <= time(WLSQ) <= time(GLSQ alpha=0.5)` with small inversion allowance due to timing noise.

### 3.2 Decision rule

- **Validated** when required criteria pass across controlled meshes and optional mixed checks.
- **Falsified** when ordering breaks broadly, hybrid advantage exceeds revised bounds, or endpoint identities fail.
- **Inconclusive** when required data for GLSQ-dependent checks is absent (for example `--schemes gg,wlsq`).

---

## 4. Revised Classifier Policy

For the present workflow:

1. Use **WLSQ as default** gradient reconstruction choice.
2. Use **GLSQ as a tuning knob** when robustness/behavior tradeoffs are needed.
3. Use `z` as a **diagnostic descriptor** and local-analysis feature, not as a sole global trigger for expecting a strong hybrid-only winner window.

This policy remains falsifiable and can be replaced if setup_3 evidence contradicts it.

---

## 5. Setup 3 Protocol Overview

Parallel revised track is defined in:

- `setup_3/TASK.md`
- `setup_3/experiment_setup_3.md`
- `setup_3/HYPOTHESIS_REVISED.md`
- `setup_3/test_gradients.py`

### 5.1 Scope of setup_3

- Keep reconstruction math unchanged (GG, WLSQ, GLSQ).
- Keep same core manufactured field and metric collection.
- Replace success/failure semantics with revised P1-P6 checks.
- Maintain comparable outputs (`results/YYYY-MM-DD_run/`, CSVs, plots, markdown report).

### 5.2 Required reruns

Minimum rerun matrix:

1. Controlled set run.
2. Controlled + mixed optional run.
3. Scheme-filter run (`gg,wlsq`) to verify graceful incompleteness handling.
4. Optional VTK-only fallback run for parser stability.

---

## 6. Limitations and Next Validation Steps

### 6.1 Current limitations

1. Manufactured field remains smooth and may favor WLSQ.
2. Current inference is primarily mesh-level; local transition-cell analysis is not yet first-class.
3. Mesh families are synthetic and may not span all production grid pathologies.

### 6.2 Next steps

1. Add local-regime diagnostics (cellwise or zonewise error stratification by z).
2. Add one harsher manufactured field (steeper or multiscale gradients).
3. Re-test revised hypothesis against extended mesh families and compare stability of P1-P6 outcomes.

---

## 7. References

1. Barth, T. J., and Jespersen, D. C., AIAA Paper 89-0366, 1989.
2. Mavriplis, D. J., AIAA Paper 2003-3986, 2003.
3. Shima, E., Kitamura, K., and Haga, T., AIAA Journal, 51(11), 2740-2747, 2013.
4. Nishikawa, H., Journal of Computational Physics, 372, 126-160, 2018.
5. Diskin, B., and Thomas, J. L., AIAA Journal, 49(4), 836-854, 2011.

Project artifacts:

- `setup_1/HYPOTHESIS_REVISED.md`
- `setup_1/FINDINGS.md`
- `setup_1/results/2026-03-03_run/validation_report.md`
- `setup_1/results/2026-03-03_run/raw/metrics_long.csv`
