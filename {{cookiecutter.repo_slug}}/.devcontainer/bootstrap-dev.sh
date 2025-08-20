#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT_ENV="${ROOT_DIR}/.env"


# Ensure the root .env exists
[[ -f "$ROOT_ENV" ]] || touch "$ROOT_ENV"

# Ensure LOAD_EXAMPLES default exists (idempotent)
grep -q '^AIRFLOW__CORE__LOAD_EXAMPLES=' "$ROOT_ENV" || echo "AIRFLOW__CORE__LOAD_EXAMPLES=False" >> "$ROOT_ENV"

# Ensure Fernet key exists (idempotent)
if ! grep -q '^AIRFLOW__CORE__FERNET_KEY=' "$ROOT_ENV"; then
  FERNET_KEY=$(python - <<'PY'
import base64, os
print(base64.urlsafe_b64encode(os.urandom(32)).decode())
PY
)
  echo "AIRFLOW__CORE__FERNET_KEY=${FERNET_KEY}" >> "$ROOT_ENV"
  echo "Added Fernet key to $ROOT_ENV"
fi

echo "Bootstrap complete."
