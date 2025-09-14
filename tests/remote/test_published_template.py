"""Remote tests against published template - Validates actual user experience."""

import subprocess
from pathlib import Path
import pytest
import os


class TestPublishedTemplate:
    """Test against published GitHub template, not work-in-progress code."""
    
    @pytest.mark.remote
    def test_main_branch_template_generation(self, temp_dir):
        """Test generation from main branch on GitHub."""
        # This test uses the remote template URL, not local files
        template_url = "https://github.com/Troubladore/data-eng-template.git"
        
        # Use specific branch if specified
        if os.getenv('PYTEST_REMOTE_BRANCH'):
            branch = os.getenv('PYTEST_REMOTE_BRANCH')
            template_url = f"{template_url}@{branch}"
        
        print(f"Testing remote template: {template_url}")
        
        # Generate project using remote template
        cmd = [
            'cookiecutter', template_url,
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        if result.returncode != 0:
            pytest.fail(f"Remote template generation failed: {result.stderr}")
        
        # Verify project was generated
        # Use default values from remote cookiecutter.json
        project_dir = temp_dir / "customer-a-etl"  # Default from remote template
        assert project_dir.exists(), "Project should be generated from remote template"
        
        # Verify key files exist
        key_files = [
            "README.md",
            "CLAUDE.md",
            "pyproject.toml",
            ".devcontainer/devcontainer.json",
            ".devcontainer/compose.yaml",
            "dags/CLAUDE.md",
            "secrets/CLAUDE.md",
            "envs/CLAUDE.md"
        ]
        
        for file_path in key_files:
            full_path = project_dir / file_path
            assert full_path.exists(), f"Key file should exist in remote generation: {file_path}"
        
        # Verify generated content shows remote template characteristics
        readme_content = (project_dir / "README.md").read_text()
        
        # Should show Astronomer-based patterns (not DCSM)
        assert "VS Code DevContainer (Recommended)" in readme_content
        assert "Astronomer" in readme_content
        assert "DevContainer Service Manager" not in readme_content, "Should not contain DCSM references"
        assert "dcm" not in readme_content.lower(), "Should not contain dcm commands"
    
    @pytest.mark.remote
    def test_remote_template_cookiecutter_variables(self, temp_dir):
        """Test that remote template has correct cookiecutter variables."""
        template_url = "https://github.com/Troubladore/data-eng-template.git"
        
        if os.getenv('PYTEST_REMOTE_BRANCH'):
            branch = os.getenv('PYTEST_REMOTE_BRANCH')
            template_url = f"{template_url}@{branch}"
        
        # Generate with custom variables to test remote template flexibility
        custom_config = {
            "customer_slug": "remote-test",
            "env_name": "qa",
            "executor": "KubernetesExecutor",
            "secrets_strategy": "azure-key-vault",
            "enable_kerberos": "yes"
        }
        
        cmd = [
            'cookiecutter', template_url,
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        # Add custom configuration
        for key, value in custom_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        if result.returncode != 0:
            pytest.fail(f"Remote template with custom config failed: {result.stderr}")
        
        # Verify custom values were applied
        project_dir = temp_dir / "remote-test-etl"
        assert project_dir.exists()
        
        # Check that custom values were applied in generated content
        main_claude = project_dir / "CLAUDE.md"
        content = main_claude.read_text()
        
        assert "KubernetesExecutor" in content
        assert "azure-key-vault" in content
        
        # Check Kerberos documentation is properly generated
        kerberos_claude = project_dir / "kerberos" / "CLAUDE.md"
        kerberos_content = kerberos_claude.read_text()
        assert "ENABLED" in kerberos_content, "Kerberos should show as enabled"
    
    @pytest.mark.remote
    @pytest.mark.slow
    def test_remote_generated_project_structure_complete(self, temp_dir):
        """Comprehensive test of remote template project structure."""
        template_url = "https://github.com/Troubladore/data-eng-template.git"
        
        if os.getenv('PYTEST_REMOTE_BRANCH'):
            branch = os.getenv('PYTEST_REMOTE_BRANCH')
            template_url = f"{template_url}@{branch}"
        
        cmd = [
            'cookiecutter', template_url,
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        if result.returncode != 0:
            pytest.fail(f"Remote template generation failed: {result.stderr}")
        
        project_dir = temp_dir / "customer-a-etl"
        
        # Verify complete Astronomer-based project structure
        expected_structure = [
            # Core files
            "README.md", "CLAUDE.md", "pyproject.toml", "astro.config.mjs",
            # DevContainer setup
            ".devcontainer/devcontainer.json", ".devcontainer/compose.yaml",
            # Airflow structure  
            "dags/", "dags/CLAUDE.md",
            # Data transformation
            "dbt/", "dbt/CLAUDE.md", "transforms/", "transforms/CLAUDE.md",
            # Enterprise features
            "secrets/", "secrets/CLAUDE.md", "secrets/azure-key-vault/",
            "kerberos/", "kerberos/CLAUDE.md",
            "envs/", "envs/CLAUDE.md", "envs/dev/", "envs/qa/", "envs/prod/",
            # Kubernetes integration
            "k8s/pod-templates/",
            # CI/CD
            ".ado/pipelines/",
            # Configuration
            "conf/", "conf/config.yaml",
            # Utilities
            "tools/", "tools/where.sh", "scripts/",
        ]
        
        missing_items = []
        for item in expected_structure:
            full_path = project_dir / item
            if not full_path.exists():
                missing_items.append(item)
        
        assert not missing_items, f"Missing items in remote template: {missing_items}"
        
        # Verify tools are executable
        where_script = project_dir / "tools" / "where.sh"
        assert where_script.stat().st_mode & 0o111, "where.sh should be executable"