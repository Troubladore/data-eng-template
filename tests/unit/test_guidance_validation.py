"""Unit tests for CLAUDE.md documentation validation - Mission critical for AI assistance."""

from pathlib import Path
import pytest
import re


class TestGuidanceValidation:
    """Validate CLAUDE.md files for consistency and quality."""
    
    @pytest.mark.unit
    @pytest.mark.guidance
    @pytest.mark.smoke
    def test_all_claude_md_files_exist(self, template_dir):
        """Verify all expected CLAUDE.md files exist in generated template."""
        if template_dir.startswith('http'):
            pytest.skip("Remote template testing")
            
        template_path = Path(template_dir)
        project_dir = template_path / "{{cookiecutter.customer_slug}}-etl"
        
        # Expected CLAUDE.md locations in generated projects
        expected_claude_files = [
            "CLAUDE.md",                    # Main project guidance
            "dags/CLAUDE.md",              # Airflow DAG guidance  
            "dbt/CLAUDE.md",               # dbt transformation guidance
            "transforms/CLAUDE.md",        # SQLModel guidance
            "scripts/CLAUDE.md",           # Operational scripts guidance
            "secrets/CLAUDE.md",           # Secrets management guidance
            "kerberos/CLAUDE.md",          # Kerberos authentication guidance
            "envs/CLAUDE.md",             # Environment configuration guidance
        ]
        
        missing_files = []
        for claude_file in expected_claude_files:
            full_path = project_dir / claude_file
            if not full_path.exists():
                missing_files.append(claude_file)
        
        assert not missing_files, f"Missing CLAUDE.md files: {missing_files}"
    
    @pytest.mark.unit
    @pytest.mark.guidance
    def test_claude_md_structure_consistency(self, template_dir):
        """Verify CLAUDE.md files follow consistent structure patterns."""
        if template_dir.startswith('http'):
            pytest.skip("Remote template testing")
            
        template_path = Path(template_dir)
        project_dir = template_path / "{{cookiecutter.customer_slug}}-etl"
        
        claude_files = list(project_dir.rglob("CLAUDE.md"))
        assert len(claude_files) >= 8, "Should have multiple CLAUDE.md files"
        
        for claude_file in claude_files:
            content = claude_file.read_text()
            
            # Verify file has substantive content
            assert len(content) > 200, f"CLAUDE.md too short: {claude_file.relative_to(project_dir)}"
            
            # Verify markdown headers exist
            assert re.search(r'^#\s+', content, re.MULTILINE), f"No main header in {claude_file.name}"
            
            # Verify no placeholder text left
            placeholder_patterns = [
                "TODO", "FIXME", "PLACEHOLDER", "TBD", 
                "Lorem ipsum", "{{", "}}"
            ]
            
            for pattern in placeholder_patterns:
                if pattern in content and not self._is_valid_cookiecutter_variable(content, pattern):
                    pytest.fail(f"Placeholder text '{pattern}' found in {claude_file.relative_to(project_dir)}")
    
    @pytest.mark.unit
    @pytest.mark.guidance
    def test_main_claude_md_covers_astronomer_workflow(self, template_dir):
        """Verify main CLAUDE.md covers Astronomer development workflow."""
        if template_dir.startswith('http'):
            pytest.skip("Remote template testing")
            
        template_path = Path(template_dir)
        main_claude = template_path / "{{cookiecutter.customer_slug}}-etl" / "CLAUDE.md"
        
        content = main_claude.read_text()
        
        # Must mention VS Code DevContainer as recommended approach
        assert "VS Code DevContainer" in content or "DevContainer" in content
        assert "Recommended" in content or "recommended" in content
        
        # Must mention Astronomer patterns
        assert "Astronomer" in content or "astro dev" in content
        
        # Must cover the three development approaches
        dev_approaches = ["DevContainer", "Astronomer", "Docker Compose"]
        for approach in dev_approaches:
            assert approach in content, f"Main CLAUDE.md should mention {approach}"
        
        # Must have clear project structure guidance
        assert "dags/" in content
        assert "transforms/" in content
        assert "scripts/" in content
    
    @pytest.mark.unit
    @pytest.mark.guidance
    def test_secrets_guidance_covers_strategies(self, template_dir):
        """Verify secrets CLAUDE.md covers all configured strategies."""
        if template_dir.startswith('http'):
            pytest.skip("Remote template testing")
            
        template_path = Path(template_dir)
        secrets_claude = template_path / "{{cookiecutter.customer_slug}}-etl" / "secrets" / "CLAUDE.md"
        
        content = secrets_claude.read_text()
        
        # Must cover the secrets strategies available in cookiecutter.json
        strategies = ["azure-key-vault", "external-secrets-operator", "env-vars"]
        
        for strategy in strategies:
            # Convert to readable form for documentation
            readable_strategy = strategy.replace('-', ' ').title().replace(' ', ' ')
            assert strategy in content or readable_strategy in content, \
                f"Secrets guidance should cover {strategy}"
        
        # Must have practical examples
        assert "```" in content, "Should have code examples"
        assert "Example" in content or "example" in content
    
    @pytest.mark.unit
    @pytest.mark.guidance
    def test_kerberos_guidance_conditional_content(self, template_dir):
        """Verify Kerberos CLAUDE.md handles enabled/disabled states."""
        if template_dir.startswith('http'):
            pytest.skip("Remote template testing")
            
        template_path = Path(template_dir)
        kerberos_claude = template_path / "{{cookiecutter.customer_slug}}-etl" / "kerberos" / "CLAUDE.md"
        
        content = kerberos_claude.read_text()
        
        # Must have conditional content for enabled/disabled states
        jinja_patterns = [
            "{% if cookiecutter.enable_kerberos == \"yes\" %}",
            "{% else %}",
            "{% endif %}"
        ]
        
        for pattern in jinja_patterns:
            assert pattern in content, f"Kerberos guidance should have conditional Jinja: {pattern}"
        
        # Must cover both scenarios
        assert "ENABLED" in content or "Enabled" in content
        assert "DISABLED" in content or "Disabled" in content
    
    @pytest.mark.unit
    @pytest.mark.guidance
    def test_environment_guidance_covers_all_envs(self, template_dir):
        """Verify environment CLAUDE.md covers all configured environments."""
        if template_dir.startswith('http'):
            pytest.skip("Remote template testing")
            
        template_path = Path(template_dir)
        envs_claude = template_path / "{{cookiecutter.customer_slug}}-etl" / "envs" / "CLAUDE.md"
        
        content = envs_claude.read_text()
        
        # Must cover the environments available in cookiecutter.json
        environments = ["dev", "int", "qa", "prod"]
        
        for env in environments:
            assert env in content, f"Environment guidance should mention {env}"
        
        # Must explain configuration patterns
        assert "airflow_settings.yaml" in content
        assert "k8s-values.patch.yaml" in content
        assert ".env.example" in content
    
    @pytest.mark.unit
    @pytest.mark.guidance
    def test_distributed_guidance_cross_references(self, template_dir):
        """Verify CLAUDE.md files properly cross-reference each other."""
        if template_dir.startswith('http'):
            pytest.skip("Remote template testing")
            
        template_path = Path(template_dir)
        project_dir = template_path / "{{cookiecutter.customer_slug}}-etl"
        
        # Main CLAUDE.md should reference component guidance
        main_claude = project_dir / "CLAUDE.md"
        main_content = main_claude.read_text()
        
        component_references = [
            "dags/CLAUDE.md",
            "transforms/CLAUDE.md", 
            "scripts/CLAUDE.md",
            "secrets/CLAUDE.md"
        ]
        
        reference_count = 0
        for ref in component_references:
            if ref in main_content:
                reference_count += 1
        
        assert reference_count >= 2, "Main CLAUDE.md should reference component guidance files"
    
    def _is_valid_cookiecutter_variable(self, content: str, pattern: str) -> bool:
        """Check if {{ }} pattern is a valid cookiecutter variable."""
        if pattern not in ["{{", "}}"]:
            return False
            
        # Count valid cookiecutter variables vs stray braces
        cookiecutter_vars = re.findall(r'\{\{cookiecutter\.[^}]+\}\}', content)
        total_braces = content.count("{{") + content.count("}}")
        
        # If most braces are valid cookiecutter variables, allow it
        return len(cookiecutter_vars) * 2 >= total_braces * 0.8