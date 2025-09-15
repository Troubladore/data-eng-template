#!/bin/bash
# Intelligent Project Generation with Port Management
#
# This script wraps cookiecutter generation with organization port management,
# automatically handling port reservations and assignments.

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$(dirname "$SCRIPT_DIR")"
PORT_REGISTRY_FILE="$TEMPLATE_DIR/org-standards/port-registry.yaml"
MANAGE_PORTS_SCRIPT="$SCRIPT_DIR/manage-ports.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to check prerequisites
check_prerequisites() {
    if ! command -v cookiecutter >/dev/null 2>&1; then
        echo -e "${RED}❌ cookiecutter not found. Install with: pipx install cookiecutter${NC}"
        exit 1
    fi

    if [[ ! -f "$MANAGE_PORTS_SCRIPT" ]]; then
        echo -e "${RED}❌ Port management script not found: $MANAGE_PORTS_SCRIPT${NC}"
        exit 1
    fi
}

# Function to determine if project should have reserved ports
determine_project_type() {
    local customer_slug="$1"

    echo -e "${BLUE}🤔 Project Classification${NC}"
    echo

    cat << EOF
${YELLOW}Project Types:${NC}
  ${GREEN}1. Permanent${NC} - Long-running, production-bound, shared projects
     • Expected lifetime > 6 months
     • Used by multiple team members
     • Production deployment planned
     • Gets reserved, predictable ports

  ${GREEN}2. Temporary${NC} - Development, testing, short-term projects
     • Personal development projects
     • Proof of concepts
     • Expected lifetime < 6 months
     • Gets dynamic port allocation

EOF

    read -p "$(echo -e "${CYAN}Is this a permanent project? (y/N): ${NC}")" -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "permanent"
    else
        echo "temporary"
    fi
}

# Function to reserve ports for permanent project
reserve_permanent_ports() {
    local customer_slug="$1"

    echo -e "${BLUE}📋 Port Reservation for Permanent Project${NC}"
    echo

    # Get project details
    read -p "$(echo -e "${CYAN}Project owner (team/person): ${NC}")" owner
    read -p "$(echo -e "${CYAN}Project description: ${NC}")" description

    # Check if already reserved
    if "$MANAGE_PORTS_SCRIPT" check "$customer_slug" >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Project already has reserved ports${NC}"
        "$MANAGE_PORTS_SCRIPT" check "$customer_slug"
        return 0
    fi

    # Reserve ports
    echo -e "${BLUE}🔒 Reserving ports...${NC}"
    if "$MANAGE_PORTS_SCRIPT" reserve "$customer_slug" "$owner" "$description"; then
        echo
        echo -e "${GREEN}✅ Ports reserved successfully${NC}"
        echo -e "${YELLOW}⚠️  IMPORTANT: Commit port-registry.yaml to version control!${NC}"
        echo
        echo -e "${BLUE}💡 Run this command to commit the reservation:${NC}"
        echo -e "${CYAN}git add org-standards/port-registry.yaml && git commit -m \"Reserve ports for $customer_slug project\"${NC}"
        echo

        # Wait for user to commit
        read -p "$(echo -e "${CYAN}Press Enter after committing the port reservation...${NC}")"

        return 0
    else
        echo -e "${RED}❌ Failed to reserve ports${NC}"
        return 1
    fi
}

# Function to generate project with appropriate port configuration
generate_project() {
    local customer_slug="$1"
    local project_type="$2"
    local config_file="${3:-}"

    # Set up environment variables for port configuration
    if [[ "$project_type" == "permanent" ]]; then
        # Get reserved ports
        local port_info
        port_info=$("$MANAGE_PORTS_SCRIPT" check "$customer_slug" 2>/dev/null || true)

        if [[ -n "$port_info" ]]; then
            # Extract ports from output
            local airflow_port postgres_port
            airflow_port=$(echo "$port_info" | grep "airflow_port:" | sed 's/.*airflow_port: *//')
            postgres_port=$(echo "$port_info" | grep "postgres_port:" | sed 's/.*postgres_port: *//')

            if [[ -n "$airflow_port" ]] && [[ -n "$postgres_port" ]]; then
                export AIRFLOW_PORT="$airflow_port"
                export POSTGRES_PORT="$postgres_port"

                echo -e "${GREEN}🔒 Using reserved ports:${NC}"
                echo -e "  🌐 Airflow: $airflow_port"
                echo -e "  🗄️  PostgreSQL: $postgres_port"
                echo
            fi
        fi
    else
        echo -e "${BLUE}🎲 Using dynamic port allocation${NC}"
        echo -e "  Ports will be assigned automatically by Docker"
        echo
    fi

    # Run cookiecutter
    echo -e "${BLUE}🚀 Generating project...${NC}"

    local cookiecutter_cmd="cookiecutter ."
    if [[ -n "$config_file" ]]; then
        cookiecutter_cmd="$cookiecutter_cmd --config-file $config_file"
    fi

    # Execute cookiecutter in template directory
    cd "$TEMPLATE_DIR"
    eval "$cookiecutter_cmd"

    echo -e "${GREEN}✅ Project generated successfully${NC}"
}

# Function to post-generation instructions
show_post_generation_instructions() {
    local project_type="$1"
    local customer_slug="$2"

    echo
    echo -e "${CYAN}🎉 Next Steps:${NC}"

    if [[ "$project_type" == "permanent" ]]; then
        echo -e "1. ${GREEN}cd ${customer_slug}-etl/${NC}"
        echo -e "2. ${GREEN}code .${NC} (open in VS Code DevContainer)"
        echo -e "3. Services will start on your reserved ports"
        echo -e "4. Access Airflow at your dedicated URL (see port registry)"
    else
        echo -e "1. ${GREEN}cd ${customer_slug}-etl/${NC}"
        echo -e "2. ${GREEN}code .${NC} (open in VS Code DevContainer)"
        echo -e "3. Run ${GREEN}./scripts/get-ports.sh${NC} to discover assigned ports"
        echo -e "4. Access services at dynamically assigned URLs"
    fi

    echo
    echo -e "${BLUE}📚 Additional Resources:${NC}"
    echo -e "• Port management: ${GREEN}./scripts/manage-ports.sh status${NC}"
    echo -e "• Development guide: ${GREEN}docs/getting-started.md${NC}"
    echo -e "• Configuration options: ${GREEN}docs/template-configuration.md${NC}"
}

# Function to show usage
show_usage() {
    cat << EOF
${CYAN}Intelligent Project Generation Script${NC}

${YELLOW}USAGE:${NC}
  $0 [--config-file FILE]

${YELLOW}OPTIONS:${NC}
  --config-file FILE    Use custom cookiecutter configuration file
                        (default: company-template-defaults.yaml if exists)

${YELLOW}WORKFLOW:${NC}
  1. Determines if project should be permanent or temporary
  2. For permanent projects: reserves ports in organization registry
  3. Generates project with appropriate port configuration
  4. Provides next steps for development

${YELLOW}EXAMPLES:${NC}
  $0                                    # Interactive generation
  $0 --config-file acme-defaults.yaml  # Use custom config

${YELLOW}PORT MANAGEMENT:${NC}
  • Permanent projects get reserved, predictable ports
  • Temporary projects get dynamic allocation
  • All ports tracked in org-standards/port-registry.yaml
  • Port conflicts automatically avoided

${YELLOW}REQUIREMENTS:${NC}
  • cookiecutter installed (pipx install cookiecutter)
  • Must run from organization's cookiecutter fork
  • Port registry file must exist (org-standards/port-registry.yaml)
EOF
}

# Main script logic
main() {
    local config_file=""

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --config-file)
                config_file="$2"
                shift 2
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Unknown option: $1${NC}"
                show_usage
                exit 1
                ;;
        esac
    done

    # Use default config file if exists and none specified
    if [[ -z "$config_file" ]] && [[ -f "$TEMPLATE_DIR/your-org-defaults.yaml" ]]; then
        config_file="your-org-defaults.yaml"
        echo -e "${BLUE}💡 Using organization defaults: $config_file${NC}"
    fi

    check_prerequisites

    echo -e "${CYAN}🏗️  Intelligent Project Generation${NC}"
    echo

    # Get customer_slug first to determine project type
    echo -e "${BLUE}📝 Project Information${NC}"
    read -p "$(echo -e "${CYAN}Customer/Project slug (kebab-case): ${NC}")" customer_slug

    # Validate slug format
    if [[ ! "$customer_slug" =~ ^[a-z0-9-]+$ ]]; then
        echo -e "${RED}❌ Invalid slug format. Use lowercase letters, numbers, and hyphens only.${NC}"
        exit 1
    fi

    # Determine project type
    local project_type
    project_type=$(determine_project_type "$customer_slug")

    # Handle port reservation for permanent projects
    if [[ "$project_type" == "permanent" ]]; then
        if ! reserve_permanent_ports "$customer_slug"; then
            echo -e "${RED}❌ Cannot proceed without port reservation${NC}"
            exit 1
        fi
    fi

    # Generate project
    if generate_project "$customer_slug" "$project_type" "$config_file"; then
        show_post_generation_instructions "$project_type" "$customer_slug"
    else
        echo -e "${RED}❌ Project generation failed${NC}"
        exit 1
    fi
}

main "$@"