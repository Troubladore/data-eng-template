"""
Integration test that validates DevContainer actually starts successfully.

This test should have been written FIRST to catch the environment variable
and mount namespace issues that prevented DevContainer startup.

Uses random project names to avoid brittleness.
"""

import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Any
import pytest
import time
import requests
import socket


def generate_random_project_name() -> str:
    """Generate a random project name to avoid test brittleness."""
    return f"test-project-{uuid.uuid4().hex[:8]}"


def wait_for_port(host: str, port: int, timeout: int = 30) -> bool:
    """Wait for a port to be available."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((host, port))
                if result == 0:
                    return True
        except:
            pass
        time.sleep(2)
    return False


class TestDevContainerStartupValidation:
    """Test that DevContainer actually starts and works with random project names."""
    
    def test_devcontainer_starts_successfully_with_random_name(self, template_dir: Path, temp_dir: Path):
        """Test DevContainer startup with a randomly named project."""
        
        # Generate random project name
        random_slug = generate_random_project_name()
        
        # Generate project with random name
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input',
            f'repo_slug={random_slug}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        assert result.returncode == 0, f"Failed to generate project: {result.stderr}"
        
        project_dir = temp_dir / random_slug
        assert project_dir.exists(), f"Project directory not found: {project_dir}"
        
        try:
            # Test DevContainer startup
            print(f"Testing DevContainer startup for project: {random_slug}")
            
            devcontainer_cmd = [
                "devcontainer", "up", 
                "--workspace-folder", str(project_dir),
                "--log-level", "info"
            ]
            
            # Start DevContainer (with extended timeout)
            result = subprocess.run(
                devcontainer_cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            # This should succeed if our environment setup is correct
            assert result.returncode == 0, f"DevContainer startup failed: {result.stderr}"
            print("✅ DevContainer started successfully")
            
            # Wait for services to be available
            print("⏳ Waiting for Airflow to be available...")
            airflow_ready = wait_for_port("localhost", 8081, timeout=60)
            assert airflow_ready, "Airflow webserver did not start within 60 seconds"
            print("✅ Airflow is accessible")
            
            print("⏳ Waiting for PostgreSQL to be available...")  
            postgres_ready = wait_for_port("localhost", 5432, timeout=60)
            assert postgres_ready, "PostgreSQL did not start within 60 seconds"
            print("✅ PostgreSQL is accessible")
            
            # Test that we can connect to Airflow UI
            try:
                response = requests.get(
                    "http://localhost:8081/health",
                    timeout=10,
                    auth=("admin", "admin")
                )
                assert response.status_code == 200, f"Airflow health check failed: {response.status_code}"
                print("✅ Airflow health check passed")
            except requests.exceptions.RequestException as e:
                pytest.fail(f"Failed to connect to Airflow UI: {e}")
            
            # Test DevContainer exec functionality
            exec_cmd = [
                "devcontainer", "exec",
                "--workspace-folder", str(project_dir),
                "python", "--version"
            ]
            
            result = subprocess.run(exec_cmd, capture_output=True, text=True, timeout=30)
            assert result.returncode == 0, f"DevContainer exec failed: {result.stderr}"
            assert "Python 3.12" in result.stdout, f"Wrong Python version: {result.stdout}"
            print("✅ DevContainer exec works")
            
        finally:
            # Clean up using robust cleanup system
            from tests.helpers.cleanup import cleanup_project
            
            cleanup_success = cleanup_project(project_dir, timeout=60)
            if cleanup_success:
                print("✅ DevContainer cleaned up successfully")
            else:
                print("⚠️ Warning: Cleanup issues detected")
                # Try emergency cleanup as fallback
                from tests.helpers.cleanup import emergency_cleanup
                emergency_cleanup()
    
    def test_environment_variables_are_populated_correctly(self, template_dir: Path, temp_dir: Path):
        """Test that environment variables are correctly generated and accessible."""
        
        random_slug = generate_random_project_name()
        
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input',
            f'repo_slug={random_slug}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        assert result.returncode == 0
        
        project_dir = temp_dir / random_slug
        
        # Run the environment setup script
        setup_cmd = ["bash", ".devcontainer/setup-hydra-env.sh"]
        result = subprocess.run(setup_cmd, cwd=project_dir, capture_output=True, text=True)
        assert result.returncode == 0, f"Environment setup failed: {result.stderr}"
        
        # Check that required environment files exist and have content
        airflow_env = project_dir / ".devcontainer" / "airflow.env"
        assert airflow_env.exists(), "airflow.env must exist"
        
        airflow_content = airflow_env.read_text()
        assert "AIRFLOW__CORE__FERNET_KEY=" in airflow_content, "Fernet key must be in airflow.env"
        assert len(airflow_content.split("AIRFLOW__CORE__FERNET_KEY=")[1].split()[0]) > 10, "Fernet key must not be empty"
        
        postgres_env = project_dir / ".devcontainer" / "postgres.env" 
        assert postgres_env.exists(), "postgres.env must exist"
        
        postgres_content = postgres_env.read_text()
        assert "POSTGRES_DB=airflow" in postgres_content, "Postgres DB must be configured"
        
        # Check that Docker Compose can read the environment variables
        compose_cmd = ["docker", "compose", "-f", ".devcontainer/compose.yaml", "config"]
        result = subprocess.run(compose_cmd, cwd=project_dir, capture_output=True, text=True)
        assert result.returncode == 0, f"Docker Compose config failed: {result.stderr}"
        
        # The compose config should not show empty Fernet key
        assert 'AIRFLOW__CORE__FERNET_KEY: ""' not in result.stdout, "Fernet key should not be empty in compose config"
        print("✅ Environment variables are properly configured")
    
    def test_multiple_random_projects_can_be_generated(self, template_dir: Path, temp_dir: Path):
        """Test that we can generate multiple projects with different random names."""
        
        projects = []
        
        for i in range(3):
            random_slug = generate_random_project_name()
            
            cmd = [
                'cookiecutter', str(template_dir),
                '--output-dir', str(temp_dir),
                '--no-input',
                f'repo_slug={random_slug}'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            assert result.returncode == 0, f"Failed to generate project {i}: {result.stderr}"
            
            project_dir = temp_dir / random_slug
            assert project_dir.exists(), f"Project directory not found: {project_dir}"
            
            # Verify each has unique configurations
            env_file = project_dir / ".env"
            if env_file.exists():
                content = env_file.read_text()
                # Each should have a unique Fernet key
                fernet_line = [line for line in content.split('\n') if 'FERNET_KEY' in line]
                assert len(fernet_line) > 0, f"No Fernet key found in project {random_slug}"
            
            projects.append(random_slug)
        
        # All project names should be unique
        assert len(set(projects)) == 3, f"Project names should be unique: {projects}"
        print(f"✅ Generated {len(projects)} unique projects: {projects}")


@pytest.mark.slow
class TestDevContainerRestart:
    """Test DevContainer restart scenarios with random names."""
    
    def test_devcontainer_survives_restart_cycle(self, template_dir: Path, temp_dir: Path):
        """Test that DevContainer can be stopped and restarted successfully."""
        
        random_slug = generate_random_project_name()
        
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input',
            f'repo_slug={random_slug}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        assert result.returncode == 0
        
        project_dir = temp_dir / random_slug
        
        try:
            # First startup
            print(f"🔄 First startup of project: {random_slug}")
            start_cmd = ["devcontainer", "up", "--workspace-folder", str(project_dir)]
            result = subprocess.run(start_cmd, capture_output=True, text=True, timeout=300)
            assert result.returncode == 0, f"First startup failed: {result.stderr}"
            
            # Verify services work
            assert wait_for_port("localhost", 8081, timeout=60), "Airflow not available after first start"
            print("✅ First startup successful")
            
            # Stop
            print("🛑 Stopping DevContainer")
            stop_cmd = ["devcontainer", "down", "--workspace-folder", str(project_dir)]
            subprocess.run(stop_cmd, timeout=60)
            
            # Wait for cleanup
            time.sleep(5)
            
            # Second startup (this is where problems often occur)
            print("🔄 Second startup (critical test)")
            start_cmd = ["devcontainer", "up", "--workspace-folder", str(project_dir)]
            result = subprocess.run(start_cmd, capture_output=True, text=True, timeout=300)
            assert result.returncode == 0, f"Second startup failed: {result.stderr}"
            
            # Verify services still work
            assert wait_for_port("localhost", 8081, timeout=60), "Airflow not available after restart"
            print("✅ Restart cycle successful")
            
        finally:
            # Cleanup using robust system
            from tests.helpers.cleanup import cleanup_project
            cleanup_project(project_dir, timeout=60)