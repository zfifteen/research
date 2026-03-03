# Results Artifacts

This directory provides machine-auditable benchmark tables used by the DOI-facing documentation.

## Provenance
- Source report: `artifacts/reports/PhaseWall_Benchmark_Report.pdf`
- Source report version/date: v2.1 (2026-02-28)
- Extraction date: 2026-03-03
- Extraction method: manual transcription from the bundled PDF table into CSV

## Files
- `phasewall_report_table.csv`: full reported benchmark table (all methods in the source report).
- `phasewall_vs_vanilla_claims.csv`: derived Vanilla vs PhaseWall claim table used for canonical narrative metrics.

## Scope Note
This release does not include seed-level raw logs or a from-scratch rerun pipeline. The CSV files are report-derived audit artifacts, not regenerated experiment outputs.
