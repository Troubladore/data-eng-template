#!/bin/bash
# Data Engineering Template - Complete Test Environment Teardown
#
# This script completely resets the testing environment for data-eng-template
# Can be run remotely without having the repo checked out locally.
#
# Usage:
#   # Remote execution (recommended for clean reset)
#   curl -fsSL https://raw.githubusercontent.com/Troubladore/data-eng-template/add_dcsm/scripts/teardown-test-environment.sh | bash
#   
#   # Or download and run locally  
#   wget https://raw.githubusercontent.com/Troubladore/data-eng-template/add_dcsm/scripts/teardown-test-environment.sh
#   chmod +x teardown-test-environment.sh
#   ./teardown-test-environment.sh
#
# What this script does:
# ✅ Deactivates virtual environments
# ✅ Stops and removes all test containers
# ✅ Removes derived Docker images (keeps base images)
# ✅ Removes local repository clone
# ✅ Cleans up temporary files
# ✅ Provides detailed progress feedback

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_header() {
    echo
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
}

# Function to safely run commands
safe_run() {
    local cmd="$1"
    local description="$2"
    
    if eval "$cmd" 2>/dev/null; then
        if [ -n "$description" ]; then
            log_success "$description"
        fi
        return 0
    else
        if [ -n "$description" ]; then
            log_warning "$description (not found or already removed)"
        fi
        return 1
    fi
}

# Main teardown function
main() {
    log_header "Data Engineering Template - Test Environment Teardown"
    echo "This script will completely reset your test environment."
    echo "It's safe to run multiple times and will skip already-cleaned items."
    echo
    
    # Step 1: Deactivate virtual environments
    log_header "Step 1: Virtual Environment Cleanup"
    
    # Deactivate any active conda/mamba environments
    if [[ "$CONDA_DEFAULT_ENV" != "" ]] || [[ "$CONDA_PREFIX" != "" ]]; then
        log_info "Deactivating conda environment: $CONDA_DEFAULT_ENV"
        # Note: conda deactivate doesn't work in non-interactive shells
        export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v "$CONDA_PREFIX" | tr '\n' ':')
        unset CONDA_DEFAULT_ENV CONDA_PREFIX
        log_success "Conda environment deactivated"
    fi
    
    # Deactivate Python virtual environment
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        log_info "Deactivating Python virtual environment: $VIRTUAL_ENV"
        deactivate 2>/dev/null || true
        log_success "Python virtual environment deactivated"
    fi
    
    # Step 2: Docker Container and Service Cleanup
    log_header "Step 2: Docker Container Cleanup"
    
    # Find and stop containers related to data-eng-template testing
    local test_containers
    test_containers=$(docker ps -a --format "table {{.Names}}" | grep -E "(data-eng|dcsm-|airflow|postgres)" | tail -n +2 || true)
    
    if [ -n "$test_containers" ]; then
        log_info "Found test containers to clean up"
        echo "$test_containers" | while read -r container; do
            if [ -n "$container" ]; then
                safe_run "docker stop '$container'" "Stopped container: $container"
                safe_run "docker rm '$container'" "Removed container: $container"
            fi
        done
    else
        log_success "No test containers found to clean up"
    fi
    
    # Stop any remaining compose services (in case containers were started via compose)
    for dir in ~/repos/data-eng-template*/; do
        if [[ -d "$dir" ]]; then
            compose_file="$dir/.devcontainer/compose.yaml"
            if [[ -f "$compose_file" ]]; then
                log_info "Stopping compose services in $dir"
                safe_run "cd '$dir' && docker compose -f '$compose_file' down -v --remove-orphans" "Stopped compose services in $dir"
            fi
        fi
    done
    
    # Step 3: Docker Image Cleanup (Keep Base Images, Remove Derived)
    log_header "Step 3: Docker Image Cleanup"
    
    log_info "Cleaning up derived images (preserving base images)..."
    
    # Remove images that are clearly derived from our testing
    local derived_patterns=(
        "data-eng.*-airflow"
        "dcsm.*-airflow" 
        ".*test.*airflow"
        "devcontainer.*airflow"
        ".*-airflow-dev"
        "localhost.*data-eng"
        "localhost.*dcsm"
    )
    
    for pattern in "${derived_patterns[@]}"; do
        local images
        images=$(docker images --format "table {{.Repository}}:{{.Tag}}" | grep -E "$pattern" | tail -n +2 || true)
        if [ -n "$images" ]; then
            echo "$images" | while read -r image; do
                if [ -n "$image" ] && [[ "$image" != "REPOSITORY:TAG" ]]; then
                    safe_run "docker rmi -f '$image'" "Removed derived image: $image"
                fi
            done
        fi
    done
    
    # Remove dangling images (untagged images that take up space)
    local dangling_images
    dangling_images=$(docker images -f "dangling=true" -q || true)
    if [ -n "$dangling_images" ]; then
        log_info "Removing dangling images..."
        safe_run "echo '$dangling_images' | xargs docker rmi -f" "Removed dangling images"
    fi
    
    # Preserve base images (these are expensive to re-download)
    log_info "Preserving base images (postgres, python, apache/airflow, etc.)"
    local preserved_count
    preserved_count=$(docker images --format "table {{.Repository}}" | grep -E "(postgres|python|apache/airflow|mcr.microsoft.com)" | wc -l || echo "0")
    log_success "Preserved $preserved_count base images for faster future builds"
    
    # Step 4: Repository Cleanup
    log_header "Step 4: Repository Cleanup"
    
    # Remove data-eng-template repositories
    for dir in ~/repos/data-eng-template*; do
        if [[ -d "$dir" ]]; then
            log_info "Removing repository: $dir"
            safe_run "rm -rf '$dir'" "Removed repository: $dir"
        fi
    done
    
    # Also check current directory if it's a data-eng-template
    if [[ "$(basename "$(pwd)")" == "data-eng-template"* ]]; then
        local current_dir="$(pwd)"
        log_info "Current directory appears to be a test repo: $current_dir"
        log_info "Changing to parent directory before cleanup"
        cd ..
        safe_run "rm -rf '$current_dir'" "Removed current test repository: $current_dir"
    fi
    
    # Step 5: Temporary Files Cleanup  
    log_header "Step 5: Temporary Files Cleanup"
    
    # Clean up cookiecutter temp files
    safe_run "find /tmp -maxdepth 2 -name '*dcsm*' -type d -exec rm -rf {} + 2>/dev/null" "Cleaned up cookiecutter temp files"
    safe_run "find /tmp -maxdepth 1 -name 'tmp*' -name '*data-eng*' -type d -exec rm -rf {} + 2>/dev/null" "Cleaned up temporary build files"
    
    # Clean up UV cache if it's taking up too much space
    if [[ -d ~/.cache/uv ]] && [[ $(du -sm ~/.cache/uv 2>/dev/null | cut -f1) -gt 100 ]]; then
        log_info "UV cache is large (>100MB), cleaning up..."
        safe_run "rm -rf ~/.cache/uv" "Cleaned up UV cache"
    fi
    
    # Step 6: Docker System Cleanup (Optional)
    log_header "Step 6: Docker System Cleanup"
    
    # Ask user if they want to run docker system prune (this is more aggressive)
    if [[ "${1:-}" == "--deep" ]]; then
        log_info "Running deep Docker cleanup (--deep flag provided)..."
        safe_run "docker system prune -f" "Docker system prune completed"
        safe_run "docker volume prune -f" "Docker volume prune completed"
    else
        log_info "Skipping docker system prune (use --deep flag for thorough cleanup)"
        log_info "Run 'docker system prune -f' manually if you want to reclaim more space"
    fi
    
    # Final summary
    log_header "Teardown Complete!"
    
    echo
    log_success "Test environment has been completely reset"
    echo
    echo "What was cleaned up:"
    echo "  🔧 Virtual environments deactivated"
    echo "  🐳 Test containers stopped and removed"  
    echo "  🏗️  Derived Docker images removed (base images preserved)"
    echo "  📁 Repository clones removed"
    echo "  🧹 Temporary files cleaned up"
    echo
    echo "You can now start fresh with:"
    echo "  git clone https://github.com/Troubladore/data-eng-template.git"
    echo "  cd data-eng-template"
    echo "  git checkout add_dcsm"
    echo "  uv sync"
    echo
    log_info "Next test run will benefit from preserved base images (faster Docker pulls)"
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Data Engineering Template - Test Environment Teardown"
        echo
        echo "Usage: $0 [--deep] [--help]"
        echo "  --deep    Include aggressive Docker cleanup (system prune)"
        echo "  --help    Show this help message"
        echo
        echo "This script can be run remotely:"
        echo "  curl -fsSL https://raw.githubusercontent.com/Troubladore/data-eng-template/add_dcsm/scripts/teardown-test-environment.sh | bash"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac