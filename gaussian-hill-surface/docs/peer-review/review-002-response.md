# Peer Review Response: Review 002 (Stale Snapshot Reconciliation)

Date: 2026-03-03
Branch: `doi-gaussian-hill-surface`
Scope: Reconcile reviewer findings against current branch state; keep conservative evidence model unchanged.

## Summary
Most reported P0 blockers were based on an older branch snapshot and are already resolved in the current branch.
The only active item is metadata URL immutability (`main` vs tagged snapshot), which is acknowledged and handled as a release-time gate.

## Point-by-Point Status

### 1) QC checklist format incompatible with `scripts/qc_check.sh`
Status: Resolved

Current state:
- `QC_CHECKLIST.md` contains exact required headings on standalone lines:
  - `## Claims`
  - `## Evidence Map`
  - `## Repro Command`
  - `## Environment`
  - `## Limitations`
  - `## Artifact Manifest`
  - `## DOI`
- Repro command line is exact: `Command: bash scripts/qc_check.sh`
- DOI section contains no `TBD`.

Files:
- `QC_CHECKLIST.md`
- `scripts/qc_check.sh`

### 2) `CITATION.cff` version not parseable by QC script
Status: Resolved

Current state:
- `CITATION.cff` is multiline CFF/YAML.
- `version: "0.1.0"` is line-starting and parse-compatible with the `awk` logic in `scripts/qc_check.sh`.
- Parsed version matches checklist release version (`v0.1.0` -> `0.1.0`).

Files:
- `CITATION.cff`
- `QC_CHECKLIST.md`
- `scripts/qc_check.sh`

### 3) Single-line Markdown/readability concern
Status: Resolved

Current state:
- `README.md`, `docs/analysis/benchmarks.md`, and `docs/technical-note/technical_note.md` are multiline and sectioned.
- `LICENSE` is multiline.

Files:
- `README.md`
- `docs/analysis/benchmarks.md`
- `docs/technical-note/technical_note.md`
- `LICENSE`

### 4) Metadata points to `main` instead of release snapshot
Status: Acknowledged (release-time gate)

Policy for this branch:
- Keep `main` URLs until `v0.1.0` tag exists.
- At release cut, switch to:
  - `https://github.com/zfifteen/research/tree/v0.1.0/gaussian-hill-surface`
- Rerun `bash scripts/qc_check.sh` after URL update.

Files:
- `CITATION.cff`
- `.zenodo.json`
- `docs/release-notes/v0.1.0-conservative-doi-draft.md`

## Validation Evidence (Current Branch)

### Command outputs
1. Repo root QC:

```text
$ bash scripts/qc_check.sh
[verify-hashes] PASS: validated 7 files
[verify-claims] PASS: validated 8 claim rows
[qc-lite] PASS: minimum rigor and reproducibility checks succeeded
```

2. Parent-directory path-robust QC:

```text
$ bash gaussian-hill-surface/scripts/qc_check.sh
[verify-hashes] PASS: validated 7 files
[verify-claims] PASS: validated 8 claim rows
[qc-lite] PASS: minimum rigor and reproducibility checks succeeded
```

### Parser compatibility checks
- Required checklist headings found at line starts in `QC_CHECKLIST.md`.
- Exact command line found: `Command: bash scripts/qc_check.sh`.
- `awk` extraction checks:
  - CITATION version: `0.1.0`
  - Checklist release version: `v0.1.0`

## Current State Table

| Check | Result | Evidence |
|---|---|---|
| Checklist required headings present | PASS | `QC_CHECKLIST.md` + heading regex checks |
| DOI section exists and has no `TBD` | PASS | `QC_CHECKLIST.md` |
| CFF parse-compatible for `version:` | PASS | `CITATION.cff` + `awk` extraction |
| Markdown docs multiline/sectioned | PASS | README + benchmarks + technical note line counts |
| QC gate executable | PASS | root and parent-directory runs |

## Notes for Reviewer Rerun
- Please re-run against the latest `doi-gaussian-hill-surface` head commit, not older branch snapshots.
- Canonical scope remains unchanged: report-derived audit package, no raw-log rerun claim.
