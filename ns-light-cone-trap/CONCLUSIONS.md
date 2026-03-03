# Meta-Analysis of Executed Setups (1–3)

## Scope
This document synthesizes the completed executions in:
- `setup_1` (run: `results/20260303_143232`)
- `setup_2` (run: `results/20260303_151821`)
- `setup_3` (run: `results/20260303_153343`)

Date of synthesis: March 3, 2026.

---

## Setup-by-Setup Findings

| Setup | Core result | Quantitative highlights | Interpretation |
|---|---|---|---|
| Setup 1 | **Inconclusive** | Both configs marked `Inconclusive`; `24/24` rows were `no_identifiable_set`; accepted candidates `0` everywhere | Inversion stage never produced admissible backward candidates, so this run did not test asymmetry strength reliably. |
| Setup 2 | **Partial support** | `exp1` marked `Supported` across tested configs; `exp2` marked `Inconclusive` with `5 ok / 1 diverged` rows; `global_outcome = Supported` | Simplified diffusion mechanism strongly supports irreversible information loss; nonlinear NS test was directionally supportive but numerically unstable/incomplete. |
| Setup 3 | **Inconclusive overall; key high-Re prediction failed in this run** | Ratios by Re: `25.30` (100), `1.64` (500), `1.10` (2000), `0.94` (5000); non-monotonic; `ratio_at_re5000 < 1`; Test 2 loss rate `0.021` avg vs critical `1.448` (not crossed) | Strong asymmetry appears only at low Re in this execution. The specific predicted threshold behavior at high Re was not observed. |

---

## Cross-Experiment Synthesis

### 1) What is supported
- The **core mechanism** (“dissipation hurts backward reconstruction more than forward prediction”) is supported in simplified/strongly dissipative regimes:
  - Setup 2 Experiment 1 (diffusion) strongly.
  - Setup 3 at low Re (`Re=100`) strongly.

### 2) What is not supported (yet)
- The **specific quantitative claim** “at high Re (around 5000+) and target horizons, backward error should exceed forward by 3–5x” was **not reproduced** in executed Setup 3 (`Re=5000 ratio ≈ 0.94`).

### 3) Why evidence quality is mixed
- The three setups use materially different inverse formulations and numerical regimes:
  - Setup 1: ensemble acceptance-based inverse (collapsed to empty feasible set).
  - Setup 2: deterministic anti-diffusive backward integration with fallback-scale runs.
  - Setup 3: deterministic `odeint` setup; completed at `N=32` fallback for runtime.
- Because of these differences, results are consistent on mechanism-level direction, but not yet decision-grade for the high-Re threshold claim.

---

## Final Conclusion

### Hypothesis status (as executed)
- **Mechanistic claim:** **Partially validated** (dissipative irreversibility signal appears repeatedly).
- **High-Re quantitative threshold claim:** **Not validated** and **falsified in the executed Setup 3 run configuration**.
- **Global status across all three executed setups:** **Inconclusive / partial support**, not a full validation.

In short: the experiments support the existence of a light-cone-style reconstruction asymmetry, but the current executed runs do **not** establish the claimed high-Re threshold behavior.

---

## Evidence Anchors
- Setup 1 summary: `setup_1/results/20260303_143232/summary.json`
- Setup 1 metrics: `setup_1/results/20260303_143232/metrics.csv`
- Setup 2 summary: `setup_2/results/20260303_151821/summary.json`
- Setup 2 metrics: `setup_2/results/20260303_151821/metrics_exp1.csv`, `metrics_exp2.csv`
- Setup 3 summary: `setup_3/results/20260303_153343/summary.json`
- Setup 3 CSV: `setup_3/results/20260303_153343/reconstruction_test_results.csv`
