#!/usr/bin/env bash
set -euo pipefail
source ./.env 2>/dev/null || true

echo
echo "Airflow URLs for ${COMPOSE_PROJECT_NAME:-project} (${ENV_NAME:-dev})"
[[ -n "${SUBDOMAIN_STANDARD:-}" ]] && echo "STANDARD: http://${SUBDOMAIN_STANDARD}"
[[ -n "${SUBDOMAIN_HIGH:-}"     ]] && echo "HIGH    : http://${SUBDOMAIN_HIGH}"
[[ -n "${PROD_STANDARD:-}"      ]] && echo "(prod std) http://${PROD_STANDARD}"
[[ -n "${PROD_HIGH:-}"          ]] && echo "(prod high) http://${PROD_HIGH}"
astro dev ps || true
