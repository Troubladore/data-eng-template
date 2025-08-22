"""Unit tests for CLAUDE.md guidance file validation."""

from pathlib import Path
import re
from typing import List
import pytest


class TestGuidanceFileContent:
    """Test the content of guidance files."""
    
    def test_outer_layer_guidance_exists(self, template_dir: Path):
        """Test that outer layer CLAUDE.md exists and has content."""
        claude_md = template_dir / "CLAUDE.md"
        assert claude_md.exists(), "Outer layer CLAUDE.md must exist"
        
        content = claude_md.read_text()
        assert len(content) > 100, "CLAUDE.md should have substantial content"
        
        # Should identify itself as template guidance
        assert "template" in content.lower(), "Should identify as template guidance"
        assert "cookiecutter" in content.lower(), "Should mention cookiecutter"
    
    def test_inner_layer_guidance_templates(self, template_dir: Path):
        """Test that inner layer CLAUDE.md templates have proper structure."""
        project_dir = template_dir / "{{cookiecutter.repo_slug}}"
        
        guidance_files = [
            "CLAUDE.md",
            "dags/CLAUDE.md", 
            "dbt/CLAUDE.md",
            "transforms/CLAUDE.md",
            "scripts/CLAUDE.md"
        ]
        
        for guidance_file in guidance_files:
            file_path = project_dir / guidance_file
            assert file_path.exists(), f"Guidance file {guidance_file} must exist"
            
            content = file_path.read_text()
            assert len(content) > 50, f"Guidance file {guidance_file} should have content"
            
            # Should use cookiecutter variables
            assert "{{cookiecutter." in content, f"Guidance file {guidance_file} should use cookiecutter variables"
    
    def test_guidance_file_headers(self, template_dir: Path):
        """Test that guidance files have appropriate headers."""
        project_dir = template_dir / "{{cookiecutter.repo_slug}}"
        
        expected_headers = {
            "CLAUDE.md": "# {{cookiecutter.project_name}}",
            "dags/CLAUDE.md": "# Airflow DAG Development Guidance",
            "dbt/CLAUDE.md": "# dbt Modeling Guidance", 
            "transforms/CLAUDE.md": "# SQLModel and Pydantic Data Models",
            "scripts/CLAUDE.md": "# Helper Scripts"
        }
        
        for guidance_file, expected_header in expected_headers.items():
            file_path = project_dir / guidance_file
            content = file_path.read_text()
            
            # Check if header is present (allowing for variations)
            header_words = expected_header.lower().split()
            content_lower = content.lower()
            
            for word in header_words:
                if word not in ["#", "{{cookiecutter.project_name}}"]:
                    assert word in content_lower, f"Header word '{word}' missing from {guidance_file}"
    
    def test_cookiecutter_variables_syntax(self, template_dir: Path):
        """Test that cookiecutter variables use correct syntax."""
        project_dir = template_dir / "{{cookiecutter.repo_slug}}"
        
        guidance_files = list(project_dir.glob("**/CLAUDE.md"))
        
        # Pattern to match cookiecutter variables
        cookiecutter_pattern = r'\{\{\s*cookiecutter\.[a-zA-Z_][a-zA-Z0-9_]*\s*\}\}'
        
        for guidance_file in guidance_files:
            content = guidance_file.read_text()
            
            # Find all cookiecutter variable references
            variables = re.findall(r'\{\{\s*cookiecutter\.[^}]+\s*\}\}', content)
            
            for var in variables:
                # Check syntax
                assert re.match(cookiecutter_pattern, var), f"Invalid cookiecutter variable syntax: {var} in {guidance_file.name}"
    
    def test_no_template_syntax_conflicts(self, template_dir: Path):
        """Test that there are no unescaped Jinja conflicts."""
        project_dir = template_dir / "{{cookiecutter.repo_slug}}"
        
        guidance_files = list(project_dir.glob("**/CLAUDE.md"))
        
        for guidance_file in guidance_files:
            content = guidance_file.read_text()
            
            # Look for potential dbt/Jinja conflicts that aren't cookiecutter variables
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                # Skip cookiecutter variables
                if "{{cookiecutter." in line:
                    continue
                    
                # Look for unescaped {{ }} that might cause conflicts
                if "{{" in line and "}}" in line and "{% raw %}" not in line:
                    # This might be a template conflict
                    pytest.fail(f"Potential template syntax conflict in {guidance_file.name} line {line_num}: {line}")


class TestGuidanceContentQuality:
    """Test the quality and completeness of guidance content."""
    
    def test_guidance_mentions_layer_context(self, template_dir: Path):
        """Test that layer-specific guidance mentions its context."""
        project_dir = template_dir / "{{cookiecutter.repo_slug}}"
        
        layer_contexts = {
            "dags/CLAUDE.md": ["airflow", "dag", "pipeline"],
            "dbt/CLAUDE.md": ["dbt", "model", "transformation", "medallion"],
            "transforms/CLAUDE.md": ["sqlmodel", "pydantic", "validation"],
            "scripts/CLAUDE.md": ["script", "utility", "operations"]
        }
        
        for guidance_file, expected_terms in layer_contexts.items():
            file_path = project_dir / guidance_file
            content = file_path.read_text().lower()
            
            for term in expected_terms:
                assert term in content, f"Layer guidance {guidance_file} should mention '{term}'"
    
    def test_guidance_includes_development_info(self, template_dir: Path):
        """Test that guidance includes development environment information."""
        project_dir = template_dir / "{{cookiecutter.repo_slug}}"
        
        layer_files = ["dags/CLAUDE.md", "dbt/CLAUDE.md", "transforms/CLAUDE.md", "scripts/CLAUDE.md"]
        
        for guidance_file in layer_files:
            file_path = project_dir / guidance_file
            content = file_path.read_text()
            
            # Should mention development environment or versions
            development_indicators = [
                "{{cookiecutter.python_version}}",
                "{{cookiecutter.airflow_version}}", 
                "{{cookiecutter.postgres_version}}",
                "{{cookiecutter.author_name}}",
                "development", "environment"
            ]
            
            has_dev_info = any(indicator in content for indicator in development_indicators)
            assert has_dev_info, f"Guidance file {guidance_file} should include development environment information"
    
    def test_guidance_cross_references(self, template_dir: Path):
        """Test that guidance files appropriately cross-reference each other."""
        project_dir = template_dir / "{{cookiecutter.repo_slug}}"
        
        main_guidance = project_dir / "CLAUDE.md"
        main_content = main_guidance.read_text()
        
        # Main guidance should reference other guidance files
        layer_references = [
            "dags/CLAUDE.md",
            "dbt/CLAUDE.md", 
            "transforms/CLAUDE.md",
            "scripts/CLAUDE.md"
        ]
        
        for reference in layer_references:
            assert reference in main_content, f"Main guidance should reference {reference}"
    
    def test_guidance_actionability(self, template_dir: Path):
        """Test that guidance provides actionable information."""
        project_dir = template_dir / "{{cookiecutter.repo_slug}}"
        
        guidance_files = list(project_dir.glob("**/CLAUDE.md"))
        
        # Look for actionable language patterns
        actionable_patterns = [
            r'##\s+[A-Z]',  # Headers indicating sections
            r'-\s+\*\*',    # Bold bullet points
            r'`[^`]+`',     # Code snippets
            r'```',         # Code blocks
        ]
        
        for guidance_file in guidance_files:
            content = guidance_file.read_text()
            
            actionable_elements = 0
            for pattern in actionable_patterns:
                matches = re.findall(pattern, content)
                actionable_elements += len(matches)
            
            assert actionable_elements > 3, f"Guidance file {guidance_file.name} should have more actionable elements (headers, code, etc.)"


class TestGuidanceConsistency:
    """Test consistency across guidance files."""
    
    def test_consistent_project_name_usage(self, template_dir: Path):
        """Test that project name is used consistently."""
        project_dir = template_dir / "{{cookiecutter.repo_slug}}"
        
        guidance_files = list(project_dir.glob("**/CLAUDE.md"))
        
        for guidance_file in guidance_files:
            content = guidance_file.read_text()
            
            # If project name is referenced, it should use the cookiecutter variable
            if "project" in content.lower() and "name" in content.lower():
                # Should use the variable, not hardcode a name
                assert "{{cookiecutter.project_name}}" in content, f"Guidance file {guidance_file.name} should use cookiecutter variable for project name"
    
    def test_consistent_author_attribution(self, template_dir: Path):
        """Test that author is consistently attributed."""
        project_dir = template_dir / "{{cookiecutter.repo_slug}}"
        
        layer_files = ["dags/CLAUDE.md", "dbt/CLAUDE.md", "transforms/CLAUDE.md", "scripts/CLAUDE.md"]
        
        for guidance_file in layer_files:
            file_path = project_dir / guidance_file
            content = file_path.read_text()
            
            # Should reference author consistently
            if "author" in content.lower():
                assert "{{cookiecutter.author_name}}" in content, f"Guidance file {guidance_file} should use cookiecutter variable for author"
    
    def test_consistent_formatting_style(self, template_dir: Path):
        """Test that guidance files follow consistent formatting."""
        project_dir = template_dir / "{{cookiecutter.repo_slug}}"
        
        guidance_files = list(project_dir.glob("**/CLAUDE.md"))
        
        for guidance_file in guidance_files:
            content = guidance_file.read_text()
            
            # Check for consistent heading style (should use # for main headers)
            lines = content.split('\n')
            for line in lines:
                if line.startswith('#'):
                    # Headers should have space after #
                    assert re.match(r'^#+\s', line), f"Header in {guidance_file.name} should have space after #: {line}"