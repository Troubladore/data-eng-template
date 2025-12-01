"""Integration tests for PostgreSQL database connectivity and configuration."""

import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, Any
import pytest

# Optional database client for testing actual connections
try:
    import psycopg
    HAS_PSYCOPG = True
except ImportError:
    HAS_PSYCOPG = False


class TestPostgresIntegration:
    """Test PostgreSQL database integration in generated projects."""
    
    @pytest.mark.slow
    def test_postgres_connection_with_default_credentials(self, template_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that PostgreSQL is accessible with default postgres/postgres credentials."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Generate project
            cmd = [
                'cookiecutter', str(template_dir),
                '--output-dir', str(temp_path),
                '--no-input'
            ]
            
            for key, value in default_cookiecutter_config.items():
                cmd.append(f"{key}={value}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Template generation failed: {result.stderr}"
            
            project_dir = temp_path / default_cookiecutter_config["repo_slug"]
            devcontainer_dir = project_dir / ".devcontainer"
            
            # Start only Postgres service for focused testing
            compose_cmd = ["docker", "compose", "-f", str(devcontainer_dir / "compose.yaml"), "up", "-d", "postgres"]
            startup_result = subprocess.run(compose_cmd, capture_output=True, text=True, cwd=devcontainer_dir)
            
            if startup_result.returncode != 0:
                pytest.skip(f"Docker Compose startup failed: {startup_result.stderr}")
            
            try:
                # Wait for Postgres to be ready (shorter timeout since it's just one service)
                max_wait_time = 60
                start_time = time.time()
                postgres_ready = False
                
                while time.time() - start_time < max_wait_time:
                    try:
                        # Test actual database connection
                        test_connection = subprocess.run([
                            "docker", "exec", "-i", "devcontainer-postgres-1",
                            "psql", "-U", "postgres", "-d", "airflow", 
                            "-c", "SELECT version();"
                        ], capture_output=True, text=True, timeout=5)
                        
                        if test_connection.returncode == 0 and "PostgreSQL" in test_connection.stdout:
                            postgres_ready = True
                            print(f"✅ PostgreSQL ready after {time.time() - start_time:.1f}s")
                            break
                    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                        pass
                    
                    time.sleep(2)
                
                assert postgres_ready, f"PostgreSQL not ready within {max_wait_time}s"
                
                # Test database operations
                operations = [
                    ("SELECT 1 as test;", "Basic query should work"),
                    ("CREATE TABLE test_table (id SERIAL PRIMARY KEY, name VARCHAR(50));", "Table creation should work"),
                    ("INSERT INTO test_table (name) VALUES ('test_data');", "Data insertion should work"),
                    ("SELECT COUNT(*) FROM test_table;", "Data selection should work"),
                    ("DROP TABLE test_table;", "Table deletion should work")
                ]
                
                for sql, description in operations:
                    result = subprocess.run([
                        "docker", "exec", "-i", "devcontainer-postgres-1",
                        "psql", "-U", "postgres", "-d", "airflow", "-c", sql
                    ], capture_output=True, text=True)
                    
                    assert result.returncode == 0, f"{description}. SQL: {sql}. Error: {result.stderr}"
                
                print("✅ All PostgreSQL database operations successful")
                
            finally:
                # Cleanup
                cleanup_cmd = ["docker", "compose", "-f", str(devcontainer_dir / "compose.yaml"), "down", "-v"]
                subprocess.run(cleanup_cmd, capture_output=True, cwd=devcontainer_dir)

    def test_postgres_configuration_files(self, template_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that PostgreSQL configuration files are correctly generated."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Generate project
            cmd = [
                'cookiecutter', str(template_dir),
                '--output-dir', str(temp_path),
                '--no-input'
            ]
            
            for key, value in default_cookiecutter_config.items():
                cmd.append(f"{key}={value}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Template generation failed: {result.stderr}"
            
            project_dir = temp_path / default_cookiecutter_config["repo_slug"]
            
            # Check postgres.env file
            postgres_env_file = project_dir / ".devcontainer" / "postgres.env"
            assert postgres_env_file.exists(), "postgres.env should exist"
            
            postgres_env_content = postgres_env_file.read_text()
            expected_postgres_vars = [
                "POSTGRES_DB=",
                "POSTGRES_USER=",
                "POSTGRES_PASSWORD="
            ]
            
            for var in expected_postgres_vars:
                assert var in postgres_env_content, f"PostgreSQL environment variable {var} should be in postgres.env"
            
            # Check main .env file has Postgres configs
            main_env_file = project_dir / ".devcontainer" / ".env"
            assert main_env_file.exists(), ".devcontainer/.env should exist"
            
            main_env_content = main_env_file.read_text()
            expected_main_vars = [
                "POSTGRES_DB=airflow",
                "POSTGRES_USER=airflow", 
                "POSTGRES_PASSWORD=airflow"
            ]
            
            for var in expected_main_vars:
                assert var in main_env_content, f"PostgreSQL variable {var} should be in main .env"
            
            # Verify compose file references postgres.env
            compose_file = project_dir / ".devcontainer" / "compose.yaml"
            compose_content = compose_file.read_text()
            assert "postgres.env" in compose_content, "compose.yaml should reference postgres.env"
            
            print("✅ PostgreSQL configuration files properly generated")

    @pytest.mark.slow  
    def test_custom_postgres_credentials(self, template_dir: Path):
        """Test PostgreSQL works with custom database credentials."""
        custom_config = {
            "project_name": "Custom DB Test",
            "repo_slug": "custom-db-test",
            "author_name": "Test Author",
            "python_version": "3.12",
            "airflow_version": "2.9.3",
            "postgres_version": "16",
            "airflow_executor": "LocalExecutor",
            "db_name": "custom_database",
            "db_user": "custom_user",
            "db_password": "custom_password_123",
            "license": "MIT"
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Generate project with custom credentials
            cmd = [
                'cookiecutter', str(template_dir),
                '--output-dir', str(temp_path),
                '--no-input'
            ]
            
            for key, value in custom_config.items():
                cmd.append(f"{key}={value}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Template generation failed: {result.stderr}"
            
            project_dir = temp_path / custom_config["repo_slug"]
            devcontainer_dir = project_dir / ".devcontainer"
            
            # Verify custom credentials are in config files
            env_file = devcontainer_dir / ".env"
            env_content = env_file.read_text()
            
            assert f"POSTGRES_DB={custom_config['db_name']}" in env_content
            assert f"POSTGRES_USER={custom_config['db_user']}" in env_content  
            assert f"POSTGRES_PASSWORD={custom_config['db_password']}" in env_content
            
            # Start Postgres with custom credentials
            compose_cmd = ["docker", "compose", "-f", str(devcontainer_dir / "compose.yaml"), "up", "-d", "postgres"]
            startup_result = subprocess.run(compose_cmd, capture_output=True, text=True, cwd=devcontainer_dir)
            
            if startup_result.returncode != 0:
                pytest.skip(f"Docker Compose startup failed: {startup_result.stderr}")
            
            try:
                # Wait for custom database to be ready
                max_wait_time = 60
                start_time = time.time()
                
                while time.time() - start_time < max_wait_time:
                    try:
                        # Test connection with custom credentials
                        test_connection = subprocess.run([
                            "docker", "exec", "-i", "devcontainer-postgres-1",
                            "psql", f"-U", custom_config['db_user'], 
                            f"-d", custom_config['db_name'],
                            "-c", "SELECT current_database(), current_user;"
                        ], capture_output=True, text=True, timeout=5)
                        
                        if test_connection.returncode == 0:
                            print(f"✅ Custom PostgreSQL credentials work: {test_connection.stdout.strip()}")
                            break
                    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                        pass
                    
                    time.sleep(2)
                else:
                    pytest.fail(f"Custom PostgreSQL credentials not working within {max_wait_time}s")
                    
            finally:
                # Cleanup
                cleanup_cmd = ["docker", "compose", "-f", str(devcontainer_dir / "compose.yaml"), "down", "-v"]
                subprocess.run(cleanup_cmd, capture_output=True, cwd=devcontainer_dir)


class TestConfigurationChanges:
    """Test that configuration changes are properly handled at runtime."""
    
    def test_env_file_configuration_override(self, template_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that changes to .env files would be picked up by services."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Generate project
            cmd = [
                'cookiecutter', str(template_dir),
                '--output-dir', str(temp_path),
                '--no-input'
            ]
            
            for key, value in default_cookiecutter_config.items():
                cmd.append(f"{key}={value}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Template generation failed: {result.stderr}"
            
            project_dir = temp_path / default_cookiecutter_config["repo_slug"]
            
            # Modify Postgres configuration
            env_file = project_dir / ".devcontainer" / ".env"
            original_content = env_file.read_text()
            
            # Change database name
            modified_content = original_content.replace(
                "POSTGRES_DB=airflow", 
                "POSTGRES_DB=modified_airflow_db"
            )
            env_file.write_text(modified_content)
            
            # Verify change was applied
            updated_content = env_file.read_text()
            assert "POSTGRES_DB=modified_airflow_db" in updated_content, "Configuration change should be persisted"
            assert "POSTGRES_DB=airflow" not in updated_content, "Old configuration should be removed"
            
            # Test that compose file would use the new values
            compose_file = project_dir / ".devcontainer" / "compose.yaml"
            compose_content = compose_file.read_text()
            
            # Compose should use ${POSTGRES_DB} variable substitution
            assert "${POSTGRES_DB" in compose_content, "Compose should use variable substitution for flexibility"
            
            print("✅ Configuration changes can be applied and would be picked up by services")

    def test_hydra_configuration_integration(self, template_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that Hydra configuration system properly generates environment variables."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Generate project
            cmd = [
                'cookiecutter', str(template_dir),
                '--output-dir', str(temp_path),
                '--no-input'
            ]
            
            for key, value in default_cookiecutter_config.items():
                cmd.append(f"{key}={value}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Template generation failed: {result.stderr}"
            
            project_dir = temp_path / default_cookiecutter_config["repo_slug"]
            
            # Check Hydra local configuration
            hydra_local_config = project_dir / "conf" / "local" / "generated.yaml"
            assert hydra_local_config.exists(), "Hydra local config should be generated"
            
            hydra_content = hydra_local_config.read_text()
            assert "project:" in hydra_content, "Should contain project configuration"
            assert "orchestration:" in hydra_content, "Should contain orchestration configuration"
            
            # Check environment export script
            env_script = project_dir / "scripts" / "export_env.sh"
            assert env_script.exists(), "Environment export script should exist"
            assert env_script.stat().st_mode & 0o111, "Export script should be executable"
            
            # Verify export script content
            script_content = env_script.read_text()
            expected_exports = [
                "POSTGRES_DB",
                "POSTGRES_USER", 
                "POSTGRES_PASSWORD",
                "AIRFLOW__CORE__FERNET_KEY",
                "_AIRFLOW_WWW_USER_USERNAME",
                "_AIRFLOW_WWW_USER_PASSWORD"
            ]
            
            for export_var in expected_exports:
                assert export_var in script_content, f"Export script should handle {export_var}"
            
            print("✅ Hydra configuration system properly integrated with environment variables")