#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"

CHECKLIST="$REPO_ROOT/QC_CHECKLIST.md"
CITATION="$REPO_ROOT/CITATION.cff"
README_FILE="$REPO_ROOT/README.md"
LICENSE_FILE="$REPO_ROOT/LICENSE"
ZENODO_FILE="$REPO_ROOT/.zenodo.json"
HASH_MANIFEST="$REPO_ROOT/artifacts/SHA256SUMS"
CLAIMS_CSV="$REPO_ROOT/artifacts/results/phasewall_vs_vanilla_claims.csv"

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
require_file "$LICENSE_FILE"
require_file "$ZENODO_FILE"
require_file "$HASH_MANIFEST"
require_file "$CLAIMS_CSV"

for h in "Claims" "Evidence Map" "Repro Command" "Environment" "Limitations" "Artifact Manifest" "DOI"; do
  require_heading "$h"
done

repro_cmd=$(awk -F'Command: ' '/^Command: /{print $2; exit}' "$CHECKLIST")
[[ -n "${repro_cmd:-}" ]] || fail "Missing repro command line (expected: Command: <shell command>)"
[[ "$repro_cmd" == "bash scripts/qc_check.sh" ]] || fail "Repro command must be: bash scripts/qc_check.sh"

doi_section=$(sed -n '/^## DOI$/,/^## /p' "$CHECKLIST")
echo "$doi_section" | grep -q "TBD" && fail "DOI section contains TBD placeholders"

mapfile -t artifact_paths < <(sed -n '/^## Artifact Manifest$/,/^## /p' "$CHECKLIST" | sed -n 's/^- path: //p')
[[ ${#artifact_paths[@]} -gt 0 ]] || fail "Artifact manifest is empty (expected lines: - path: <relative-path>)"
for p in "${artifact_paths[@]}"; do
  [[ -f "$REPO_ROOT/$p" ]] || fail "Artifact path missing: $p"
done

release_version=$(awk -F'Release Version: ' '/^Release Version: /{print $2; exit}' "$CHECKLIST")
[[ -n "${release_version:-}" ]] || fail "Missing DOI release version line"
release_norm="${release_version#v}"

citation_version=$(awk -F': ' '/^version:/{gsub(/"/,"",$2); print $2; exit}' "$CITATION")
[[ -n "${citation_version:-}" ]] || fail "Missing version in CITATION.cff"

[[ "$release_norm" == "$citation_version" ]] || fail "Version mismatch: checklist=$release_version citation=$citation_version"

python3 "$SCRIPT_DIR/verify_hashes.py" "$HASH_MANIFEST"
python3 "$SCRIPT_DIR/verify_report_claims.py" "$CLAIMS_CSV"

echo "[qc-lite] PASS: minimum rigor and reproducibility checks succeeded"
