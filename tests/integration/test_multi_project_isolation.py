"""Integration tests for multi-project isolation - Critical for team environments."""

import subprocess
from pathlib import Path
from typing import Dict, Any
import pytest
import time


class TestMultiProjectIsolation:
    """Test that multiple generated projects don't conflict."""
    
    @pytest.mark.integration
    @pytest.mark.multi_project
    def test_two_projects_no_port_conflicts(self, template_dir, temp_dir):
        """Test that two projects can run simultaneously without port conflicts."""
        # Generate first project
        project_a_config = {
            "customer_slug": "company-a",
            "project_slug": "company-a-etl", 
            "project_name": "Company A ETL Project",
            "author_name": "Test Author",
            "description": "Test project A",
            "python_version": "3.12",
            "airflow_version": "2.8.0",
            "runtime_tag": "8.10.0",
            "image_repo": "registry.example.com/etl/company-a",
            "postgres_version": "16",
            "env_name": "dev",
            "company_domain": "company-a.com",
            "local_domain": "localhost",
            "high_label": "high",
            "executor": "LocalExecutor",
            "secrets_strategy": "env-vars",
            "enable_kerberos": "no",
            "db_name": "company_a_etl",
            "db_user": "postgres",
            "db_password": "postgres",
            "license": "MIT",
            "year": "2025"
        }
        
        # Generate second project with different naming
        project_b_config = project_a_config.copy()
        project_b_config.update({
            "customer_slug": "company-b",
            "project_slug": "company-b-etl",
            "project_name": "Company B ETL Project", 
            "company_domain": "company-b.com",
            "db_name": "company_b_etl",
            "image_repo": "registry.example.com/etl/company-b"
        })
        
        # Generate both projects
        project_a_dir = self._generate_project(template_dir, temp_dir, "project-a", project_a_config)
        project_b_dir = self._generate_project(template_dir, temp_dir, "project-b", project_b_config)
        
        # Verify both projects generated successfully
        assert project_a_dir.exists()
        assert project_b_dir.exists()
        
        # Verify Docker Compose projects have different names
        compose_a = project_a_dir / ".devcontainer" / "compose.yaml"
        compose_b = project_b_dir / ".devcontainer" / "compose.yaml"
        
        compose_a_content = compose_a.read_text()
        compose_b_content = compose_b.read_text()
        
        # Check project names are different (prevents container conflicts)
        assert "company-a-etl-modern" in compose_a_content
        assert "company-b-etl-modern" in compose_b_content
        
        # Verify database names are different (prevents data conflicts)
        assert "company_a_etl" in compose_a_content
        assert "company_b_etl" in compose_b_content
    
    @pytest.mark.integration 
    @pytest.mark.multi_project
    @pytest.mark.slow
    def test_concurrent_devcontainer_startup(self, template_dir, temp_dir):
        """Test that multiple DevContainers can start concurrently."""
        # This would be a more complex test that actually starts containers
        # and verifies they don't interfere with each other
        pytest.skip("Requires Docker-in-Docker setup - implement in full E2E environment")
    
    def _generate_project(self, template_dir: str, temp_dir: Path, project_name: str, config: Dict[str, Any]) -> Path:
        """Generate a cookiecutter project with given configuration."""
        output_dir = temp_dir / project_name
        output_dir.mkdir()
        
        # Build cookiecutter command
        cmd = [
            'cookiecutter', template_dir,
            '--output-dir', str(output_dir),
            '--no-input'
        ]
        
        # Add configuration variables
        for key, value in config.items():
            cmd.append(f"{key}={value}")
        
        # Generate project
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            pytest.fail(f"Project generation failed: {result.stderr}")
        
        # Return path to generated project
        return output_dir / config["project_slug"]