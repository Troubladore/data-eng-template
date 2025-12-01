"""
Fast DevContainer startup tests using pre-built base images.

These tests validate the same functionality as the original DevContainer tests
but use optimized infrastructure to run much faster by avoiding repeated
large image downloads and builds.
"""

import subprocess
import time
import uuid
from pathlib import Path
from typing import Dict, Any
import pytest
import requests
import socket

from tests.helpers.fast_testing import (
    fast_test_project_factory,
    fast_devcontainer_up, 
    fast_devcontainer_down,
    fast_test_base_image
)


def generate_random_project_name() -> str:
    """Generate a random project name to avoid test brittleness."""
    return f"fast-test-{uuid.uuid4().hex[:8]}"


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


class TestFastDevContainerStartup:
    """Test DevContainer startup using fast pre-built infrastructure."""
    
    def test_fast_devcontainer_starts_successfully(
        self, 
        fast_test_base_image,
        fast_test_project_factory,
        default_cookiecutter_config
    ):
        """Test fast DevContainer startup with pre-built base image."""
        
        # Generate random project to avoid conflicts
        config = default_cookiecutter_config.copy()
        config["repo_slug"] = generate_random_project_name()
        
        # Create project with fast infrastructure
        project_dir = fast_test_project_factory(config)
        
        try:
            # Start DevContainer with fast method
            success = fast_devcontainer_up(project_dir, timeout=120)
            assert success, "Fast DevContainer startup should succeed"
            
            # Wait for services to be available - should be much faster
            print("⏳ Waiting for Airflow to be available...")
            airflow_ready = wait_for_port("localhost", 8081, timeout=60)
            assert airflow_ready, "Airflow webserver did not start within 60 seconds"
            print("✅ Airflow is accessible")
            
            print("⏳ Waiting for PostgreSQL to be available...")
            postgres_ready = wait_for_port("localhost", 5432, timeout=30)
            assert postgres_ready, "PostgreSQL did not start within 30 seconds"
            print("✅ PostgreSQL is accessible")
            
            # Test Airflow health endpoint
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
            
            # Test that we can execute commands in the container
            exec_cmd = [
                "docker", "compose",
                "-f", str(project_dir / ".devcontainer" / "compose.yaml"),
                "exec", "-T", "airflow-webserver",
                "python", "-c", "import airflow; print(f'Airflow {airflow.__version__}')"
            ]
            
            result = subprocess.run(exec_cmd, capture_output=True, text=True, timeout=30)
            assert result.returncode == 0, f"Container exec failed: {result.stderr}"
            assert "Airflow 3.0.6" in result.stdout, f"Wrong Airflow version: {result.stdout}"
            print("✅ Container exec works with Airflow 3.0.6")
            
        finally:
            # Clean up
            fast_devcontainer_down(project_dir, timeout=60)
    
    def test_fast_startup_performance_benchmark(
        self, 
        fast_test_base_image,
        fast_test_project_factory, 
        default_cookiecutter_config
    ):
        """Benchmark the performance improvement of fast startup."""
        
        config = default_cookiecutter_config.copy()
        config["repo_slug"] = generate_random_project_name()
        
        project_dir = fast_test_project_factory(config)
        
        try:
            # Time the startup process
            start_time = time.time()
            
            success = fast_devcontainer_up(project_dir, timeout=120)
            assert success, "Fast startup should succeed"
            
            # Wait for Airflow to be ready
            airflow_ready = wait_for_port("localhost", 8081, timeout=60)
            assert airflow_ready, "Airflow should be ready quickly"
            
            total_time = time.time() - start_time
            print(f"🏁 Fast startup completed in {total_time:.1f} seconds")
            
            # Fast startup should be under 2 minutes (vs 5+ minutes for full build)
            assert total_time < 120, f"Fast startup took too long: {total_time:.1f}s"
            
            print("✅ Fast startup performance meets expectations")
            
        finally:
            fast_devcontainer_down(project_dir)
    
    def test_multiple_fast_projects_can_coexist(
        self,
        fast_test_base_image,
        fast_test_project_factory,
        default_cookiecutter_config
    ):
        """Test that multiple fast test projects can be created simultaneously."""
        
        projects = []
        
        try:
            # Create 3 projects quickly
            for i in range(3):
                config = default_cookiecutter_config.copy()
                config["repo_slug"] = generate_random_project_name()
                
                project_dir = fast_test_project_factory(config)
                projects.append(project_dir)
                
                # Verify each project has the fast compose setup
                compose_file = project_dir / ".devcontainer" / "compose.yaml"
                compose_content = compose_file.read_text()
                assert "test-fast" in compose_content, "Should use fast test compose"
                
            print(f"✅ Created {len(projects)} fast test projects successfully")
            
            # Each should have unique compose project names
            project_names = []
            for project_dir in projects:
                compose_content = (project_dir / ".devcontainer" / "compose.yaml").read_text()
                # Extract project name from compose file
                for line in compose_content.split('\n'):
                    if line.startswith('name:'):
                        project_names.append(line.split(':')[1].strip())
                        break
            
            assert len(set(project_names)) == len(projects), "Project names should be unique"
            print(f"✅ All projects have unique Docker Compose names")
            
        finally:
            # Cleanup all projects
            for project_dir in projects:
                try:
                    fast_devcontainer_down(project_dir, timeout=30)
                except:
                    pass


@pytest.mark.slow 
class TestFastDevContainerRestart:
    """Test DevContainer restart scenarios with fast infrastructure."""
    
    def test_fast_devcontainer_survives_restart_cycle(
        self,
        fast_test_base_image, 
        fast_test_project_factory,
        default_cookiecutter_config
    ):
        """Test that fast DevContainer can be stopped and restarted."""
        
        config = default_cookiecutter_config.copy()
        config["repo_slug"] = generate_random_project_name()
        
        project_dir = fast_test_project_factory(config)
        
        try:
            # First startup
            print(f"🔄 First fast startup of {project_dir.name}")
            success = fast_devcontainer_up(project_dir, timeout=120)
            assert success, "First fast startup should succeed"
            
            airflow_ready = wait_for_port("localhost", 8081, timeout=60)
            assert airflow_ready, "Airflow should be ready after first start"
            print("✅ First fast startup successful")
            
            # Stop cleanly
            print("🛑 Stopping fast DevContainer")
            stop_success = fast_devcontainer_down(project_dir, timeout=60)
            assert stop_success, "Fast stop should succeed"
            
            # Wait for cleanup
            time.sleep(3)  # Reduced wait time for fast infrastructure
            
            # Second startup (this tests image caching)
            print("🔄 Second fast startup (testing cache)")
            start_time = time.time()
            success = fast_devcontainer_up(project_dir, timeout=120)
            assert success, "Second fast startup should succeed"
            
            restart_time = time.time() - start_time
            print(f"🏁 Second startup completed in {restart_time:.1f} seconds")
            
            # Second startup should be even faster due to Docker layer caching
            assert restart_time < 90, f"Second startup too slow: {restart_time:.1f}s"
            
            airflow_ready = wait_for_port("localhost", 8081, timeout=60)
            assert airflow_ready, "Airflow should be ready after restart"
            print("✅ Fast restart cycle successful")
            
        finally:
            fast_devcontainer_down(project_dir, timeout=60)