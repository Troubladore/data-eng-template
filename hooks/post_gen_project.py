import base64, os, pathlib, json, subprocess
import yaml

# Generate Fernet key and dynamic configuration
fernet_key = base64.urlsafe_b64encode(os.urandom(32)).decode()

# Create local Hydra configuration override with generated values
local_config_dir = pathlib.Path("conf/local")
local_config_dir.mkdir(parents=True, exist_ok=True)

# Generate local configuration overrides
local_config = {
    # Security and secrets (generated dynamically)
    "orchestration": {
        "fernet_key": fernet_key,  # Top-level for easy reference
        "admin_username": "admin",
        "admin_password": "admin",
        "core": {
            "security_key": fernet_key  # Direct replacement for Airflow security key
        }
    },
    
    # Project-specific overrides from cookiecutter variables
    "project": {
        "python_version": "{{cookiecutter.python_version}}",
        "airflow_version": "{{cookiecutter.airflow_version}}",  
        "postgres_version": "{{cookiecutter.postgres_version}}"
    }
}

# Write local configuration override
local_config_file = local_config_dir / "generated.yaml"
with open(local_config_file, 'w') as f:
    f.write("# @package _global_\n")
    f.write("# Generated configuration overrides - DO NOT EDIT MANUALLY\n")
    f.write("# This file is recreated each time the template is generated\n\n")
    yaml.dump(local_config, f, default_flow_style=False, sort_keys=False)

# Create environment export script for Docker Compose integration
env_script_content = '''#!/bin/bash
# Export environment variables from Hydra configuration for Docker Compose
# This script bridges Hydra configs to Docker Compose environment variables

set -euo pipefail

# Change to project root directory  
cd "$(dirname "$0")"

# Use Python to extract environment variables from Hydra config
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')

try:
    from {{cookiecutter.repo_slug.replace('-', '_')}}.config import get_settings
    
    # Load configuration
    settings = get_settings()
    
    # Export key environment variables for Docker Compose
    print(f"export AIRFLOW__CORE__FERNET_KEY='{settings.orchestration.fernet_key}'")
    print(f"export AIRFLOW__CORE__EXECUTOR='{settings.orchestration.executor}'")  
    print(f"export AIRFLOW__CORE__LOAD_EXAMPLES='False'")
    print(f"export _AIRFLOW_WWW_USER_USERNAME='{settings.orchestration.admin_username}'")
    print(f"export _AIRFLOW_WWW_USER_PASSWORD='{settings.orchestration.admin_password}'")
    
    print(f"export POSTGRES_DB='{settings.database.name}'")
    print(f"export POSTGRES_USER='{settings.database.user}'")  
    print(f"export POSTGRES_PASSWORD='{settings.database.password}'")
    print(f"export POSTGRES_VERSION='{settings.project.postgres_version}'")
    
    print(f"export PYTHON_VERSION='{settings.project.python_version}'")
    print(f"export AIRFLOW_VERSION='{settings.project.airflow_version}'")
    
    # Optional: Export all DATA_ENG_ prefixed environment variables
    print("# Additional Hydra-managed environment variables")
    print(f"export DATA_ENG_ENVIRONMENT='{settings.transformations.target}'")
    
except ImportError as e:
    print("# Warning: Could not import Hydra configuration. Using fallback defaults.")
    print("# Run 'uv sync' to install dependencies, then restart DevContainer.")
    
    # Fallback environment variables (minimal for container startup)
    import base64, os
    fallback_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
    print(f"export AIRFLOW__CORE__FERNET_KEY='{fallback_key}'")
    print("export AIRFLOW__CORE__EXECUTOR='LocalExecutor'")
    print("export _AIRFLOW_WWW_USER_USERNAME='admin'")
    print("export _AIRFLOW_WWW_USER_PASSWORD='admin'")
    print("export POSTGRES_DB='airflow'") 
    print("export POSTGRES_USER='airflow'")
    print("export POSTGRES_PASSWORD='airflow'")
    print("export AIRFLOW_VERSION='{{cookiecutter.airflow_version}}'")
    print("export PYTHON_VERSION='{{cookiecutter.python_version}}'")
    print("export POSTGRES_VERSION='{{cookiecutter.postgres_version}}'")
    
EOF
'''

env_script_path = pathlib.Path("scripts/export_env.sh")
env_script_path.parent.mkdir(exist_ok=True)
env_script_path.write_text(env_script_content)
env_script_path.chmod(0o755)  # Make executable

# Create Docker Compose .env file for variable substitution
# This ensures environment variables are available when services start
compose_env_content = f"""# Docker Compose environment variables
# Generated automatically by cookiecutter hook - do not edit manually

# Airflow configuration
AIRFLOW__CORE__FERNET_KEY={fernet_key}
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__LOAD_EXAMPLES=False

# Airflow admin user
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=admin

# Database configuration  
POSTGRES_DB={{cookiecutter.db_name}}
POSTGRES_USER={{cookiecutter.db_user}}
POSTGRES_PASSWORD={{cookiecutter.db_password}}

# Version configuration from cookiecutter
PYTHON_VERSION={{cookiecutter.python_version}}
AIRFLOW_VERSION={{cookiecutter.airflow_version}}
POSTGRES_VERSION={{cookiecutter.postgres_version}}
"""

# Create .devcontainer/.env file
devcontainer_dir = pathlib.Path(".devcontainer")
devcontainer_env_file = devcontainer_dir / ".env"
devcontainer_env_file.write_text(compose_env_content)

# Update .devcontainer/airflow.env file with admin credentials
airflow_env_file = devcontainer_dir / "airflow.env"
if airflow_env_file.exists():
    airflow_env_content = airflow_env_file.read_text()
    
    # Check if admin credentials are already present
    if "_AIRFLOW_WWW_USER_USERNAME" not in airflow_env_content:
        # Append admin credentials to existing airflow.env content
        airflow_env_content += "_AIRFLOW_WWW_USER_USERNAME=admin\n"
        airflow_env_content += "_AIRFLOW_WWW_USER_PASSWORD=admin\n"
        airflow_env_file.write_text(airflow_env_content)
        print("Updated .devcontainer/airflow.env with admin credentials.")
    else:
        print("Admin credentials already present in airflow.env.")
else:
    # Create airflow.env if it doesn't exist
    airflow_env_content = """AIRFLOW_UID=50000
AIRFLOW_GID=0
PIP_USER=false
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=admin
"""
    airflow_env_file.write_text(airflow_env_content)
    print("Created .devcontainer/airflow.env with admin credentials.")

# Update services.yaml with generated values (cookiecutter vars already resolved)
services_config_path = pathlib.Path(".devcontainer/services.yaml")
if services_config_path.exists():
    services_content = services_config_path.read_text()
    
    # Replace placeholders with generated values
    services_content = services_content.replace("PLACEHOLDER_AIRFLOW_FERNET_KEY", fernet_key)
    services_content = services_content.replace("PLACEHOLDER_AIRFLOW_WEB_USER", "admin")
    services_content = services_content.replace("PLACEHOLDER_AIRFLOW_WEB_PASSWORD", "admin")
    
    services_config_path.write_text(services_content)

print("Generated Hydra configuration with Fernet key.")
print("Created environment export script: scripts/export_env.sh") 
print("Created Docker Compose .env file: .devcontainer/.env")
print("Updated DevContainer services configuration with generated values.")

# uv.lock will be created when users run `uv sync`

# Initialize git repository with professional defaults
try:
    # Check if git is available
    subprocess.run(["git", "--version"], check=True, capture_output=True)
    
    # Initialize git repo
    subprocess.run(["git", "init"], check=True, capture_output=True)
    
    # Check for basic git config and warn if missing
    try:
        subprocess.run(["git", "config", "user.name"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Warning: git user.name not configured. Run: git config --global user.name 'Your Name'")
        
    try:
        subprocess.run(["git", "config", "user.email"], check=True, capture_output=True) 
    except subprocess.CalledProcessError:
        print("Warning: git user.email not configured. Run: git config --global user.email 'you@example.com'")
    
    # Set default branch
    subprocess.run(["git", "config", "init.defaultBranch", "main"], capture_output=True)
    
    # Add initial commit
    subprocess.run(["git", "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit from data-eng-template"], check=True, capture_output=True)
    
    print("Initialized git repository with initial commit.")
    
except (subprocess.CalledProcessError, FileNotFoundError) as e:
    print(f"Warning: git initialization failed: {e}")
