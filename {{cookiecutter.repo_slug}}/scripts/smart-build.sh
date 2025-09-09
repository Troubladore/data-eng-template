#!/bin/bash
# Smart Docker build system with fingerprint-based caching
# Works across repos and branches to minimize redundant builds

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Import fingerprinting system
FINGERPRINT_SCRIPT="$PROJECT_ROOT/../tests/docker/fingerprint.py"

usage() {
    cat << EOF
Smart Docker Build System

Usage: $0 [OPTIONS] <build-type>

Build Types:
  airflow         - Build Airflow environment (SQLAlchemy 1.4.x)
  data-processing - Build modern data processing environment (SQLAlchemy 2.0+)  
  all            - Build both environments
  
Options:
  -h, --help     Show this help message
  --no-cache     Force rebuild without checking cache
  --push-only    Only push to cache, don't build locally
  
Examples:
  $0 airflow                    # Smart build Airflow environment
  $0 data-processing            # Smart build data processing environment  
  $0 all                        # Smart build both environments
  $0 --no-cache airflow         # Force rebuild Airflow environment

The smart build system:
1. Computes fingerprints based on dependencies and Docker configuration
2. Checks cross-repo cache for existing builds
3. Pulls from cache if available, builds locally if not
4. Pushes successful builds to cache for other repos/branches
EOF
}

build_airflow() {
    echo "🚀 Smart building Airflow environment..."
    
    if [[ "${NO_CACHE:-}" == "true" ]]; then
        docker build -f Dockerfile.airflow -t "{{cookiecutter.repo_slug}}-airflow" .
    else
        python3 "$FINGERPRINT_SCRIPT" \
            "$PROJECT_ROOT" \
            "Dockerfile.airflow" \
            "{{cookiecutter.repo_slug}}-airflow" \
            "airflow" \
            "airflow/requirements.txt" \
            "pyproject.toml"
    fi
}

build_data_processing() {
    echo "🚀 Smart building data processing environment..."
    
    if [[ "${NO_CACHE:-}" == "true" ]]; then
        docker build -f Dockerfile.data-processing -t "{{cookiecutter.repo_slug}}-data-processing" .
    else
        python3 "$FINGERPRINT_SCRIPT" \
            "$PROJECT_ROOT" \
            "Dockerfile.data-processing" \
            "{{cookiecutter.repo_slug}}-data-processing" \
            "data-processing" \
            "transforms/requirements.txt" \
            "pyproject.toml"
    fi
}

validate_environments() {
    echo "🧪 Validating environments..."
    
    # Test Airflow environment - should have SQLAlchemy 1.4.x
    echo "Testing Airflow environment (SQLAlchemy 1.4.x)..."
    docker run --rm "{{cookiecutter.repo_slug}}-airflow" python -c "
import sqlalchemy as sa
import airflow
print(f'✅ Airflow: {airflow.__version__}')
print(f'✅ SQLAlchemy: {sa.__version__}')
assert sa.__version__.startswith('1.4'), f'Expected SQLAlchemy 1.4.x, got {sa.__version__}'
print('✅ Airflow environment validated')
"
    
    # Test data processing environment - should have SQLAlchemy 2.0+
    echo "Testing data processing environment (SQLAlchemy 2.0+)..."
    docker run --rm "{{cookiecutter.repo_slug}}-data-processing" python -c "
import sqlalchemy as sa
import pandas as pd
print(f'✅ SQLAlchemy: {sa.__version__}')
print(f'✅ Pandas: {pd.__version__}')
assert sa.__version__.startswith('2.'), f'Expected SQLAlchemy 2.x, got {sa.__version__}'
print('✅ Data processing environment validated')
"
    
    echo "🎉 Both environments validated successfully!"
}

# Parse command line arguments
NO_CACHE="false"
PUSH_ONLY="false"
BUILD_TYPE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        --no-cache)
            NO_CACHE="true"
            shift
            ;;
        --push-only)
            PUSH_ONLY="true" 
            shift
            ;;
        airflow|data-processing|all)
            BUILD_TYPE="$1"
            shift
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage
            exit 1
            ;;
    esac
done

if [[ -z "$BUILD_TYPE" ]]; then
    echo "Error: Build type required" >&2
    usage
    exit 1
fi

# Check if fingerprint script exists
if [[ ! -f "$FINGERPRINT_SCRIPT" ]]; then
    echo "⚠️ Fingerprint script not found, falling back to regular Docker build"
    NO_CACHE="true"
fi

# Execute builds
case "$BUILD_TYPE" in
    airflow)
        build_airflow
        if [[ "${PUSH_ONLY:-}" != "true" ]]; then
            validate_environments || true
        fi
        ;;
    data-processing)
        build_data_processing
        if [[ "${PUSH_ONLY:-}" != "true" ]]; then
            validate_environments || true
        fi
        ;;
    all)
        build_airflow
        build_data_processing
        if [[ "${PUSH_ONLY:-}" != "true" ]]; then
            validate_environments
        fi
        ;;
esac

echo "✅ Smart build completed for: $BUILD_TYPE"