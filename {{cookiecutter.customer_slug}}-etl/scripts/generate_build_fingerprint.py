#!/usr/bin/env python3
"""
Generate build fingerprint for Docker image caching optimization.

This script creates a deterministic fingerprint based on build configuration,
enabling shared Docker image caching across projects with identical configurations.
Inspired by DCSM fingerprinting system.
"""

import hashlib
import json
import re
from pathlib import Path
from typing import Dict, Any


def _normalize_pyproject(content: str) -> str:
    """Normalize pyproject.toml by removing customer-specific fields for fingerprinting."""
    # Replace customer-specific name with placeholder
    content = re.sub(r'name = "[^"]*"', 'name = "NORMALIZED_PROJECT"', content)

    # Remove description which might contain customer names
    content = re.sub(r'description = "[^"]*"', 'description = "NORMALIZED_DESCRIPTION"', content)

    return content


def _normalize_dockerfile(content: str) -> str:
    """Normalize Dockerfile content by removing customer-specific references."""
    # Remove customer-specific project references but keep structural content
    # This preserves actual build instructions while normalizing project names
    content = re.sub(r'customer-[a-zA-Z0-9-]+', 'NORMALIZED_CUSTOMER', content)
    content = re.sub(r'{{cookiecutter\.customer_slug}}', 'NORMALIZED_CUSTOMER', content)
    content = re.sub(r'{{cookiecutter\.project_slug}}', 'NORMALIZED_PROJECT', content)

    return content


def generate_build_fingerprint(project_root: Path) -> str:
    """
    Generate deterministic build fingerprint for Docker image caching.
    
    Fingerprint includes:
    - Airflow version
    - Python version  
    - pyproject.toml content
    - requirements.txt content
    - Dockerfile content
    - Build environment configuration
    
    Returns:
        8-character hexadecimal fingerprint
    """
    fingerprint_data = {}
    
    # Core version configuration - read from generated cookiecutter.json or defaults
    try:
        import json
        cookiecutter_file = project_root / "cookiecutter.json"
        if cookiecutter_file.exists():
            cookiecutter_config = json.loads(cookiecutter_file.read_text())
            fingerprint_data['airflow_version'] = cookiecutter_config.get('airflow_version', '2.8.0')
            fingerprint_data['python_version'] = cookiecutter_config.get('python_version', '3.12')
            fingerprint_data['postgres_version'] = cookiecutter_config.get('postgres_version', '16')
        else:
            # Fallback defaults for generated projects
            fingerprint_data['airflow_version'] = '2.8.0'
            fingerprint_data['python_version'] = '3.12'
            fingerprint_data['postgres_version'] = '16'
    except Exception:
        # Fallback defaults if config reading fails
        fingerprint_data['airflow_version'] = '2.8.0'
        fingerprint_data['python_version'] = '3.12'
        fingerprint_data['postgres_version'] = '16'
    
    # Build configuration files (customer-agnostic content only)
    build_files = {
        'airflow/requirements.txt': lambda content: content,  # Include as-is
        'Dockerfile.airflow': lambda content: _normalize_dockerfile(content),  # Normalize customer references
        'pyproject.toml': lambda content: _normalize_pyproject(content)  # Normalize customer-specific fields
    }

    for file_path, normalizer in build_files.items():
        full_path = project_root / file_path
        if full_path.exists():
            content = full_path.read_text().strip()
            fingerprint_data[file_path] = normalizer(content)
        else:
            fingerprint_data[file_path] = ""
    
    # Serialize and hash
    fingerprint_json = json.dumps(fingerprint_data, sort_keys=True)
    fingerprint_hash = hashlib.sha256(fingerprint_json.encode()).hexdigest()
    
    # Debug: Print what's being hashed (remove in production)
    print(f"DEBUG - Fingerprint data: {fingerprint_json[:200]}...")
    
    return fingerprint_hash[:8]


def generate_image_name(fingerprint: str, project_root: Path) -> str:
    """Generate standardized image name with fingerprint."""
    try:
        import json
        cookiecutter_file = project_root / "cookiecutter.json"
        if cookiecutter_file.exists():
            cookiecutter_config = json.loads(cookiecutter_file.read_text())
            airflow_version = cookiecutter_config.get('airflow_version', '2.8.0')
            python_version = cookiecutter_config.get('python_version', '3.12')
        else:
            # Fallback defaults for generated projects
            airflow_version = '2.8.0'
            python_version = '3.12'
    except Exception:
        # Fallback defaults if config reading fails
        airflow_version = '2.8.0'
        python_version = '3.12'

    return f"data-eng-airflow-dev:{airflow_version}-py{python_version}-{fingerprint}"


def main():
    """Generate and display build fingerprint."""
    project_root = Path(__file__).parent.parent
    fingerprint = generate_build_fingerprint(project_root)
    image_name = generate_image_name(fingerprint, project_root)

    print(f"Build Fingerprint: {fingerprint}")
    print(f"Shared Image Name: {image_name}")

    # Write to file for Docker Compose usage
    fingerprint_file = project_root / ".devcontainer" / "build_fingerprint.txt"
    fingerprint_file.parent.mkdir(exist_ok=True)  # Ensure directory exists
    fingerprint_file.write_text(image_name)

    return fingerprint, image_name


if __name__ == "__main__":
    main()