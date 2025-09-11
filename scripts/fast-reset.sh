#!/bin/bash
# Fast Reset Script for DCSM Testing Iterations
# 
# This script quickly resets the testing environment between test iterations
# for rapid development/testing cycles (30+ iterations expected).
#
# Usage: ./scripts/fast-reset.sh [--deep]
#   --deep: Include slower cleanup (Docker system prune, rebuild validation)

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔄 Starting fast reset for DCSM testing..."

# Function to check if we're in the right directory
check_location() {
    if [[ ! -f "$PROJECT_ROOT/cookiecutter.json" ]] || [[ ! -d "$PROJECT_ROOT/scripts" ]]; then
        echo "❌ Error: Must run from data-eng-template root directory"
        echo "Current location: $(pwd)"
        echo "Expected location: data-eng-template/"
        exit 1
    fi
}

# Function to stop and clean Docker resources
cleanup_docker() {
    echo "🐳 Cleaning up Docker resources..."
    
    # Stop any running compose services from test projects
    for dir in /tmp/*/dcsm-*/.devcontainer /tmp/*/dcsm-test-*/.devcontainer; do
        if [[ -f "$dir/compose.yaml" ]]; then
            echo "  Stopping services in $dir"
            (cd "$dir" && docker compose down -v --remove-orphans 2>/dev/null) || true
        fi
    done
    
    # Stop services in any generated test projects in current directory
    for dir in ./dcsm-*/.devcontainer ./dcsm-test-*/.devcontainer; do
        if [[ -f "$dir/compose.yaml" ]]; then
            echo "  Stopping services in $dir"
            (cd "$dir" && docker compose down -v --remove-orphans 2>/dev/null) || true
        fi
    done
    
    # Remove test project Docker images (they rebuild quickly with caching)
    echo "  Removing test project images..."
    docker images --format "table {{.Repository}}:{{.Tag}}" | grep -E "(dcsm-.*-airflow|devcontainer.*airflow)" | awk '{print $1}' | xargs -r docker rmi -f 2>/dev/null || true
    
    # Remove orphaned test build images
    docker images --filter "dangling=true" --format "table {{.ID}}" | tail -n +2 | xargs -r docker rmi -f 2>/dev/null || true
}

# Function to clean generated test projects 
cleanup_test_projects() {
    echo "📁 Cleaning up generated test projects..."
    
    # Remove any test projects in current directory
    rm -rf ./dcsm-* ./dcsm-test-* 2>/dev/null || true
    
    # Note: /tmp cleanup happens automatically, but we can be explicit
    find /tmp -maxdepth 2 -name "dcsm-*" -type d -exec rm -rf {} + 2>/dev/null || true
}

# Function to reset git state (if needed)
reset_git_state() {
    echo "🔧 Checking git state..."
    
    # Check if we're on the right branch
    current_branch=$(git branch --show-current)
    if [[ "$current_branch" != "add_dcsm" ]]; then
        echo "⚠️  Warning: Not on add_dcsm branch (current: $current_branch)"
        echo "   Run: git checkout add_dcsm"
    fi
    
    # Check for uncommitted changes
    if ! git diff --quiet || ! git diff --cached --quiet; then
        echo "⚠️  Warning: Uncommitted changes detected"
        echo "   You may want to commit or stash changes"
    fi
    
    # Pull latest changes if on correct branch
    if [[ "$current_branch" == "add_dcsm" ]]; then
        echo "  Pulling latest changes..."
        git pull origin add_dcsm --ff-only 2>/dev/null || echo "  (No updates available or conflicts detected)"
    fi
}

# Function for deeper cleanup (slower)
deep_cleanup() {
    echo "🧹 Performing deep cleanup..."
    
    # Docker system cleanup
    echo "  Docker system prune..."
    docker system prune -f --volumes || true
    
    # Rebuild validation environment to catch dependency changes
    if [[ -f "$PROJECT_ROOT/pyproject.toml" ]]; then
        echo "  Updating validation environment with uv..."
        (cd "$PROJECT_ROOT" && uv sync --quiet) || true
    fi
}

# Main execution
main() {
    check_location
    
    echo "📍 Working directory: $PROJECT_ROOT"
    
    cleanup_docker
    cleanup_test_projects
    reset_git_state
    
    # Deep cleanup if requested
    if [[ "$1" == "--deep" ]]; then
        deep_cleanup
    fi
    
    echo ""
    echo "✅ Fast reset complete! Environment ready for next test iteration."
    echo ""
    echo "🚀 Quick validation test:"
    echo "   source .venv/bin/activate  # (created by uv sync)"
    echo "   python scripts/validate-dcsm-integration.py --quick --no-docker"
    echo ""
    echo "💡 For 30+ iterations, run this script between tests:"
    echo "   ./scripts/fast-reset.sh"
    echo "   (Add --deep flag occasionally for thorough cleanup)"
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Fast Reset Script for DCSM Testing Iterations"
        echo ""
        echo "Usage: $0 [--deep] [--help]"
        echo "  --deep    Include slower cleanup (Docker prune, dep updates)"
        echo "  --help    Show this help message"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac