#!/usr/bin/env bash
set -euo pipefail
if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found. Install uv first." >&2
  exit 1
fi
uv export --frozen --no-hashes -o requirements.txt
