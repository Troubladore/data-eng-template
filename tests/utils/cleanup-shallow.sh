#!/bin/bash

# Shallow cleanup script for data-eng-template testing
# Removes generated repo folders and their associated Docker artifacts

set -euo pipefail

echo "🧹 Starting shallow cleanup..."

# Function to safely remove directory
remove_directory() {
    local dir="$1"
    if [[ -d "$dir" ]]; then
        echo "Removing directory: $dir"
        rm -rf "$dir"
    else
        echo "Directory not found (already clean): $dir"
    fi
}

# Function to stop and remove Docker Compose project
cleanup_compose_project() {
    local project_name="$1"
    echo "Cleaning up Docker Compose project: $project_name"

    # Try to stop and remove containers (both running and stopped)
    echo "  Stopping and removing containers..."
    docker compose -p "$project_name" down --remove-orphans --volumes 2>/dev/null || true

    # Remove any leftover containers with both compose labels and our custom labels
    local containers=$(docker ps -a --filter "label=com.docker.compose.project=$project_name" -q 2>/dev/null || true)
    if [[ -n "$containers" ]]; then
        echo "  Removing leftover containers..."
        docker rm -f $containers 2>/dev/null || true
    fi

    # Remove networks
    local networks=$(docker network ls --filter "name=${project_name}" -q 2>/dev/null || true)
    if [[ -n "$networks" ]]; then
        echo "  Removing networks..."
        docker network rm $networks 2>/dev/null || true
    fi

    # Remove volumes
    local volumes=$(docker volume ls --filter "label=com.docker.compose.project=$project_name" -q 2>/dev/null || true)
    if [[ -n "$volumes" ]]; then
        echo "  Removing volumes..."
        docker volume rm $volumes 2>/dev/null || true
    fi
}

# Function to cleanup project artifacts using labels
cleanup_project_by_labels() {
    local project_slug="$1"
    echo "Cleaning up Docker artifacts with project label: $project_slug"

    # Remove containers with de-template.project label
    local containers=$(docker ps -a --filter "label=de-template.project=$project_slug" --format "{{.Names}}" 2>/dev/null || true)
    if [[ -n "$containers" ]]; then
        echo "  Removing labeled containers..."
        echo "$containers" | while IFS= read -r container; do
            if [[ -n "$container" ]]; then
                echo "    Removing container: $container"
                docker rm -f "$container" 2>/dev/null || true
            fi
        done
    fi

    # Remove images with project slug
    cleanup_images "^${project_slug}-"
}

# Function to remove Docker images by pattern
cleanup_images() {
    local pattern="$1"
    echo "Removing Docker images matching pattern: $pattern"

    local images=$(docker images --format "table {{.Repository}}:{{.Tag}}" | grep -E "$pattern" | tr -s ' ' || true)
    if [[ -n "$images" ]]; then
        echo "$images" | while IFS= read -r image; do
            if [[ "$image" != "REPOSITORY:TAG" ]]; then
                echo "  Removing image: $image"
                docker rmi "$image" 2>/dev/null || echo "    Failed to remove $image (might be in use)"
            fi
        done
    else
        echo "  No images found matching pattern"
    fi
}

# Clean up generated repository folders
echo ""
echo "📁 Cleaning up generated repository folders..."

# Look for generated folders in current directory and /tmp ONLY
search_paths=("." "/tmp")

for search_path in "${search_paths[@]}"; do
    if [[ ! -d "$search_path" ]]; then
        continue
    fi

    echo "Searching for generated projects in: $search_path"

    # Look for generated folders (they will have the pattern from cookiecutter defaults)
    if [[ "$search_path" == "/tmp" ]]; then
        # For /tmp, search ONLY one level deep within /tmp (NEVER multiple levels for safety)
        for dir in /tmp/customer-a-etl*/ /tmp/*-etl*/; do
            # CRITICAL SAFETY CHECKS to prevent template directory deletion
            if [[ -d "$dir" ]]; then
                # Never touch anything that contains template patterns
                if [[ "$dir" == *"{{cookiecutter"* || "$dir" == *"}}-etl"* || "$(basename "$dir")" == "data-eng-template" || "$(basename "$dir")" == *"cookiecutter"* ]]; then
                    echo "  SAFETY: Skipping template directory: $dir"
                    continue
                fi
                # Never delete anything not directly in /tmp (safety check)
                parent_dir=$(dirname "$dir")
                if [[ "$parent_dir" != "/tmp" ]]; then
                    echo "  SAFETY: Refusing to delete directory with unsafe path: $dir (parent: $parent_dir)"
                    continue
                fi
                # Check if it looks like a generated project (has .devcontainer folder)
                if [[ -d "$dir/.devcontainer" ]]; then
                    echo "Found generated project: $dir"

                    # Extract project slug from directory name
                    project_slug=$(basename "$dir")

                    # Cleanup associated Docker artifacts
                    echo "  Cleaning up Docker artifacts for: $project_slug"
                    cleanup_compose_project "${project_slug}-modern"
                    cleanup_compose_project "${project_slug}-modern-test"
                    cleanup_compose_project "${project_slug}-test-fast"
                    cleanup_compose_project "${project_slug}-test-fast-test"

                    # Also cleanup by labels (catches any containers not removed by compose)
                    cleanup_project_by_labels "$project_slug"

                    # Remove the directory
                    remove_directory "$dir"
                fi
            fi
        done
    else
        # For current directory, only search top level
        for dir in "$search_path"/customer-a-etl*/ "$search_path"/*-etl*/; do
            # Skip the template directory itself (it has literal {{ }} in the name)
            if [[ -d "$dir" && "$(basename "$dir")" != "data-eng-template" && "$(basename "$dir")" != *"cookiecutter"* ]]; then
                # Check if it looks like a generated project (has .devcontainer folder)
                if [[ -d "$dir/.devcontainer" ]]; then
                    echo "Found generated project: $dir"

                    # Extract project slug from directory name
                    project_slug=$(basename "$dir")

                    # Cleanup associated Docker artifacts
                    echo "  Cleaning up Docker artifacts for: $project_slug"
                    cleanup_compose_project "${project_slug}-modern"
                    cleanup_compose_project "${project_slug}-modern-test"
                    cleanup_compose_project "${project_slug}-test-fast"
                    cleanup_compose_project "${project_slug}-test-fast-test"

                    # Also cleanup by labels (catches any containers not removed by compose)
                    cleanup_project_by_labels "$project_slug"

                    # Remove the directory
                    remove_directory "$dir"
                fi
            fi
        done
    fi
done

# Clean up any orphaned volumes that might be left
echo ""
echo "🗑️  Cleaning up orphaned Docker volumes..."
docker volume prune -f 2>/dev/null || true

echo ""
echo "✅ Shallow cleanup complete!"
echo ""
echo "Summary: Removed generated project folders and their associated Docker artifacts."
echo "To perform a deeper cleanup of all data-eng-template related Docker artifacts, run:"
echo "  ./cleanup-deep.sh"