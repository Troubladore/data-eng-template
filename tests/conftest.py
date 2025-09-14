"""Test configuration and fixtures for template testing."""

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, Generator
import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create and cleanup temporary directory for test isolation."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def template_dir() -> str:
    """Path to the cookiecutter template directory or remote URL."""
    if os.getenv('PYTEST_REMOTE_BRANCH'):
        branch = os.getenv('PYTEST_REMOTE_BRANCH', 'main')
        return f"https://github.com/Troubladore/data-eng-template.git@{branch}"
    return str(Path(__file__).parent.parent)


@pytest.fixture
def default_cookiecutter_config() -> Dict[str, Any]:
    """Default cookiecutter configuration for testing."""
    return {
        "customer_slug": "test-customer",
        "project_slug": "test-customer-etl",
        "project_name": "Test Customer ETL Project",
        "author_name": "Test Author",
        "description": "Test data engineering project",
        "python_version": "3.12",
        "airflow_version": "3.0.6",
        "runtime_tag": "8.10.0",
        "image_repo": "registry.example.com/etl/test-customer",
        "postgres_version": "16",
        "env_name": "dev",
        "company_domain": "test.com",
        "local_domain": "localhost",
        "high_label": "high",
        "executor": "LocalExecutor",
        "secrets_strategy": "env-vars",
        "enable_kerberos": "no",
        "db_name": "test_customer_etl",
        "db_user": "postgres",
        "db_password": "postgres",
        "license": "MIT",
        "year": "2025"
    }


@pytest.fixture
def cookiecutter_config_file(temp_dir: Path, default_cookiecutter_config: Dict[str, Any]) -> Path:
    """Create temporary cookiecutter config file."""
    config_file = temp_dir / "cookiecutter_config.json"
    with open(config_file, 'w') as f:
        json.dump({"default_context": default_cookiecutter_config}, f, indent=2)
    return config_file


@pytest.fixture
def minimal_cookiecutter_config() -> Dict[str, Any]:
    """Minimal cookiecutter configuration for edge case testing."""
    return {
        "project_name": "Min",
        "customer_slug": "min",
        "project_slug": "min-etl",
        "author_name": "A",
        "python_version": "3.12",
        "airflow_version": "3.0.6", 
        "postgres_version": "16",
        "executor": "LocalExecutor",
        "secrets_strategy": "env-vars",
        "enable_kerberos": "no",
        "db_name": "min",
        "db_user": "postgres",
        "db_password": "postgres",
        "license": "Proprietary"
    }


@pytest.fixture  
def complex_cookiecutter_config() -> Dict[str, Any]:
    """Complex cookiecutter configuration for comprehensive testing."""
    return {
        "project_name": "Enterprise Data Engineering Platform",
        "customer_slug": "enterprise-data", 
        "project_slug": "enterprise-data-etl",
        "author_name": "Enterprise Data Team with Special Characters & Symbols",
        "python_version": "3.12",
        "airflow_version": "3.0.6",
        "postgres_version": "16", 
        "executor": "KubernetesExecutor",
        "secrets_strategy": "azure-key-vault",
        "enable_kerberos": "yes",
        "db_name": "enterprise_data_engineering_platform",
        "db_user": "enterprise_user",
        "db_password": "complex_password_123!",
        "license": "Apache-2.0"
    }


@pytest.fixture(params=["default", "minimal", "complex"])
def all_cookiecutter_configs(request, default_cookiecutter_config, minimal_cookiecutter_config, complex_cookiecutter_config):
    """Parameterized fixture to test all cookiecutter configurations."""
    configs = {
        "default": default_cookiecutter_config,
        "minimal": minimal_cookiecutter_config, 
        "complex": complex_cookiecutter_config
    }
    return configs[request.param]


@pytest.fixture
def expected_project_structure() -> list:
    """Expected directory structure for generated projects."""
    return [
        "CLAUDE.md",
        "Makefile", 
        "pyproject.toml",
        "airflow/",
        "dags/",
        "dags/CLAUDE.md",
        "dags/example_dag.py",
        "dags/example_modern_airflow.py",
        "dbt/",
        "dbt/CLAUDE.md", 
        "dbt/dbt_project.yml",
        "dbt/models/bronze/",
        "dbt/models/silver/",
        "dbt/models/gold/", 
        "docs/",
        "scripts/",
        "scripts/CLAUDE.md",
        "tests/",
        "transforms/",
        "transforms/CLAUDE.md"
    ]


@pytest.fixture
def expected_guidance_files() -> list:
    """Expected CLAUDE.md guidance files in generated project."""
    return [
        "CLAUDE.md",
        "dags/CLAUDE.md",
        "dbt/CLAUDE.md", 
        "transforms/CLAUDE.md",
        "scripts/CLAUDE.md"
    ]