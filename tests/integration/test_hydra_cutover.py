"""Integration tests for complete Hydra configuration cutover.

These tests verify that the .env -> Hydra cutover is complete and functional.
They test the entire workflow from template generation to DevContainer setup.
"""

import json
import subprocess
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Any
import pytest


class TestHydraCutover:
    """Test complete cutover from .env to Hydra-only system."""
    
    def test_post_gen_hook_creates_hydra_configs(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that post_gen_project.py creates Hydra configs instead of .env files."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Template generation failed: {result.stderr}"
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        
        # Test 1: Hydra local config should be generated
        local_config_file = project_dir / "conf/local/generated.yaml"
        assert local_config_file.exists(), "Post-generation hook should create conf/local/generated.yaml"
        
        # Test 2: Generated config should contain Fernet key and dynamic values
        with open(local_config_file) as f:
            config_content = f.read()
            config_data = yaml.safe_load(config_content)
        
        assert "orchestration" in config_data
        assert "fernet_key" in config_data["orchestration"]
        assert len(config_data["orchestration"]["fernet_key"]) > 20  # Fernet keys are long
        
        # Test 3: Environment export script should be created
        export_script = project_dir / "scripts/export_env.sh"
        assert export_script.exists(), "Should create environment export script"
        assert export_script.stat().st_mode & 0o111, "Export script should be executable"
        
        # Test 4: Traditional .env file should NOT be created by hook
        env_file = project_dir / ".env"
        assert not env_file.exists(), "Post-generation hook should NOT create .env file anymore"
    
    def test_hydra_config_loads_successfully(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that generated project can load Hydra configuration successfully."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        
        # Install dependencies (required for Hydra to work)
        uv_result = subprocess.run(['uv', 'sync'], cwd=project_dir, capture_output=True, text=True)
        if uv_result.returncode != 0:
            # Fallback: install minimum required packages for test
            subprocess.run(['pip', 'install', 'hydra-core', 'omegaconf', 'pydantic', 'sqlmodel', 'pyyaml'], 
                         cwd=project_dir, capture_output=True, text=True)
        
        # Test: Python can import and load Hydra configuration
        # Convert repo_slug to valid Python identifier
        module_name = default_cookiecutter_config["repo_slug"].replace("-", "_")
        python_test_script = f'''
import sys
import yaml
sys.path.insert(0, "src")

try:
    # First, check what's in the local config
    with open("conf/local/generated.yaml", "r") as f:
        local_config = yaml.safe_load(f)
        print("DEBUG - Local config contents:")
        print(yaml.dump(local_config, indent=2))
    
    # Try basic Hydra config load without our wrapper
    from hydra import initialize, compose
    with initialize(config_path="conf", version_base="1.1"):
        cfg = compose(config_name="config")
        print("DEBUG - Hydra config loaded:")
        print(f"  project.name: {{cfg.project.name}}")
        print(f"  orchestration keys: {{list(cfg.orchestration.keys())}}")
        if hasattr(cfg.orchestration, 'fernet_key'):
            print(f"  orchestration.fernet_key: {{cfg.orchestration.fernet_key[:20]}}...")
        if hasattr(cfg.orchestration, 'core') and hasattr(cfg.orchestration.core, 'fernet_key'):
            print(f"  orchestration.core.fernet_key: {{cfg.orchestration.core.fernet_key[:20]}}...")
    
    # Now try our settings wrapper
    from {module_name}.config import get_settings
    settings = get_settings()
    
    print("SUCCESS: Hydra configuration loaded successfully")
    
except Exception as e:
    import traceback
    print(f"FAILED: {{e}}")
    print("TRACEBACK:")
    traceback.print_exc()
    sys.exit(1)
'''
        
        result = subprocess.run([
            'python3', '-c', python_test_script
        ], cwd=project_dir, capture_output=True, text=True)
        
        assert result.returncode == 0, f"Hydra config failed to load: {result.stderr}"
        assert "SUCCESS" in result.stdout
    
    def test_environment_export_script_works(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that the environment export script generates correct environment variables."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        
        # Install dependencies first (required for Hydra to work)
        uv_result = subprocess.run(['uv', 'sync'], cwd=project_dir, capture_output=True, text=True)
        # Note: uv sync might fail in test environment, but that's okay for this test
        
        # Test: Run environment export script
        export_script = project_dir / "scripts/export_env.sh"
        result = subprocess.run([
            'bash', str(export_script)
        ], cwd=project_dir, capture_output=True, text=True)
        
        # Should succeed (either with Hydra or fallback)
        assert result.returncode == 0, f"Environment export script failed: {result.stderr}"
        
        # Should contain required environment variables
        output = result.stdout
        required_vars = [
            "AIRFLOW__CORE__FERNET_KEY",
            "AIRFLOW__CORE__EXECUTOR", 
            "POSTGRES_DB",
            "POSTGRES_USER",
            "AIRFLOW_VERSION"
        ]
        
        for var in required_vars:
            assert f"export {var}=" in output, f"Missing environment variable: {var}"
    
    def test_devcontainer_setup_script_creates_env(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that DevContainer setup script creates .env from Hydra configuration."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        
        # Test: Run DevContainer setup script
        setup_script = project_dir / ".devcontainer/setup-hydra-env.sh"
        assert setup_script.exists(), "DevContainer setup script should exist"
        assert setup_script.stat().st_mode & 0o111, "Setup script should be executable"
        
        result = subprocess.run([
            'bash', str(setup_script)
        ], cwd=project_dir, capture_output=True, text=True)
        
        assert result.returncode == 0, f"DevContainer setup failed: {result.stderr}"
        
        # Test: .env file should be created by setup script
        env_file = project_dir / ".env"
        assert env_file.exists(), "DevContainer setup should create .env file"
        
        # Test: .env should contain required variables
        env_content = env_file.read_text()
        required_vars = [
            "AIRFLOW__CORE__FERNET_KEY",
            "POSTGRES_DB",
            "POSTGRES_USER",
            "_AIRFLOW_WWW_USER_USERNAME"
        ]
        
        for var in required_vars:
            assert var in env_content, f"Generated .env missing variable: {var}"
    
    def test_docker_compose_no_longer_depends_on_manual_env(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that Docker Compose files don't reference ../.env anymore."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        
        # Test: Docker Compose should not reference ../.env
        compose_file = project_dir / ".devcontainer/compose.yaml"
        compose_content = compose_file.read_text()
        
        # Should not contain references to ../.env
        assert "../.env" not in compose_content, "Docker Compose should not reference ../.env anymore"
        
        # Should still contain references to local env files (./airflow.env, ./postgres.env)
        assert "./airflow.env" in compose_content, "Should still reference local airflow.env"
        assert "./postgres.env" in compose_content, "Should still reference local postgres.env"
    
    def test_gitignore_properly_configured(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that .gitignore is properly configured for generated .env files."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        
        # Test: .gitignore should exist and ignore .env files
        gitignore_file = project_dir / ".gitignore"
        assert gitignore_file.exists(), ".gitignore should be created"
        
        gitignore_content = gitignore_file.read_text()
        assert ".env" in gitignore_content, ".gitignore should ignore .env files"
        assert "conf/local/" in gitignore_content, ".gitignore should ignore local config overrides"
    
    def test_pipeline_runner_works_with_hydra_only(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that the pipeline runner works with Hydra-only configuration."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        
        # Install dependencies (required for pipeline runner)
        uv_result = subprocess.run(['uv', 'sync'], cwd=project_dir, capture_output=True, text=True)
        # Note: May fail in test environment, but we test with fallback
        
        # Test: Pipeline runner should work in dry-run mode
        result = subprocess.run([
            'python', 'scripts/run_pipeline.py', 'runtime.dry_run=true'
        ], cwd=project_dir, capture_output=True, text=True)
        
        # Should succeed (pipeline runner is Hydra-based)
        if result.returncode != 0:
            # Print debug info if it fails
            print(f"Pipeline runner failed with return code {result.returncode}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
        
        assert result.returncode == 0, "Pipeline runner should work with Hydra configuration"
        
        # Should indicate dry run mode was used
        assert "DRY RUN" in result.stdout or "dry_run" in result.stdout


class TestHydraConfigurationIntegrity:
    """Test that Hydra configuration system maintains integrity."""
    
    def test_no_env_file_dependencies_remain(self, template_dir: Path):
        """Test that template files don't contain .env dependencies anymore."""
        template_files = [
            template_dir / "{{cookiecutter.repo_slug}}/.devcontainer/compose.yaml",
            template_dir / "{{cookiecutter.repo_slug}}/.devcontainer/devcontainer.json",
        ]
        
        for file_path in template_files:
            if file_path.exists():
                content = file_path.read_text()
                # Should not contain ../.env references
                assert "../.env" not in content, f"File {file_path} should not reference ../.env"
    
    def test_hydra_configs_have_valid_syntax(self, template_dir: Path):
        """Test that all Hydra configuration files have valid YAML syntax."""
        conf_dir = template_dir / "{{cookiecutter.repo_slug}}/conf"
        
        if conf_dir.exists():
            yaml_files = list(conf_dir.rglob("*.yaml"))
            assert len(yaml_files) > 0, "Should have Hydra configuration files"
            
            for yaml_file in yaml_files:
                try:
                    with open(yaml_file) as f:
                        yaml.safe_load(f)
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML syntax in {yaml_file}: {e}")
    
    def test_migration_script_exists_and_works(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that migration script exists and can convert .env to Hydra."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        
        # Test: Migration script should exist
        migration_script = project_dir / "scripts/migrate_config.py"
        assert migration_script.exists(), "Migration script should exist"
        assert migration_script.stat().st_mode & 0o111, "Migration script should be executable"
        
        # Create a test .env file to migrate
        test_env_file = project_dir / "test.env"
        test_env_file.write_text("""
DB_HOST=localhost
DB_PORT=5432
AIRFLOW_EXECUTOR=CeleryExecutor
DEBUG=true
""")
        
        # Test: Run migration script
        result = subprocess.run([
            'python', str(migration_script), 
            '--env-file', str(test_env_file),
            '--output-dir', str(temp_dir / "migrated_config")
        ], cwd=project_dir, capture_output=True, text=True)
        
        assert result.returncode == 0, f"Migration script failed: {result.stderr}"
        
        # Test: Migration should create YAML files
        migrated_dir = temp_dir / "migrated_config"
        assert migrated_dir.exists(), "Migration should create output directory"
        
        config_files = list(migrated_dir.glob("*.yaml"))
        assert len(config_files) > 0, "Migration should create configuration files"