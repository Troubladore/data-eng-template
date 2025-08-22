"""Unit tests for cookiecutter configuration validation."""

import json
from pathlib import Path
from typing import Any, Dict
import pytest


class TestCookiecutterConfig:
    """Test cookiecutter.json configuration file."""
    
    def test_cookiecutter_json_exists(self, template_dir: Path):
        """Test that cookiecutter.json exists."""
        config_file = template_dir / "cookiecutter.json"
        assert config_file.exists(), "cookiecutter.json must exist"
        assert config_file.is_file(), "cookiecutter.json must be a file"
    
    def test_cookiecutter_json_valid_syntax(self, template_dir: Path):
        """Test that cookiecutter.json has valid JSON syntax."""
        config_file = template_dir / "cookiecutter.json"
        
        with open(config_file) as f:
            try:
                json.load(f)
            except json.JSONDecodeError as e:
                pytest.fail(f"cookiecutter.json has invalid JSON syntax: {e}")
    
    def test_required_variables_present(self, template_dir: Path):
        """Test that all required variables are present."""
        config_file = template_dir / "cookiecutter.json"
        
        with open(config_file) as f:
            config = json.load(f)
        
        required_variables = [
            "project_name",
            "repo_slug", 
            "author_name",
            "python_version",
            "airflow_version",
            "postgres_version",
            "airflow_executor",
            "db_name",
            "db_user", 
            "db_password",
            "license"
        ]
        
        for var in required_variables:
            assert var in config, f"Required variable '{var}' missing from cookiecutter.json"
    
    def test_variable_types(self, template_dir: Path):
        """Test that variables have appropriate types."""
        config_file = template_dir / "cookiecutter.json"
        
        with open(config_file) as f:
            config = json.load(f)
        
        # String variables
        string_vars = ["project_name", "repo_slug", "author_name", "python_version", 
                      "airflow_version", "postgres_version", "db_name", "db_user", "db_password"]
        
        for var in string_vars:
            if var in config:
                assert isinstance(config[var], str), f"Variable '{var}' should be a string"
        
        # Choice variables (lists)
        choice_vars = ["airflow_executor", "license"]
        
        for var in choice_vars:
            if var in config:
                assert isinstance(config[var], list), f"Variable '{var}' should be a list of choices"
                assert len(config[var]) > 0, f"Variable '{var}' should have at least one choice"
    
    def test_default_values_reasonable(self, template_dir: Path):
        """Test that default values are reasonable."""
        config_file = template_dir / "cookiecutter.json"
        
        with open(config_file) as f:
            config = json.load(f)
        
        # Project name should be descriptive
        assert len(config["project_name"]) > 3, "Project name should be descriptive"
        
        # Repo slug should be URL-safe
        repo_slug = config["repo_slug"] 
        assert "-" in repo_slug or "_" not in repo_slug, "Repo slug should use hyphens"
        
        # Python version should be modern
        python_version = config["python_version"]
        major, minor = python_version.split(".")[:2]
        assert int(major) == 3, "Should use Python 3"
        assert int(minor) >= 11, "Should use Python 3.11 or newer"
        
        # Airflow executor choices should be valid
        airflow_executors = config["airflow_executor"]
        valid_executors = ["LocalExecutor", "SequentialExecutor", "CeleryExecutor"]
        for executor in airflow_executors:
            assert executor in valid_executors, f"Invalid Airflow executor: {executor}"
    
    def test_computed_variables_syntax(self, template_dir: Path):
        """Test computed variables have correct Jinja syntax."""
        config_file = template_dir / "cookiecutter.json"
        
        with open(config_file) as f:
            config = json.load(f)
        
        # db_name should be computed from repo_slug
        if "db_name" in config and "{{" in str(config["db_name"]):
            db_name_template = config["db_name"]
            assert "cookiecutter.repo_slug" in db_name_template
            assert "replace('-', '_')" in db_name_template


class TestCookiecutterVariableInteractions:
    """Test interactions between cookiecutter variables."""
    
    @pytest.mark.parametrize("test_config", [
        {"repo_slug": "my-project", "expected_db": "my_project"},
        {"repo_slug": "multi-word-project", "expected_db": "multi_word_project"},
        {"repo_slug": "simple", "expected_db": "simple"}
    ])
    def test_db_name_computation(self, test_config: Dict[str, Any]):
        """Test that db_name is correctly computed from repo_slug."""
        repo_slug = test_config["repo_slug"]
        expected_db = test_config["expected_db"]
        
        # Simulate the Jinja computation
        computed_db = repo_slug.replace('-', '_')
        assert computed_db == expected_db
    
    def test_version_compatibility(self, template_dir: Path):
        """Test that specified versions are compatible."""
        config_file = template_dir / "cookiecutter.json"
        
        with open(config_file) as f:
            config = json.load(f)
        
        # Check Python and Airflow compatibility
        python_version = config["python_version"]
        airflow_version = config["airflow_version"]
        
        # Airflow 2.9+ requires Python 3.8+
        if airflow_version.startswith("2.9"):
            python_major, python_minor = python_version.split(".")[:2]
            assert int(python_major) >= 3
            assert int(python_minor) >= 8
    
    def test_executor_environment_compatibility(self, template_dir: Path):
        """Test executor choices are appropriate for development."""
        config_file = template_dir / "cookiecutter.json"
        
        with open(config_file) as f:
            config = json.load(f)
        
        airflow_executors = config["airflow_executor"]
        
        # Should include LocalExecutor for development
        assert "LocalExecutor" in airflow_executors
        
        # Should include SequentialExecutor for simplicity
        assert "SequentialExecutor" in airflow_executors