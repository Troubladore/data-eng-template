#!/bin/bash
# Port Management Script for Organization
#
# This script helps manage port reservations across your organization's
# data engineering projects, integrating with the port registry system.

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$(dirname "$SCRIPT_DIR")"
PORT_REGISTRY_FILE="$TEMPLATE_DIR/org-standards/port-registry.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to check if port registry exists
check_port_registry() {
    if [[ ! -f "$PORT_REGISTRY_FILE" ]]; then
        echo -e "${RED}❌ Port registry not found: $PORT_REGISTRY_FILE${NC}"
        echo -e "${BLUE}💡 Run this script from your organization's cookiecutter fork${NC}"
        exit 1
    fi
}

# Function to parse YAML (simplified parser)
get_yaml_value() {
    local yaml_file="$1"
    local key="$2"

    # Simple YAML parser - handles basic key: value pairs
    grep -E "^\s*${key}:" "$yaml_file" | sed -E "s/^\s*${key}:\s*//" | sed 's/["\047]//g' | head -1
}

# Function to get reserved ports for a project
get_reserved_ports() {
    local project_slug="$1"

    # Extract reserved ports section
    sed -n '/^reserved_ports:/,/^[a-zA-Z]/p' "$PORT_REGISTRY_FILE" | \
    sed -n "/^\s\+${project_slug}:/,/^\s\+[a-zA-Z]/p" | \
    grep -E "^\s+(airflow_port|postgres_port):" || true
}

# Function to get all reserved ports
get_all_reserved_ports() {
    local type="$1"  # "airflow" or "postgres"

    sed -n '/^reserved_ports:/,/^[a-zA-Z]/p' "$PORT_REGISTRY_FILE" | \
    grep -E "^\s+${type}_port:" | \
    sed -E "s/^\s+${type}_port:\s*//" | \
    sort -n
}

# Function to get dynamic allocation pool
get_dynamic_ports() {
    local type="$1"  # "airflow" or "postgres"

    sed -n '/^dynamic_allocation:/,/^[a-zA-Z]/p' "$PORT_REGISTRY_FILE" | \
    sed -n "/${type}_ports:/,/^\s\+[a-zA-Z]/p" | \
    grep -E "^\s+available:" | \
    sed -E 's/^\s+available:\s*\[//' | \
    sed -E 's/\].*$//' | \
    tr ',' '\n' | \
    sed 's/[^0-9]//g' | \
    grep -v '^$' | \
    sort -n
}

# Function to check if a port is available
is_port_available() {
    local port="$1"
    local type="$2"  # "airflow" or "postgres"

    # Check if port is reserved
    if get_all_reserved_ports "$type" | grep -q "^${port}$"; then
        return 1  # Port is reserved
    fi

    # Check if port is in use (via netstat/ss)
    if command -v netstat >/dev/null 2>&1; then
        if netstat -tuln 2>/dev/null | grep -q ":${port}\s"; then
            return 1  # Port is in use
        fi
    elif command -v ss >/dev/null 2>&1; then
        if ss -tuln 2>/dev/null | grep -q ":${port}\s"; then
            return 1  # Port is in use
        fi
    fi

    return 0  # Port is available
}

# Function to suggest available port
suggest_port() {
    local type="$1"  # "airflow" or "postgres"
    local project_type="${2:-dynamic}"  # "permanent" or "dynamic"

    if [[ "$project_type" == "dynamic" ]]; then
        # Use dynamic allocation pool
        local available_ports
        mapfile -t available_ports < <(get_dynamic_ports "$type")

        for port in "${available_ports[@]}"; do
            if [[ -n "$port" ]] && is_port_available "$port" "$type"; then
                echo "$port"
                return 0
            fi
        done
    fi

    # Fallback: suggest from range
    local range_start range_end
    if [[ "$type" == "airflow" ]]; then
        range_start=8100
        range_end=8199
    else
        range_start=5500
        range_end=5599
    fi

    for ((port=range_start; port<=range_end; port++)); do
        if is_port_available "$port" "$type"; then
            echo "$port"
            return 0
        fi
    done

    echo "No available ports found" >&2
    return 1
}

# Function to show port status
show_port_status() {
    echo -e "${CYAN}🔍 Organization Port Status${NC}"
    echo

    echo -e "${BLUE}📋 Reserved Ports:${NC}"

    # Parse reserved ports
    local in_reserved=false
    local current_project=""

    while IFS= read -r line; do
        if [[ "$line" =~ ^reserved_ports: ]]; then
            in_reserved=true
            continue
        elif [[ "$line" =~ ^[a-zA-Z] ]] && [[ "$in_reserved" == true ]]; then
            break
        elif [[ "$in_reserved" == true ]]; then
            if [[ "$line" =~ ^[[:space:]]+([a-zA-Z0-9-]+): ]]; then
                current_project="${BASH_REMATCH[1]}"
                echo -e "  📦 ${GREEN}$current_project${NC}"
            elif [[ "$line" =~ ^[[:space:]]+airflow_port:[[:space:]]*([0-9]+) ]]; then
                echo -e "    🌐 Airflow: ${YELLOW}${BASH_REMATCH[1]}${NC}"
            elif [[ "$line" =~ ^[[:space:]]+postgres_port:[[:space:]]*([0-9]+) ]]; then
                echo -e "    🗄️  PostgreSQL: ${YELLOW}${BASH_REMATCH[1]}${NC}"
            elif [[ "$line" =~ ^[[:space:]]+owner:[[:space:]]*\"([^\"]+)\" ]]; then
                echo -e "    👥 Owner: ${BASH_REMATCH[1]}"
            elif [[ "$line" =~ ^[[:space:]]+description:[[:space:]]*\"([^\"]+)\" ]]; then
                echo -e "    📝 ${BASH_REMATCH[1]}"
                echo
            fi
        fi
    done < "$PORT_REGISTRY_FILE"

    echo -e "${BLUE}🎯 Next Available Ports:${NC}"
    local next_airflow next_postgres
    if next_airflow=$(suggest_port "airflow" "dynamic"); then
        echo -e "  🌐 Airflow: ${GREEN}$next_airflow${NC}"
    else
        echo -e "  🌐 Airflow: ${RED}No available ports${NC}"
    fi

    if next_postgres=$(suggest_port "postgres" "dynamic"); then
        echo -e "  🗄️  PostgreSQL: ${GREEN}$next_postgres${NC}"
    else
        echo -e "  🗄️  PostgreSQL: ${RED}No available ports${NC}"
    fi
}

# Function to reserve ports for a project
reserve_ports() {
    local project_slug="$1"
    local airflow_port="$2"
    local postgres_port="$3"
    local owner="$4"
    local description="$5"

    echo -e "${BLUE}🔒 Reserving ports for project: $project_slug${NC}"

    # Validate ports are available
    if ! is_port_available "$airflow_port" "airflow"; then
        echo -e "${RED}❌ Airflow port $airflow_port is not available${NC}"
        return 1
    fi

    if ! is_port_available "$postgres_port" "postgres"; then
        echo -e "${RED}❌ PostgreSQL port $postgres_port is not available${NC}"
        return 1
    fi

    # Create backup
    cp "$PORT_REGISTRY_FILE" "${PORT_REGISTRY_FILE}.backup"

    # Add reservation (simplified - in production use proper YAML editor)
    local today=$(date +%Y-%m-%d)

    echo -e "\n  $project_slug:" >> "$PORT_REGISTRY_FILE"
    echo -e "    airflow_port: $airflow_port" >> "$PORT_REGISTRY_FILE"
    echo -e "    postgres_port: $postgres_port" >> "$PORT_REGISTRY_FILE"
    echo -e "    owner: \"$owner\"" >> "$PORT_REGISTRY_FILE"
    echo -e "    description: \"$description\"" >> "$PORT_REGISTRY_FILE"
    echo -e "    created: \"$today\"" >> "$PORT_REGISTRY_FILE"

    echo -e "${GREEN}✅ Ports reserved successfully${NC}"
    echo -e "${YELLOW}⚠️  Remember to commit this change to version control!${NC}"

    # Show what was added
    echo
    echo -e "${BLUE}📋 Reserved:${NC}"
    echo -e "  📦 Project: $project_slug"
    echo -e "  🌐 Airflow: $airflow_port"
    echo -e "  🗄️  PostgreSQL: $postgres_port"
    echo -e "  👥 Owner: $owner"
}

# Function to show usage
show_usage() {
    cat << EOF
${CYAN}Port Management Script${NC}

${YELLOW}USAGE:${NC}
  $0 status                     # Show current port allocations
  $0 suggest <project-type>     # Suggest available ports (permanent|dynamic)
  $0 reserve <project> <owner> <description>  # Reserve ports for project
  $0 check <project>           # Check if project has reserved ports

${YELLOW}EXAMPLES:${NC}
  $0 status
  $0 suggest dynamic
  $0 reserve customer-analytics "analytics-team" "Customer analytics pipeline"
  $0 check fraud-detection

${YELLOW}PORT RANGES:${NC}
  Airflow:    8100-8199 (development)
  PostgreSQL: 5500-5599 (development)
  Testing:    8200-8299 (CI/testing)
  Monitoring: 9100-9199 (metrics)

${YELLOW}WORKFLOW:${NC}
  1. Check status to see current allocations
  2. For permanent projects: reserve ports via this script + commit PR
  3. For temporary projects: use dynamic allocation (automatic)
  4. Update port registry monthly to clean up unused reservations
EOF
}

# Main script logic
main() {
    check_port_registry

    case "${1:-}" in
        "status")
            show_port_status
            ;;
        "suggest")
            local project_type="${2:-dynamic}"
            echo -e "${BLUE}🎯 Suggested ports for $project_type project:${NC}"
            local airflow_port postgres_port
            if airflow_port=$(suggest_port "airflow" "$project_type"); then
                echo -e "  🌐 Airflow: ${GREEN}$airflow_port${NC}"
            fi
            if postgres_port=$(suggest_port "postgres" "$project_type"); then
                echo -e "  🗄️  PostgreSQL: ${GREEN}$postgres_port${NC}"
            fi
            ;;
        "reserve")
            if [[ $# -lt 4 ]]; then
                echo -e "${RED}❌ Usage: $0 reserve <project> <owner> <description>${NC}"
                exit 1
            fi

            local project="$2"
            local owner="$3"
            local description="$4"

            # Suggest ports
            local airflow_port postgres_port
            airflow_port=$(suggest_port "airflow" "permanent")
            postgres_port=$(suggest_port "postgres" "permanent")

            if [[ -z "$airflow_port" ]] || [[ -z "$postgres_port" ]]; then
                echo -e "${RED}❌ Unable to find available ports${NC}"
                exit 1
            fi

            reserve_ports "$project" "$airflow_port" "$postgres_port" "$owner" "$description"
            ;;
        "check")
            local project="${2:-}"
            if [[ -z "$project" ]]; then
                echo -e "${RED}❌ Usage: $0 check <project>${NC}"
                exit 1
            fi

            local reserved_info
            reserved_info=$(get_reserved_ports "$project")

            if [[ -n "$reserved_info" ]]; then
                echo -e "${GREEN}✅ Project '$project' has reserved ports:${NC}"
                echo "$reserved_info" | sed 's/^/  /'
            else
                echo -e "${YELLOW}⚠️  Project '$project' has no reserved ports (will use dynamic allocation)${NC}"
            fi
            ;;
        *)
            show_usage
            ;;
    esac
}

main "$@"