# Gaussian Hill Surface / PhaseWall

## Status
This repository is an exploratory, artifact-backed research package.

It is designed for conservative claim auditing, not for a full benchmark rerun from raw logs.

## Research Focus
This project studies a geometric boundary on the Gaussian hill surface and whether a phase-aware damping rule is associated with improved robustness under noisy optimization conditions in the bundled report artifacts.

Core geometry claim:
- For `z = exp(-r^2 / (2 sigma^2))`, Gaussian curvature changes sign exactly at `r = sigma`.
- A derivation is included in `docs/technical-note/technical_note.md` (Appendix A).

## Canonical Evidence Model
The canonical quantitative source is:
- `artifacts/reports/PhaseWall_Benchmark_Report.pdf` (v2.1, 2026-02-28)

Machine-auditable tables derived from that report:
- `artifacts/results/phasewall_report_table.csv`
- `artifacts/results/phasewall_vs_vanilla_claims.csv`

Integrity manifest:
- `artifacts/SHA256SUMS`

The DOI-facing narrative is in:
- `docs/technical-note/technical_note.md`
- `docs/analysis/benchmarks.md`

## Benchmark Snapshot (Vanilla vs PhaseWall)
Values below are from `artifacts/results/phasewall_vs_vanilla_claims.csv`.

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

Interpretation for minimization:
- `ratio_vs_vanilla < 1.0` indicates lower median final objective for PhaseWall.
- Outcomes are mixed across function families; no universal improvement claim is made.

## Reproducibility Command
Run:

```bash
bash scripts/qc_check.sh
```

This validates:
- required metadata/docs for this release package,
- SHA256 integrity for canonical artifacts,
- numerical consistency of derived claim metrics.

## Repository Layout
- `docs/technical-note/technical_note.md`: canonical technical note
- `docs/analysis/benchmarks.md`: benchmark scope and verified outcomes
- `QC_CHECKLIST.md`: release QC checklist and evidence map
- `artifacts/reports/`: bundled report artifact
- `artifacts/results/`: machine-auditable benchmark tables
- `scripts/`: QC and verification scripts

## Limitations
- Seed-level raw logs are not bundled in this release.
- No full rerun pipeline is included yet.
- Claims are constrained to report-derived evidence under the documented setup.

## Hypotheses / Future Work
- Publish seed-level raw logs and a full rerun pipeline.
- Add paired statistical scripts over raw trials.
- Expand evaluation across additional optimizers and noise regimes.
