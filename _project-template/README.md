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
2. Ensure `scripts/qc_check.sh` passes.
3. Create tag `vX.Y.Z`.
4. Publish release and mint DOI via Zenodo.
5. Backfill DOI lines in `QC_CHECKLIST.md` and `CITATION.cff`.
