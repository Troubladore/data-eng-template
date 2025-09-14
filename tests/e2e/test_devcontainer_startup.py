"""End-to-end tests for DevContainer startup - Full workflow validation."""

import subprocess
import time
from pathlib import Path
import pytest
import requests
import json
import shutil


class TestDevContainerStartup:
    """Test complete DevContainer workflow end-to-end."""
    
    @pytest.mark.e2e
    @pytest.mark.devcontainer
    @pytest.mark.slow
    def test_devcontainer_compose_startup(self, template_dir, temp_dir, default_cookiecutter_config):
        """Test that generated DevContainer can start services successfully."""
        # Generate project
        project_dir = self._generate_project(template_dir, temp_dir, default_cookiecutter_config)
        
        # Navigate to .devcontainer directory
        devcontainer_dir = project_dir / ".devcontainer"
        assert devcontainer_dir.exists(), "DevContainer directory should exist"
        
        compose_file = devcontainer_dir / "compose.yaml"
        assert compose_file.exists(), "Docker Compose file should exist"
        
        try:
            # Start Docker Compose services
            print("Starting Docker Compose services...")
            start_result = subprocess.run([
                'docker', 'compose', '-f', str(compose_file), 'up', '-d'
            ], capture_output=True, text=True, timeout=300, cwd=devcontainer_dir)
            
            if start_result.returncode != 0:
                pytest.fail(f"Docker Compose startup failed: {start_result.stderr}")
            
            # Wait for services to be ready
            self._wait_for_services(project_dir)
            
            # Test Airflow UI accessibility
            self._test_airflow_ui()
            
            # Test database connectivity  
            self._test_database_connectivity(devcontainer_dir)
            
        finally:
            # Always cleanup
            print("Cleaning up Docker Compose services...")
            subprocess.run([
                'docker', 'compose', '-f', str(compose_file), 'down', '-v'
            ], capture_output=True, timeout=60, cwd=devcontainer_dir)
    
    @pytest.mark.e2e
    @pytest.mark.devcontainer
    def test_vscode_devcontainer_config(self, template_dir, temp_dir, default_cookiecutter_config):
        """Test that VS Code DevContainer configuration is valid."""
        project_dir = self._generate_project(template_dir, temp_dir, default_cookiecutter_config)
        
        devcontainer_json = project_dir / ".devcontainer" / "devcontainer.json"
        assert devcontainer_json.exists(), "devcontainer.json should exist"
        
        # Parse and validate DevContainer configuration
        with open(devcontainer_json) as f:
            config = json.load(f)
        
        # Verify required fields
        assert "name" in config
        assert "image" in config
        assert "forwardPorts" in config
        
        # Verify ports configuration
        expected_ports = ["8081", "5432"]  # Airflow UI, PostgreSQL
        for port in expected_ports:
            assert port in config["forwardPorts"], f"Port {port} should be forwarded"
        
        # Verify VS Code extensions
        assert "customizations" in config
        assert "vscode" in config["customizations"]
        assert "extensions" in config["customizations"]["vscode"]
        
        expected_extensions = [
            "ms-python.python",
            "charliermarsh.ruff",
            "redhat.vscode-yaml"
        ]
        
        actual_extensions = config["customizations"]["vscode"]["extensions"]
        for ext in expected_extensions:
            assert ext in actual_extensions, f"Extension {ext} should be included"
    
    def _generate_project(self, template_dir: str, temp_dir: Path, config: dict) -> Path:
        """Generate a test project."""
        cmd = [
            'cookiecutter', template_dir,
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            pytest.fail(f"Project generation failed: {result.stderr}")
        
        return temp_dir / config["project_slug"]
    
    def _wait_for_services(self, project_dir: Path, max_wait: int = 120):
        """Wait for services to be ready."""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            # Check if Airflow webserver is responding
            try:
                response = requests.get("http://localhost:8081/health", timeout=5)
                if response.status_code == 200:
                    print("Airflow webserver is ready!")
                    return
            except requests.RequestException:
                pass
            
            print("Waiting for services to be ready...")
            time.sleep(5)
        
        pytest.fail("Services failed to start within timeout")
    
    def _test_airflow_ui(self):
        """Test that Airflow UI is accessible."""
        try:
            response = requests.get("http://localhost:8081/", timeout=10)
            assert response.status_code == 200, "Airflow UI should be accessible"
            assert "airflow" in response.text.lower(), "Should contain Airflow content"
        except requests.RequestException as e:
            pytest.fail(f"Failed to access Airflow UI: {e}")
    
    def _test_database_connectivity(self, devcontainer_dir: Path):
        """Test database connectivity."""
        # Test that PostgreSQL container is running and accepting connections
        test_cmd = [
            'docker', 'compose', 'exec', '-T', 'postgres',
            'pg_isready', '-U', 'admin'
        ]
        
        result = subprocess.run(test_cmd, capture_output=True, text=True, 
                              timeout=30, cwd=devcontainer_dir)
        
        assert result.returncode == 0, f"PostgreSQL should be ready: {result.stderr}"