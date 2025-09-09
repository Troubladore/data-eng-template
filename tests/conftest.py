"""Test configuration and fixtures for template testing."""

import json
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
def template_dir() -> Path:
    """Path to the cookiecutter template directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def default_cookiecutter_config() -> Dict[str, Any]:
    """Default cookiecutter configuration for testing."""
    return {
        "project_name": "Test Data Project",
        "repo_slug": "test-data-project",
        "author_name": "Test Author",
        "python_version": "3.12",
        "airflow_version": "3.0.6",
        "postgres_version": "16",
        "airflow_executor": "LocalExecutor",
        "db_name": "test_data_project",
        "db_user": "postgres",
        "db_password": "postgres",
        "license": "MIT"
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
        "repo_slug": "min",
        "author_name": "A",
        "python_version": "3.12",
        "airflow_version": "3.0.6", 
        "postgres_version": "16",
        "airflow_executor": "SequentialExecutor",
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
        "repo_slug": "enterprise-data-engineering-platform", 
        "author_name": "Enterprise Data Team with Special Characters & Symbols",
        "python_version": "3.12",
        "airflow_version": "3.0.6",
        "postgres_version": "16", 
        "airflow_executor": "LocalExecutor",
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