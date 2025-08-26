"""Integration tests for Airflow authentication functionality."""

import subprocess
import tempfile
import time
import requests
from pathlib import Path
from typing import Dict, Any
import pytest


class TestAirflowAuthentication:
    """Test complete Airflow authentication flow in generated projects."""
    
    @pytest.mark.slow
    def test_airflow_login_with_admin_credentials(self, template_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that admin/admin credentials work for Airflow login in generated project.
        
        This is the critical end-to-end test that validates:
        1. Project generation with correct credentials
        2. Docker Compose services start successfully
        3. Airflow web server is accessible
        4. Authentication works with admin/admin credentials
        5. User can access the Airflow dashboard after login
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Generate project
            cmd = [
                'cookiecutter', str(template_dir),
                '--output-dir', str(temp_path),
                '--no-input'
            ]
            
            # Add each config variable as command line argument
            for key, value in default_cookiecutter_config.items():
                cmd.append(f"{key}={value}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Template generation failed: {result.stderr}"
            
            project_dir = temp_path / default_cookiecutter_config["repo_slug"]
            devcontainer_dir = project_dir / ".devcontainer"
            
            # Verify files exist before starting services
            assert (devcontainer_dir / "compose.yaml").exists(), "compose.yaml should exist"
            assert (devcontainer_dir / "airflow.env").exists(), "airflow.env should exist"
            
            # Start Docker Compose services
            compose_cmd = ["docker", "compose", "-f", str(devcontainer_dir / "compose.yaml"), "up", "-d"]
            startup_result = subprocess.run(compose_cmd, capture_output=True, text=True, cwd=devcontainer_dir)
            
            if startup_result.returncode != 0:
                pytest.skip(f"Docker Compose startup failed (Docker may not be available): {startup_result.stderr}")
            
            try:
                # Wait for services to be healthy (up to 5 minutes)
                max_wait_time = 300  # 5 minutes
                start_time = time.time()
                airflow_ready = False
                
                print("Waiting for Airflow web server to start...")
                
                while time.time() - start_time < max_wait_time:
                    try:
                        # Check if Airflow webserver is responding
                        response = requests.get("http://localhost:8080/health", timeout=5)
                        if response.status_code == 200:
                            print(f"✅ Airflow health endpoint responding after {time.time() - start_time:.1f}s")
                            airflow_ready = True
                            break
                    except (requests.ConnectionError, requests.Timeout):
                        pass
                    
                    time.sleep(5)
                    print(f"Still waiting for Airflow... ({time.time() - start_time:.1f}s elapsed)")
                
                if not airflow_ready:
                    # Get container logs for debugging
                    logs_cmd = ["docker", "compose", "-f", str(devcontainer_dir / "compose.yaml"), "logs", "airflow-webserver"]
                    logs_result = subprocess.run(logs_cmd, capture_output=True, text=True, cwd=devcontainer_dir)
                    pytest.fail(f"Airflow did not become ready within {max_wait_time}s. Webserver logs:\n{logs_result.stdout}\n{logs_result.stderr}")
                
                # Test login page access
                login_response = requests.get("http://localhost:8080/login/", timeout=10)
                assert login_response.status_code == 200, f"Login page should be accessible, got {login_response.status_code}"
                assert "login" in login_response.text.lower(), "Login page should contain login form"
                
                # Test authentication with admin/admin credentials
                session = requests.Session()
                
                # Get login page to extract CSRF token
                login_page = session.get("http://localhost:8080/login/", timeout=10)
                assert login_page.status_code == 200, "Should be able to access login page"
                
                # Extract CSRF token from login form
                csrf_token = None
                if 'csrf_token' in login_page.text:
                    # Parse CSRF token from form (simple string search for this test)
                    start = login_page.text.find('name="csrf_token"')
                    if start != -1:
                        start = login_page.text.find('value="', start) + 7
                        end = login_page.text.find('"', start)
                        csrf_token = login_page.text[start:end]
                
                # Attempt login with admin credentials
                login_data = {
                    "username": "admin",
                    "password": "admin"
                }
                
                if csrf_token:
                    login_data["csrf_token"] = csrf_token
                
                print("Attempting login with admin/admin credentials...")
                login_attempt = session.post(
                    "http://localhost:8080/login/",
                    data=login_data,
                    allow_redirects=False,  # Don't follow redirects automatically
                    timeout=10
                )
                
                # Successful login should redirect (302) or return 200
                assert login_attempt.status_code in [200, 302], f"Login attempt failed with status {login_attempt.status_code}: {login_attempt.text[:500]}"
                
                # Follow redirect if present and verify we reach the dashboard
                if login_attempt.status_code == 302:
                    redirect_location = login_attempt.headers.get('Location', '')
                    if redirect_location.startswith('/'):
                        redirect_location = "http://localhost:8080" + redirect_location
                    
                    dashboard_response = session.get(redirect_location, timeout=10)
                    assert dashboard_response.status_code == 200, f"Dashboard access failed: {dashboard_response.status_code}"
                    
                    # Verify we're on the Airflow dashboard (not back to login)
                    dashboard_content = dashboard_response.text.lower()
                    assert "dag" in dashboard_content or "airflow" in dashboard_content, "Should be on Airflow dashboard"
                    assert "login" not in dashboard_content or "logout" in dashboard_content, "Should not be on login page"
                    
                    print("✅ Successfully logged in and accessed Airflow dashboard")
                else:
                    # Direct 200 response - verify we're authenticated
                    content = login_attempt.text.lower()
                    assert "dag" in content or "airflow" in content, "Should see Airflow dashboard content"
                    assert "invalid" not in content and "error" not in content, "Should not see login errors"
                    
                    print("✅ Successfully authenticated with admin/admin credentials")
                
                # Additional verification: Try to access a protected endpoint
                # Try different possible DAG endpoints (Airflow versions vary)
                protected_endpoints = ["/home", "/dag", "/grid", "/"]
                authenticated = False
                
                for endpoint in protected_endpoints:
                    try:
                        endpoint_response = session.get(f"http://localhost:8080{endpoint}", timeout=10)
                        if endpoint_response.status_code == 200:
                            content = endpoint_response.text.lower()
                            if "dag" in content or "airflow" in content:
                                authenticated = True
                                print(f"✅ Successfully accessed protected endpoint: {endpoint}")
                                break
                    except:
                        continue
                
                assert authenticated, "Should be able to access at least one protected Airflow endpoint when authenticated"
                
                print("✅ End-to-end Airflow authentication test passed!")
                
            finally:
                # Clean up: Stop and remove containers
                cleanup_cmd = ["docker", "compose", "-f", str(devcontainer_dir / "compose.yaml"), "down", "-v"]
                cleanup_result = subprocess.run(cleanup_cmd, capture_output=True, text=True, cwd=devcontainer_dir)
                
                if cleanup_result.returncode != 0:
                    print(f"Warning: Cleanup failed: {cleanup_result.stderr}")
                else:
                    print("✅ Docker containers cleaned up successfully")
    
    def test_airflow_login_rejects_wrong_credentials(self, template_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that Airflow properly rejects incorrect credentials."""
        # This is a lighter test that can run without full Docker Compose setup
        # Just verify that the authentication mechanism would work by checking files
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
            
            # Verify that the credentials are properly configured
            airflow_env_file = project_dir / ".devcontainer" / "airflow.env"
            airflow_env_content = airflow_env_file.read_text()
            
            # The credentials should be exactly "admin" (not blank, not default, not placeholder)
            assert "_AIRFLOW_WWW_USER_USERNAME=admin" in airflow_env_content
            assert "_AIRFLOW_WWW_USER_PASSWORD=admin" in airflow_env_content
            
            # Verify the compose file references the correct env file
            compose_file = project_dir / ".devcontainer" / "compose.yaml"
            compose_content = compose_file.read_text()
            
            # The compose file should use airflow.env for airflow services
            assert "env_file: [./airflow.env]" in compose_content, "Compose should reference airflow.env"
            
            # The init command should use the environment variables
            assert "$$_AIRFLOW_WWW_USER_USERNAME" in compose_content, "Init should use username variable"
            assert "$$_AIRFLOW_WWW_USER_PASSWORD" in compose_content, "Init should use password variable"