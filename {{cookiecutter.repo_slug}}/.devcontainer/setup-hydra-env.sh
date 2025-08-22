#!/bin/bash
# Setup environment variables from Hydra configuration for DevContainer
# This script bridges Hydra configs to Docker Compose environment files

set -euo pipefail

echo "Setting up environment variables from Hydra configuration..."

# Change to project root (inside devcontainer, this is /workspaces/{{cookiecutter.repo_slug}})
# But if we're in the project directory already, stay here
if [ -d "/workspaces/{{cookiecutter.repo_slug}}" ]; then
    cd "/workspaces/{{cookiecutter.repo_slug}}"
elif [ -f "pyproject.toml" ]; then
    # We're already in the project directory
    echo "Already in project directory"
else
    echo "Error: Cannot find project directory"
    exit 1
fi

# Generate .env file from Hydra configuration
echo "Generating .env file from Hydra configuration..."

# Use the export_env.sh script to get environment variables
if [ -f "scripts/export_env.sh" ]; then
    # Run the export script and save to .env file
    bash scripts/export_env.sh > .env
    
    echo "Created .env file with $(wc -l < .env) environment variables"
    echo "Environment setup complete!"
else
    echo "Warning: scripts/export_env.sh not found, creating minimal .env"
    
    # Fallback: create minimal .env with essential variables
    cat > .env << ENVEOF
# Minimal fallback environment variables
AIRFLOW__CORE__EXECUTOR=LocalExecutor
POSTGRES_DB=airflow
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
ENVEOF
    
    echo "Created fallback .env file"
fi

# Make sure .env file is readable
chmod 644 .env

# Also populate Docker Compose environment files
echo "Updating Docker Compose environment files..."

# Extract values from .env for use in compose env files
if [ -f ".env" ]; then
    # Read the .env file and extract necessary variables
    # Convert export format to plain format and source it
    sed 's/^export //' .env | sed "s/'//g" > .env.tmp
    source .env.tmp 2>/dev/null || true
    rm -f .env.tmp
    
    # Update Airflow environment file
    cat > .devcontainer/airflow.env << AIRFLOWEOF
AIRFLOW_UID=50000
AIRFLOW_GID=0
PIP_USER=false
AIRFLOW__CORE__FERNET_KEY=${AIRFLOW__CORE__FERNET_KEY:-}
_AIRFLOW_WWW_USER_USERNAME=${_AIRFLOW_WWW_USER_USERNAME:-admin}
_AIRFLOW_WWW_USER_PASSWORD=${_AIRFLOW_WWW_USER_PASSWORD:-admin}
AIRFLOWEOF

    # Update Postgres environment file
    cat > .devcontainer/postgres.env << POSTGRESEOF
POSTGRES_DB=${POSTGRES_DB:-airflow}
POSTGRES_USER=${POSTGRES_USER:-airflow}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-airflow}
POSTGRESEOF

    # Create Docker Compose .env file (for variable substitution in compose.yaml)
    cat > .devcontainer/.env << COMPOSEEOF
AIRFLOW__CORE__FERNET_KEY=${AIRFLOW__CORE__FERNET_KEY:-}
AIRFLOW__CORE__EXECUTOR=${AIRFLOW__CORE__EXECUTOR:-LocalExecutor}
AIRFLOW__CORE__LOAD_EXAMPLES=${AIRFLOW__CORE__LOAD_EXAMPLES:-False}
POSTGRES_USER=${POSTGRES_USER:-airflow}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-airflow}
POSTGRES_DB=${POSTGRES_DB:-airflow}
PYTHON_VERSION=${PYTHON_VERSION:-3.12}
POSTGRES_VERSION=${POSTGRES_VERSION:-16}
AIRFLOW_VERSION=${AIRFLOW_VERSION:-2.9.3}
COMPOSEEOF

    echo "Updated Docker Compose environment files"
else
    echo "Warning: .env file not found, using defaults in compose env files"
fi

echo "DevContainer environment setup complete!"
