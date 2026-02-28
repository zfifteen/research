#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PY="$SCRIPT_DIR/.venv/bin/python"

if [[ ! -x "$VENV_PY" ]]; then
  echo "Missing virtual environment at $SCRIPT_DIR/.venv"
  echo "Create it with:"
  echo "  python3 -m venv $SCRIPT_DIR/.venv"
  echo "  $SCRIPT_DIR/.venv/bin/python -m pip install -r $SCRIPT_DIR/requirements.txt"
  exit 1
fi

export MPLBACKEND=Agg
export XDG_CACHE_HOME="$SCRIPT_DIR/.cache"
export MPLCONFIGDIR="$SCRIPT_DIR/.cache/matplotlib"
mkdir -p "$MPLCONFIGDIR"

cd "$SCRIPT_DIR"
exec "$VENV_PY" dynamical_symmetry_breaking.py
