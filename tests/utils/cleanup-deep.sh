#!/bin/bash

# Deep cleanup script for data-eng-template testing
# Removes ALL test-related data-eng-template Docker artifacts and generated repos

set -euo pipefail

echo "🧹 Starting deep cleanup..."
echo "⚠️  WARNING: This will remove ALL Docker artifacts that might be related to data-eng-template testing!"
echo ""

# Function to prompt for confirmation
confirm_cleanup() {
    read -p "Are you sure you want to proceed with deep cleanup? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cleanup cancelled."
        exit 1
    fi
}

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

# Function to cleanup all containers matching patterns
cleanup_containers() {
    echo "🐳 Cleaning up containers..."

    # First, cleanup all containers with de-template labels (most reliable)
    echo "  Cleaning up containers with de-template labels..."
    local de_template_containers=$(docker ps -a --filter "label=de-template.project" --format "{{.Names}}" 2>/dev/null || true)
    if [[ -n "$de_template_containers" ]]; then
        echo "    Found $(echo $de_template_containers | wc -w) containers with de-template labels"
        echo "$de_template_containers" | while IFS= read -r container; do
            if [[ -n "$container" ]]; then
                echo "      Removing labeled container: $container"
                docker rm -f "$container" 2>/dev/null || true
            fi
        done
    fi

    # Stop and remove containers from known compose projects
    echo "  Cleaning up Docker Compose projects..."
    local compose_patterns=(
        "*-etl-modern*"
        "*-etl-test-fast*"
        "*-modern*"
        "*-test-fast*"
        "customer-a-etl-*"
    )

    for pattern in "${compose_patterns[@]}"; do
        local projects=$(docker compose ls --format json 2>/dev/null | jq -r '.[] | select(.Name | test("'"${pattern//\*/.*}"'")) | .Name' 2>/dev/null || true)
        if [[ -n "$projects" ]]; then
            echo "$projects" | while IFS= read -r project; do
                echo "    Stopping Docker Compose project: $project"
                docker compose -p "$project" down --remove-orphans --volumes --rmi local 2>/dev/null || true
            done
        fi
    done

    # Remove any remaining containers with data-eng-template related names
    echo "  Cleaning up remaining containers by name patterns..."
    local container_patterns=(
        "*-etl-*"
        "*airflow*"
        "*postgres*"
        "customer-a*"
    )

    for pattern in "${container_patterns[@]}"; do
        local containers=$(docker ps -a --format "table {{.Names}}" | grep -E "${pattern//\*/.*}" | tail -n +2 || true)
        if [[ -n "$containers" ]]; then
            echo "    Removing containers matching pattern: $pattern"
            echo "$containers" | while IFS= read -r container; do
                if [[ -n "$container" && "$container" != "NAMES" ]]; then
                    echo "      Removing container: $container"
                    docker rm -f "$container" 2>/dev/null || true
                fi
            done
        fi
    done
}

# Function to cleanup all images
cleanup_images() {
    echo "🖼️  Cleaning up images..."

    # Remove images with specific patterns
    local image_patterns=(
        "*-etl-airflow-dev"
        "*-etl-airflow-fast-test"
        "*-airflow-dev"
        "*-airflow-fast-test"
        "customer-a-etl-*"
        "*-etl-*"
    )

    for pattern in "${image_patterns[@]}"; do
        local images=$(docker images --format "table {{.Repository}}:{{.Tag}}" | grep -E "${pattern//\*/.*}" || true)
        if [[ -n "$images" ]]; then
            echo "  Removing images matching pattern: $pattern"
            echo "$images" | tail -n +2 | while IFS= read -r image; do
                if [[ -n "$image" && "$image" != "REPOSITORY:TAG" ]]; then
                    echo "    Removing image: $image"
                    docker rmi -f "$image" 2>/dev/null || echo "      Failed to remove $image (might be in use)"
                fi
            done
        fi
    done

    # Remove untagged images (the <none> ones mentioned in the issue)
    echo "  Removing untagged images..."
    local untagged=$(docker images -f "dangling=true" -q || true)
    if [[ -n "$untagged" ]]; then
        echo "    Found $(echo $untagged | wc -w) untagged images"
        docker rmi -f $untagged 2>/dev/null || echo "    Some untagged images could not be removed"
    else
        echo "    No untagged images found"
    fi

    # Clean up any postgres images used for testing (be careful with this)
    echo "  Checking for postgres test images..."
    local postgres_images=$(docker images postgres --format "table {{.Repository}}:{{.Tag}}" | tail -n +2 || true)
    if [[ -n "$postgres_images" ]]; then
        echo "    Found postgres images (review manually if needed):"
        echo "$postgres_images" | while IFS= read -r image; do
            echo "      $image"
        done
    fi
}

# Function to cleanup volumes
cleanup_volumes() {
    echo "💾 Cleaning up volumes..."

    # Remove volumes with specific patterns
    local volume_patterns=(
        "*-etl-*"
        "*airflow*"
        "*postgres*"
        "customer-a*"
    )

    for pattern in "${volume_patterns[@]}"; do
        local volumes=$(docker volume ls --format "table {{.Name}}" | grep -E "${pattern//\*/.*}" | tail -n +2 || true)
        if [[ -n "$volumes" ]]; then
            echo "  Removing volumes matching pattern: $pattern"
            echo "$volumes" | while IFS= read -r volume; do
                if [[ -n "$volume" && "$volume" != "VOLUME" ]]; then
                    echo "    Removing volume: $volume"
                    docker volume rm "$volume" 2>/dev/null || echo "      Failed to remove $volume (might be in use)"
                fi
            done
        fi
    done

    # Remove all orphaned volumes
    echo "  Removing orphaned volumes..."
    docker volume prune -f 2>/dev/null || true
}

# Function to cleanup networks
cleanup_networks() {
    echo "🌐 Cleaning up networks..."

    local network_patterns=(
        "*-etl-*"
        "*-modern*"
        "*-test-fast*"
        "customer-a*"
    )

    for pattern in "${network_patterns[@]}"; do
        local networks=$(docker network ls --format "table {{.Name}}" | grep -E "${pattern//\*/.*}" | tail -n +2 || true)
        if [[ -n "$networks" ]]; then
            echo "  Removing networks matching pattern: $pattern"
            echo "$networks" | while IFS= read -r network; do
                if [[ -n "$network" && "$network" != "NAME" ]]; then
                    echo "    Removing network: $network"
                    docker network rm "$network" 2>/dev/null || echo "      Failed to remove $network (might be in use)"
                fi
            done
        fi
    done

    # Remove unused networks
    echo "  Removing unused networks..."
    docker network prune -f 2>/dev/null || true
}

# Function to cleanup build cache
cleanup_build_cache() {
    echo "🗂️  Cleaning up build cache..."
    echo "  Current build cache usage:"
    docker system df 2>/dev/null || true

    echo "  Removing build cache..."
    docker builder prune -f 2>/dev/null || true
}

# Prompt for confirmation
confirm_cleanup

# Run shallow cleanup first (includes generated directories)
echo ""
echo "🔄 Running shallow cleanup first..."
if [[ -f "./cleanup-shallow.sh" ]]; then
    ./cleanup-shallow.sh
else
    echo "Warning: cleanup-shallow.sh not found, continuing with deep cleanup only..."
fi

echo ""
echo "🧽 Performing deep cleanup operations..."

# Cleanup Docker artifacts
cleanup_containers
cleanup_images
cleanup_volumes
cleanup_networks
cleanup_build_cache

# Remove any additional generated directories that might have been missed
echo ""
echo "📁 Final directory cleanup..."
for dir in */; do
    if [[ -d "$dir" && "$dir" != "data-eng-template/" ]]; then
        # Check if it has a .devcontainer (likely generated) and no .git (not a real repo)
        if [[ -d "$dir/.devcontainer" && ! -d "$dir/.git" ]]; then
            echo "Removing likely generated directory: $dir"
            remove_directory "$dir"
        fi
    fi
done

# Final system cleanup
echo ""
echo "🧹 Final Docker system cleanup..."
echo "  Current disk usage:"
docker system df 2>/dev/null || true

echo "  Running system prune..."
docker system prune -f --volumes 2>/dev/null || true

echo ""
echo "✅ Deep cleanup complete!"
echo ""
echo "Summary: Removed ALL Docker artifacts and directories related to data-eng-template testing."
echo "This includes:"
echo "  • Generated project directories"
echo "  • Docker containers and compose projects"
echo "  • Docker images (including untagged <none> images)"
echo "  • Docker volumes and networks"
echo "  • Build cache"
echo ""
echo "Final disk usage:"
docker system df 2>/dev/null || echo "Docker system df not available"