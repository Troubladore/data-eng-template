"""Unit tests for template syntax validation - Lightning fast (< 1s each)."""

import json
from pathlib import Path
import pytest


class TestTemplateSyntax:
    """Fast validation of template syntax and structure."""
    
    @pytest.mark.unit
    @pytest.mark.smoke
    def test_cookiecutter_json_valid(self, template_dir):
        """Verify cookiecutter.json is valid JSON."""
        if template_dir.startswith('http'):
            pytest.skip("Remote template testing - syntax validated in CI")
            
        cookiecutter_file = Path(template_dir) / "cookiecutter.json"
        assert cookiecutter_file.exists(), "cookiecutter.json must exist"
        
        with open(cookiecutter_file) as f:
            config = json.load(f)
            
        # Verify required fields exist
        required_fields = [
            "customer_slug", "project_slug", "project_name", 
            "author_name", "python_version", "airflow_version"
        ]
        
        for field in required_fields:
            assert field in config, f"Required field '{field}' missing from cookiecutter.json"
    
    @pytest.mark.unit
    @pytest.mark.smoke
    def test_template_directory_exists(self, template_dir):
        """Verify template directory structure exists."""
        if template_dir.startswith('http'):
            pytest.skip("Remote template testing - structure validated elsewhere")
            
        template_path = Path(template_dir)
        project_template_dir = template_path / "{{cookiecutter.customer_slug}}-etl"
        
        assert template_path.exists(), "Template directory must exist"
        assert project_template_dir.exists(), "Project template directory must exist"
        
        # Verify key template files exist
        key_files = [
            "cookiecutter.json",
            "{{cookiecutter.customer_slug}}-etl/README.md",
            "{{cookiecutter.customer_slug}}-etl/CLAUDE.md",
            "{{cookiecutter.customer_slug}}-etl/pyproject.toml",
            "hooks/post_gen_project.py"
        ]
        
        for file_path in key_files:
            full_path = template_path / file_path
            assert full_path.exists(), f"Required template file missing: {file_path}"
    
    @pytest.mark.unit
    def test_jinja_template_syntax(self, template_dir):
        """Verify Jinja templates don't have syntax conflicts."""
        if template_dir.startswith('http'):
            pytest.skip("Remote template testing")
            
        template_path = Path(template_dir)
        project_dir = template_path / "{{cookiecutter.customer_slug}}-etl"
        
        # Check for common Jinja/Docker format conflicts
        problematic_patterns = [
            "{{.Names}}",  # Docker format that conflicts with Jinja
            "{{.Status}}",
            "{{.Image}}",
        ]
        
        # Scan shell scripts for Docker format conflicts
        for script_file in project_dir.rglob("*.sh"):
            content = script_file.read_text()
            for pattern in problematic_patterns:
                assert pattern not in content, f"Docker format conflict in {script_file}: {pattern}"