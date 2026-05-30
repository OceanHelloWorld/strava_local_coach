#!/usr/bin/env bash
# Launch a strava-coach Python entrypoint, resolving the `mcp` dependency with
# zero manual setup. Prefers `uv` (fast, auto-installs deps); if uv isn't present,
# falls back to a self-managed venv created with the system python3.
#
# Usage: _run.sh <script.py> [args...]
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"

if command -v uv >/dev/null 2>&1; then
  exec uv run --directory "$DIR" "$@"
fi

# Fallback: create/reuse a local venv with mcp installed.
VENV="$DIR/.venv"
PY="${PYTHON:-python3}"
if [ ! -x "$VENV/bin/python" ]; then
  "$PY" -m venv "$VENV"
  "$VENV/bin/python" -m pip install --quiet --upgrade pip
  "$VENV/bin/python" -m pip install --quiet "mcp>=1.2.0"
fi
SCRIPT="$1"; shift
exec "$VENV/bin/python" "$DIR/$SCRIPT" "$@"
