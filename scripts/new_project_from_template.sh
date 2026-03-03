#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE_DIR="$ROOT_DIR/_project-template"

usage() {
  echo "Usage: scripts/new_project_from_template.sh <project-name>"
  echo
  echo "Example:"
  echo "  scripts/new_project_from_template.sh gaussian-phasewall-v2"
}

fail() {
  echo "[new-project] ERROR: $1" >&2
  exit 1
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

PROJECT_NAME="${1:-}"
[[ -n "$PROJECT_NAME" ]] || { usage; exit 1; }

if [[ "$PROJECT_NAME" == */* ]]; then
  fail "Project name must be a single folder name (no '/')."
fi

DEST_DIR="$ROOT_DIR/$PROJECT_NAME"

[[ -d "$TEMPLATE_DIR" ]] || fail "Template not found: $TEMPLATE_DIR"
[[ ! -e "$DEST_DIR" ]] || fail "Destination already exists: $DEST_DIR"

cp -R "$TEMPLATE_DIR" "$DEST_DIR"

# Clear template-only defaults that should be filled by the new project owner.
sed -i '' "s/^# Project Title (Template)$/# ${PROJECT_NAME}/" "$DEST_DIR/README.md"
sed -i '' "s/^title: \"Project Title\"$/title: \"${PROJECT_NAME}\"/" "$DEST_DIR/CITATION.cff"

cat <<MSG
[new-project] Created: $DEST_DIR

Next steps:
1. Update $PROJECT_NAME/QC_CHECKLIST.md
2. Update $PROJECT_NAME/CITATION.cff (authors/repository/date)
3. Write $PROJECT_NAME/docs/technical-note/technical_note.md
4. Run: $PROJECT_NAME/scripts/qc_check.sh
MSG
