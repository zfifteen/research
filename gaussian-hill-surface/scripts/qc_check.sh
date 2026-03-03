#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-gaussian-hill-surface}"
CHECKLIST="$PROJECT_DIR/QC_CHECKLIST.md"
CITATION="$PROJECT_DIR/CITATION.cff"
README_FILE="$PROJECT_DIR/README.md"

fail() {
  echo "[qc-lite] FAIL: $1" >&2
  exit 1
}

require_file() {
  local path="$1"
  [[ -f "$path" ]] || fail "Missing required file: $path"
}

require_heading() {
  local heading="$1"
  grep -q "^## ${heading}$" "$CHECKLIST" || fail "Missing checklist section: ## ${heading}"
}

require_file "$README_FILE"
require_file "$CHECKLIST"
require_file "$CITATION"

for h in "Claims" "Evidence Map" "Repro Command" "Environment" "Limitations" "Artifact Manifest" "DOI"; do
  require_heading "$h"
done

repro_cmd=$(awk -F'Command: ' '/^Command: /{print $2; exit}' "$CHECKLIST")
[[ -n "${repro_cmd:-}" ]] || fail "Missing repro command line (expected: Command: <shell command>)"

echo "[qc-lite] Running repro command..."
bash -lc "$repro_cmd" || fail "Repro command failed"

mapfile -t artifact_paths < <(sed -n '/^## Artifact Manifest$/,/^## /p' "$CHECKLIST" | sed -n 's/^- path: //p')
[[ ${#artifact_paths[@]} -gt 0 ]] || fail "Artifact manifest is empty (expected lines: - path: <relative-path>)"
for p in "${artifact_paths[@]}"; do
  [[ -f "$p" ]] || fail "Artifact path missing: $p"
done

release_version=$(awk -F'Release Version: ' '/^Release Version: /{print $2; exit}' "$CHECKLIST")
[[ -n "${release_version:-}" ]] || fail "Missing DOI release version line"
release_norm="${release_version#v}"

citation_version=$(awk -F': ' '/^version:/{gsub(/"/,"",$2); print $2; exit}' "$CITATION")
[[ -n "${citation_version:-}" ]] || fail "Missing version in CITATION.cff"

[[ "$release_norm" == "$citation_version" ]] || fail "Version mismatch: checklist=$release_version citation=$citation_version"

version_doi=$(awk -F'Version DOI: ' '/^Version DOI: /{print $2; exit}' "$CHECKLIST")
concept_doi=$(awk -F'Concept DOI: ' '/^Concept DOI: /{print $2; exit}' "$CHECKLIST")
[[ -n "${version_doi:-}" ]] || fail "Missing Version DOI line"
[[ -n "${concept_doi:-}" ]] || fail "Missing Concept DOI line"

echo "[qc-lite] PASS: minimum rigor and reproducibility checks succeeded"
