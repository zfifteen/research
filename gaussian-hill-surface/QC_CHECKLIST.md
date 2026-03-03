# QC Checklist (Conservative DOI Readiness)

## Claims
- The Gaussian hill surface has a curvature sign transition at `r = sigma` (derivation in technical note Appendix A).
- Under the bundled report conditions, PhaseWall is associated with lower median final objective than vanilla on some settings and higher on others.
- Canonical quantitative claims in this package are auditable from report-derived CSV artifacts plus hash verification.

## Evidence Map
- Geometry claim -> `docs/technical-note/technical_note.md` (Appendix A)
- Benchmark protocol + interpretation -> `docs/analysis/benchmarks.md`
- Full report-derived table -> `artifacts/results/phasewall_report_table.csv`
- Canonical Vanilla vs PhaseWall claim table -> `artifacts/results/phasewall_vs_vanilla_claims.csv`
- Source report -> `artifacts/reports/PhaseWall_Benchmark_Report.pdf`
- Artifact integrity manifest -> `artifacts/SHA256SUMS`

## Repro Command
Command: bash scripts/qc_check.sh

## Environment
- OS: macOS
- Python: 3.10+
- Shell: bash/zsh
- Notes: QC validates package integrity and claim consistency; it does not regenerate experiments.

## Limitations
- Seed-level raw trial logs are not bundled in this release.
- No from-scratch rerun pipeline is included.
- Report-derived CSVs support claim auditing but are not a replacement for raw-run replay.

## Artifact Manifest
- path: artifacts/reports/PhaseWall_Benchmark_Report.pdf
- path: artifacts/figures/benchmarks/benchmark_bars.png
- path: artifacts/figures/benchmarks/benchmark_ratios.png
- path: artifacts/results/phasewall_report_table.csv
- path: artifacts/results/phasewall_vs_vanilla_claims.csv
- path: artifacts/SHA256SUMS
- path: docs/analysis/benchmarks.md
- path: docs/technical-note/technical_note.md

## DOI
Release Version: v0.1.0
Version DOI: Pre-DOI draft; DOI will be minted at release publication.
Concept DOI: Pre-DOI draft; DOI will be minted at release publication.
