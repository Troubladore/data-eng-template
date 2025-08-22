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

echo "DevContainer environment setup complete!"
