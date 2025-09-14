#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Cleaning up for fresh start..."

# Stop and remove all devcontainer services
echo "Stopping containers..."
docker compose -f "${ROOT_DIR}/.devcontainer/compose.yaml" down -v --remove-orphans || true

# Remove any dangling containers with our project name
echo "Removing any remaining containers..."
docker ps -a --filter "name=data-eng-template_devcontainer" -q | xargs -r docker rm -f || true

# Remove volumes
echo "Removing volumes..."
docker volume ls --filter "name=data-eng-template_devcontainer" -q | xargs -r docker volume rm || true

# Clean up generated files
echo "Removing generated files..."
rm -f "${ROOT_DIR}/.env"

echo "Clean complete. Ready for fresh devcontainer up."