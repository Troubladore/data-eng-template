"""Tests for Hydra configuration system."""

import pytest
from pathlib import Path
import tempfile
import yaml

from src.{{cookiecutter.repo_slug}}.config import get_settings, Settings


class TestHydraConfig:
    """Test Hydra configuration integration."""
    
    def test_default_config_loads(self):
        """Test that default configuration loads successfully."""
        # This test requires the conf/ directory to exist
        conf_dir = Path("conf")
        if not conf_dir.exists():
            pytest.skip("Configuration directory not found")
        
        settings = get_settings(config_dir=conf_dir)
        
        assert isinstance(settings, Settings)
        assert settings.project.name == "{{cookiecutter.project_name}}"
        assert settings.project.slug == "{{cookiecutter.repo_slug}}"
        assert settings.runtime.log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]
    
    def test_environment_override(self):
        """Test environment-specific configuration loading."""
        conf_dir = Path("conf")
        if not conf_dir.exists():
            pytest.skip("Configuration directory not found")
        
        # Load production environment
        settings = get_settings(config_dir=conf_dir, environment="prod")
        
        assert settings.transformations.target == "prod"
        assert settings.runtime.log_level == "INFO"  # Production should be less verbose
        assert not settings.runtime.debug_mode  # Debug disabled in production
    
    def test_command_line_overrides(self):
        """Test command-line configuration overrides."""
        conf_dir = Path("conf")
        if not conf_dir.exists():
            pytest.skip("Configuration directory not found")
        
        # Override specific settings
        settings = get_settings(
            config_dir=conf_dir,
            overrides=["runtime.parallel_jobs=8", "database.port=5433"]
        )
        
        assert settings.runtime.parallel_jobs == 8
        assert settings.database.port == 5433
    
    def test_database_connection_url(self):
        """Test database connection URL generation."""
        conf_dir = Path("conf")
        if not conf_dir.exists():
            pytest.skip("Configuration directory not found")
        
        settings = get_settings(config_dir=conf_dir)
        
        url = settings.database.connection_url
        assert url.startswith("postgresql://")
        assert settings.database.host in url
        assert str(settings.database.port) in url
        assert settings.database.name in url
    
    def test_settings_validation(self):
        """Test Pydantic validation of settings."""
        conf_dir = Path("conf")
        if not conf_dir.exists():
            pytest.skip("Configuration directory not found")
        
        settings = get_settings(config_dir=conf_dir)
        
        # Test type validation
        assert isinstance(settings.runtime.parallel_jobs, int)
        assert isinstance(settings.runtime.debug_mode, bool)
        assert isinstance(settings.database.port, int)
        
        # Test value constraints
        assert settings.runtime.parallel_jobs > 0
        assert settings.database.port > 0
    
    def test_environment_variable_overrides(self, monkeypatch):
        """Test environment variable configuration overrides."""
        conf_dir = Path("conf")
        if not conf_dir.exists():
            pytest.skip("Configuration directory not found")
        
        # Set environment variables
        monkeypatch.setenv("DATA_ENG_DATABASE_HOST", "test-host")
        monkeypatch.setenv("DATA_ENG_RUNTIME_DEBUG_MODE", "true")
        
        settings = get_settings(config_dir=conf_dir)
        
        assert settings.database.host == "test-host"
        assert settings.runtime.debug_mode is True


class TestConfigurationIntegrity:
    """Test configuration file integrity and consistency."""
    
    def test_config_files_exist(self):
        """Test that required configuration files exist."""
        conf_dir = Path("conf")
        if not conf_dir.exists():
            pytest.skip("Configuration directory not found")
        
        required_files = [
            "config.yaml",
            "environment/dev.yaml", 
            "environment/prod.yaml",
            "database/postgres_local.yaml",
            "orchestration/airflow_local.yaml",
            "transformations/dbt_dev.yaml",
            "compute/local.yaml"
        ]
        
        for file_path in required_files:
            full_path = conf_dir / file_path
            assert full_path.exists(), f"Required config file missing: {file_path}"
    
    def test_yaml_syntax_valid(self):
        """Test that all YAML files have valid syntax."""
        conf_dir = Path("conf")
        if not conf_dir.exists():
            pytest.skip("Configuration directory not found")
        
        yaml_files = list(conf_dir.rglob("*.yaml"))
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file) as f:
                    yaml.safe_load(f)
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML syntax in {yaml_file}: {e}")
    
    def test_config_completeness(self):
        """Test that configurations have required sections."""
        conf_dir = Path("conf")
        if not conf_dir.exists():
            pytest.skip("Configuration directory not found")
        
        settings = get_settings(config_dir=conf_dir)
        
        # Verify all required sections exist
        assert hasattr(settings, 'project')
        assert hasattr(settings, 'runtime')
        assert hasattr(settings, 'database')
        assert hasattr(settings, 'orchestration')
        assert hasattr(settings, 'transformations')
        assert hasattr(settings, 'compute')
        assert hasattr(settings, 'pipeline')
        assert hasattr(settings, 'monitoring')
        
        # Verify required fields in each section
        assert settings.project.name
        assert settings.project.slug
        assert settings.database.host
        assert settings.database.name