# QC Checklist (Solo Minimum Rigor)

## Claims
- Crossing the Gaussian phase wall (`r = σ`) separates convergent interior behavior from scattering-prone exterior behavior.
- A phase-aware rule can improve stability/sample efficiency under noisy conditions versus baseline dynamics.
- The reported benchmark and figure artifacts in this project are sufficient to audit these claims.

## Evidence Map
- Claim 1 -> `gaussian-hill-surface/docs/specs/PhaseWall_Tech_Spec_v2.1.md`
- Claim 2 -> `gaussian-hill-surface/docs/analysis/benchmarks.md`
- Claim 2 -> `gaussian-hill-surface/artifacts/reports/PhaseWall_Benchmark_Report.pdf`
- Claim 3 -> `gaussian-hill-surface/artifacts/figures/benchmarks/benchmark_bars.png`
- Claim 3 -> `gaussian-hill-surface/artifacts/figures/benchmarks/benchmark_ratios.png`

## Repro Command
Command: python3 -c "import pathlib; req=[pathlib.Path('gaussian-hill-surface/artifacts/reports/PhaseWall_Benchmark_Report.pdf'), pathlib.Path('gaussian-hill-surface/docs/analysis/benchmarks.md')]; assert all(p.exists() for p in req), 'Missing required reproducibility artifacts'; print('repro smoke pass')"

## Environment
- OS: macOS
- Python: 3.10+
- Notes: This checklist validates artifact integrity/repro traceability before DOI release.

## Limitations
- This QC pass validates existence/traceability and a reproducibility smoke command, not full statistical re-execution.
- Strong claims should still be interpreted with benchmark scope limits stated in benchmark docs.

## Artifact Manifest
- path: gaussian-hill-surface/artifacts/reports/PhaseWall_Benchmark_Report.pdf
- path: gaussian-hill-surface/artifacts/figures/concepts/img.png
- path: gaussian-hill-surface/artifacts/figures/concepts/img_1.png
- path: gaussian-hill-surface/artifacts/figures/benchmarks/benchmark_bars.png
- path: gaussian-hill-surface/artifacts/figures/benchmarks/benchmark_ratios.png
- path: gaussian-hill-surface/docs/analysis/benchmarks.md
- path: gaussian-hill-surface/docs/specs/PhaseWall_Tech_Spec_v2.1.md

## DOI
Release Version: v0.1.0
Version DOI: TBD
Concept DOI: TBD
