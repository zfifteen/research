# Peer Review Response: Review 001 (ChatGPT)

Date: 2026-03-03
Scope: Conservative DOI-go remediation without new reruns.

## Point-by-Point Traceability

### 1) Overclaiming vs available evidence (`docs/analysis/benchmarks.md`)
Status: Resolved

Changes:
- Rewrote benchmark note to a report-derived scope.
- Added explicit run manifest (functions, dimensions, seeds, budget, noise, metric, methods).
- Removed production/drop-in language and non-canonical extra-run claims.

Files:
- `docs/analysis/benchmarks.md`

### 2) Technical note structure and self-containment
Status: Resolved

Changes:
- Kept fully structured Markdown note.
- Added explicit baseline/variant definitions.
- Added Appendix A derivation showing curvature sign change at `r = sigma`.
- Removed required dependency on external `phasewall` repository references for canonical claims.

Files:
- `docs/technical-note/technical_note.md`

Note:
- Reviewer sub-point about "single-line formatting" was stale against current repository state; file already had structured Markdown before this pass.

### 3) Repro command was only existence check
Status: Resolved

Changes:
- Replaced QC mechanism with executable integrity checks:
  - hash verification (`scripts/verify_hashes.py`)
  - claim metric recomputation (`scripts/verify_report_claims.py`)
- Updated top-level QC command contract to `bash scripts/qc_check.sh`.

Files:
- `scripts/qc_check.sh`
- `scripts/verify_hashes.py`
- `scripts/verify_report_claims.py`
- `QC_CHECKLIST.md`

### 4) PDF-only evidence not machine-auditable
Status: Resolved

Changes:
- Added machine-auditable CSV artifacts derived from report table.
- Added provenance note for extraction method and scope.

Files:
- `artifacts/results/phasewall_report_table.csv`
- `artifacts/results/phasewall_vs_vanilla_claims.csv`
- `artifacts/results/README.md`

### 5) DOI metadata placeholders and release metadata gaps
Status: Resolved

Changes:
- Added `LICENSE` (MIT).
- Added `.zenodo.json`.
- Replaced DOI `TBD` placeholders with explicit pre-DOI wording.
- Kept release version aligned with `CITATION.cff`.

Files:
- `LICENSE`
- `.zenodo.json`
- `QC_CHECKLIST.md`
- `CITATION.cff` (retained, version-aligned)

### 6) README tone misaligned with exploratory framing
Status: Resolved

Changes:
- Rewrote README with conservative, artifact-backed framing.
- Removed broad production-level claims.
- Added explicit limitations and hypotheses/future-work split.

Files:
- `README.md`

## Additional Integrity Controls Added
- Hash manifest for canonical artifacts:
  - `artifacts/SHA256SUMS`
- Scripted verification path integrated into QC command.

## Deferred Items
- Full seed-level raw logs and complete rerun pipeline are deferred to a future release.
