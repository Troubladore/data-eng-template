#!/usr/bin/env bash
set -euo pipefail

# Require uv (installation managed by Ansible)
if ! command -v uv >/dev/null 2>&1; then
  echo "[post-start] uv not found; skipping sync. Install uv via curl or Ansible." >&2
  exit 0
fi

# Optional: check for newer uv (non-fatal)
uv self update --check || true

# Only sync if lockfile changed (speedy on no-op)
LOCK_FILE="${WORKSPACE_FOLDER:-/workspaces/$(basename "$PWD")}/uv.lock"
STATE_DIR=".venv/.uv"
STATE_HASH="${STATE_DIR}/lock.sha256"

mkdir -p "${STATE_DIR}"

if [[ -f "${LOCK_FILE}" ]]; then
  NEW_HASH=$(sha256sum "${LOCK_FILE}" | awk '{print $1}')
else
  # No lock? fall back to resolving from pyproject
  NEW_HASH=$(sha256sum pyproject.toml | awk '{print $1}')
fi

OLD_HASH=""
[[ -f "${STATE_HASH}" ]] && OLD_HASH=$(cat "${STATE_HASH}")

if [[ "${NEW_HASH}" != "${OLD_HASH}" ]]; then
  echo "[post-start] Dependency spec changed → running 'uv sync --frozen'..."
  uv sync --frozen
  echo "${NEW_HASH}" > "${STATE_HASH}"
  
  # Refresh environment variables after dependency update
  echo "[post-start] Refreshing environment variables from Hydra..."
  bash .devcontainer/setup-hydra-env.sh
else
  echo "[post-start] Environment up to date; no sync needed."
fi

# Report host port mappings for Postgres services
for svc in postgres warehouse; do
  if docker compose -f .devcontainer/compose.yaml ps "$svc" >/dev/null 2>&1; then
    PORT=$(docker compose -f .devcontainer/compose.yaml port "$svc" 5432 2>/dev/null | awk -F: '{print $2}')
    [[ -n "${PORT:-}" ]] && echo "[post-start] Host port for $svc → $PORT"
  fi
done

# Ensure services are up (use docker/podman compose via devcontainers engine)
echo "Devcontainer started. Airflow should be reachable on http://localhost:8080"
