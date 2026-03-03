# Project Title (Template)

Short description of the research question and why it matters.

## Scope
- What this project is testing.
- What this project is not claiming.

## Core Claims (Draft)
- Claim 1
- Claim 2
- Claim 3 (optional)

## Evidence Overview
- `docs/technical-note/technical_note.md`: primary publication document
- `docs/analysis/results.md` (or equivalent): summary metrics
- `artifacts/`: generated figures/reports used for publication package
- `docs/specs/`: method/assumption details

## Reproducibility
Run:

```bash
scripts/qc_check.sh
```

## Release / DOI
1. Complete `QC_CHECKLIST.md`.
2. Finalize `docs/technical-note/technical_note.md`.
3. Ensure `scripts/qc_check.sh` passes.
4. Create tag `vX.Y.Z`.
5. Publish release and mint DOI via Zenodo.
6. Backfill DOI lines in `QC_CHECKLIST.md` and `CITATION.cff`.
