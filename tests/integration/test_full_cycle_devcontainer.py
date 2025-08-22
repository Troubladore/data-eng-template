"""
Full-cycle DevContainer integration test.

This test validates the complete workflow:
1. Generate project from cookiecutter template
2. Start DevContainer with all services
3. Verify services are running and accessible
4. Stop DevContainer cleanly
5. Start DevContainer again 
6. Verify services still work (critical for restart reliability)
7. Test deployment capabilities work in the running environment

This catches issues that only appear after multiple start/stop cycles,
which are common in real development workflows.
"""

import subprocess
import time
import tempfile
import json
from pathlib import Path
from typing import Dict, Any
import pytest
import os
import signal

# Optional dependencies for service checking
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import psycopg
    HAS_PSYCOPG = True
except ImportError:
    HAS_PSYCOPG = False


class DevContainerManager:
    """Manages DevContainer lifecycle for testing."""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.container_name = None
        self.is_running = False
    
    def start(self, timeout: int = 300) -> bool:
        """Start the DevContainer and wait for services to be ready."""
        print(f"🚀 Starting DevContainer in {self.project_dir}")
        
        # Start DevContainer
        cmd = [
            "devcontainer", "up", 
            "--workspace-folder", str(self.project_dir),
            "--config", str(self.project_dir / ".devcontainer" / "devcontainer.json")
        ]
        
        try:
            result = subprocess.run(
                cmd, 
                cwd=self.project_dir,
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            
            if result.returncode != 0:
                print(f"❌ DevContainer start failed: {result.stderr}")
                return False
            
            print("✅ DevContainer started successfully")
            self.is_running = True
            
            # Wait for services to be ready
            return self._wait_for_services(timeout=120)
            
        except subprocess.TimeoutExpired:
            print(f"❌ DevContainer start timed out after {timeout}s")
            return False
        except Exception as e:
            print(f"❌ DevContainer start error: {e}")
            return False
    
    def stop(self, timeout: int = 60) -> bool:
        """Stop the DevContainer cleanly."""
        if not self.is_running:
            return True
            
        print(f"🛑 Stopping DevContainer in {self.project_dir}")
        
        # Use docker-compose to stop services
        compose_file = self.project_dir / ".devcontainer" / "compose.yaml"
        
        if not compose_file.exists():
            print("❌ Compose file not found")
            return False
        
        cmd = ["docker-compose", "-f", str(compose_file), "down", "--volumes"]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_dir, 
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                print("✅ DevContainer stopped successfully")
                self.is_running = False
                return True
            else:
                print(f"❌ DevContainer stop failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ DevContainer stop timed out after {timeout}s")
            return False
        except Exception as e:
            print(f"❌ DevContainer stop error: {e}")
            return False
    
    def _wait_for_services(self, timeout: int = 120) -> bool:
        """Wait for Airflow and Postgres to be ready."""
        print("⏳ Waiting for services to be ready...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check Airflow webserver
                airflow_ready = self._check_airflow()
                
                # Check Postgres
                postgres_ready = self._check_postgres()
                
                if airflow_ready and postgres_ready:
                    print("✅ All services are ready")
                    return True
                    
                print(f"⏳ Services not ready yet (Airflow: {airflow_ready}, Postgres: {postgres_ready})")
                time.sleep(10)
                
            except Exception as e:
                print(f"⏳ Service check error: {e}")
                time.sleep(10)
        
        print(f"❌ Services failed to start within {timeout}s")
        return False
    
    def _check_airflow(self) -> bool:
        """Check if Airflow webserver is responding."""
        if not HAS_REQUESTS:
            print("⚠️ requests not available, using basic port check")
            return self._check_port("localhost", 8080)
        
        try:
            import requests
            response = requests.get(
                "http://localhost:8080/health", 
                timeout=5,
                auth=("admin", "admin")
            )
            return response.status_code == 200
        except:
            return False
    
    def _check_postgres(self) -> bool:
        """Check if Postgres is accepting connections."""
        if not HAS_PSYCOPG:
            print("⚠️ psycopg not available, using basic port check")
            return self._check_port("localhost", 5432)
        
        try:
            import psycopg
            with psycopg.connect(
                "postgresql://postgres:postgres@localhost:5432/airflow",
                connect_timeout=5
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    return cur.fetchone()[0] == 1
        except:
            return False
    
    def _check_port(self, host: str, port: int) -> bool:
        """Basic port connectivity check."""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                result = s.connect_ex((host, port))
                return result == 0
        except:
            return False


class TestFullCycleDevContainer:
    """Full-cycle DevContainer integration tests."""
    
    @pytest.fixture
    def generated_project_dir(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]) -> Path:
        """Generate a fresh project for testing."""
        print(f"🏗️ Generating test project in {temp_dir}")
        
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            pytest.fail(f"Failed to generate project: {result.stderr}")
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        
        if not project_dir.exists():
            pytest.fail(f"Generated project directory not found: {project_dir}")
            
        print(f"✅ Generated project at {project_dir}")
        return project_dir
    
    def test_full_devcontainer_lifecycle(self, generated_project_dir: Path):
        """Test complete DevContainer start -> stop -> start cycle."""
        manager = DevContainerManager(generated_project_dir)
        
        try:
            # First start cycle
            print("\n" + "="*60)
            print("🔄 FIRST START CYCLE")
            print("="*60)
            
            assert manager.start(), "First DevContainer start should succeed"
            
            # Verify services work
            self._verify_services_work(generated_project_dir)
            
            # Test deployment functionality
            self._test_deployment_functionality(generated_project_dir)
            
            # Stop cleanly
            print("\n" + "="*60)
            print("🛑 STOPPING DEVCONTAINER")
            print("="*60)
            
            assert manager.stop(), "DevContainer stop should succeed"
            
            # Wait a moment for cleanup
            time.sleep(5)
            
            # Second start cycle (this is where issues often appear)
            print("\n" + "="*60)
            print("🔄 SECOND START CYCLE (CRITICAL)")
            print("="*60)
            
            assert manager.start(), "Second DevContainer start should succeed"
            
            # Verify services still work after restart
            self._verify_services_work(generated_project_dir)
            
            # Test deployment functionality still works
            self._test_deployment_functionality(generated_project_dir)
            
            print("\n✅ Full lifecycle test PASSED")
            
        finally:
            # Cleanup
            try:
                if manager.is_running:
                    manager.stop()
            except:
                pass
    
    def _verify_services_work(self, project_dir: Path):
        """Verify that all services are working properly."""
        print("🔍 Verifying services work...")
        
        # Test Airflow webserver
        if HAS_REQUESTS:
            import requests
            response = requests.get(
                "http://localhost:8080/health",
                timeout=10,
                auth=("admin", "admin")
            )
            assert response.status_code == 200, "Airflow webserver should be healthy"
            print("✅ Airflow webserver is healthy")
        else:
            assert self._check_port("localhost", 8080), "Airflow port should be accessible"
            print("✅ Airflow port is accessible")
        
        # Test Postgres connection
        if HAS_PSYCOPG:
            import psycopg
            with psycopg.connect(
                "postgresql://postgres:postgres@localhost:5432/airflow",
                connect_timeout=10
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT version()")
                    version = cur.fetchone()[0]
                    assert "PostgreSQL" in version, "Should connect to PostgreSQL"
                    print(f"✅ PostgreSQL is accessible: {version[:50]}...")
        else:
            assert self._check_port("localhost", 5432), "PostgreSQL port should be accessible"
            print("✅ PostgreSQL port is accessible")
        
        # Test that DAGs directory is accessible
        dags_dir = project_dir / "dags"
        assert dags_dir.exists(), "DAGs directory should exist"
        
        # Check that example DAG exists (from template)
        example_dags = list(dags_dir.glob("*.py"))
        assert len(example_dags) > 0, "Should have at least one DAG file"
        print(f"✅ Found {len(example_dags)} DAG files")
    
    def _test_deployment_functionality(self, project_dir: Path):
        """Test that deployment functionality works in the running container."""
        print("🚀 Testing deployment functionality...")
        
        # Test that deploy script exists and is executable
        deploy_script = project_dir / "scripts" / "deploy.py"
        assert deploy_script.exists(), "Deploy script should exist"
        assert os.access(deploy_script, os.X_OK), "Deploy script should be executable"
        
        # Test dry-run deployment detection
        result = subprocess.run(
            ["python", "scripts/deploy.py", "--detect-changes", "--dry-run"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        assert result.returncode == 0, f"Deploy dry-run should succeed: {result.stderr}"
        assert "Recommended strategy:" in result.stdout, "Should show recommended strategy"
        print("✅ Deployment change detection works")
        
        # Test DAG-only dry-run deployment
        result = subprocess.run(
            ["python", "scripts/deploy.py", "--dags-only", "--dry-run"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        assert result.returncode == 0, f"DAG-only deploy dry-run should succeed: {result.stderr}"
        assert "DRY RUN" in result.stdout, "Should indicate dry run mode"
        print("✅ DAG-only deployment works")
        
        # Test that Makefile targets work
        result = subprocess.run(
            ["make", "deploy-status"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode == 0, f"Make deploy-status should work: {result.stderr}"
        print("✅ Makefile deployment targets work")
        
        print("✅ All deployment functionality verified")
    
    def _check_port(self, host: str, port: int) -> bool:
        """Basic port connectivity check."""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                result = s.connect_ex((host, port))
                return result == 0
        except:
            return False


class TestDevContainerResilience:
    """Test DevContainer resilience and error recovery."""
    
    def test_devcontainer_handles_interrupted_startup(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that DevContainer can recover from interrupted startup."""
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
        manager = DevContainerManager(project_dir)
        
        try:
            # Start and immediately interrupt (simulate common developer scenario)
            print("🔄 Testing interrupted startup recovery...")
            
            # Start the container but don't wait for full startup
            cmd = [
                "devcontainer", "up", 
                "--workspace-folder", str(project_dir),
                "--config", str(project_dir / ".devcontainer" / "devcontainer.json")
            ]
            
            process = subprocess.Popen(
                cmd,
                cwd=project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Let it start for a few seconds then interrupt
            time.sleep(10)
            process.terminate()
            process.wait(timeout=30)
            
            # Now try to start normally - this should work
            assert manager.start(), "Should recover from interrupted startup"
            
            print("✅ Successfully recovered from interrupted startup")
            
        finally:
            try:
                manager.stop()
            except:
                pass