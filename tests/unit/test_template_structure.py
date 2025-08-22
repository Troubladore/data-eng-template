"""Unit tests for template directory structure validation."""

from pathlib import Path
import pytest


class TestTemplateStructure:
    """Test the cookiecutter template directory structure."""
    
    def test_template_root_files(self, template_dir: Path):
        """Test that required root files exist."""
        required_files = [
            "cookiecutter.json",
            "CLAUDE.md", 
            "README.md",
            "DISTRIBUTED_GUIDANCE_STRATEGY.md",
            "TESTING_STRATEGY.md"
        ]
        
        for file_name in required_files:
            file_path = template_dir / file_name
            assert file_path.exists(), f"Required file {file_name} is missing"
            assert file_path.is_file(), f"{file_name} should be a file"
    
    def test_hooks_directory(self, template_dir: Path):
        """Test hooks directory structure."""
        hooks_dir = template_dir / "hooks"
        assert hooks_dir.exists(), "hooks/ directory must exist"
        assert hooks_dir.is_dir(), "hooks/ must be a directory"
        
        # Check for post-generation hook
        post_gen_hook = hooks_dir / "post_gen_project.py"
        assert post_gen_hook.exists(), "post_gen_project.py hook must exist"
        assert post_gen_hook.is_file(), "post_gen_project.py must be a file"
    
    def test_template_project_directory(self, template_dir: Path):
        """Test that the templated project directory exists."""
        template_project_dir = template_dir / "{{cookiecutter.repo_slug}}"
        assert template_project_dir.exists(), "{{cookiecutter.repo_slug}}/ directory must exist"
        assert template_project_dir.is_dir(), "{{cookiecutter.repo_slug}}/ must be a directory"
    
    def test_template_project_structure(self, template_dir: Path):
        """Test the structure of the templated project."""
        project_dir = template_dir / "{{cookiecutter.repo_slug}}"
        
        required_items = [
            # Files
            "CLAUDE.md",
            "Makefile",
            "pyproject.toml",
            
            # Directories
            "airflow/",
            "dags/",
            "dbt/",
            "docs/",
            "scripts/",
            "tests/", 
            "transforms/"
        ]
        
        for item in required_items:
            item_path = project_dir / item
            assert item_path.exists(), f"Required item {item} missing from project template"
    
    def test_guidance_files_distribution(self, template_dir: Path):
        """Test that CLAUDE.md files are distributed correctly."""
        project_dir = template_dir / "{{cookiecutter.repo_slug}}"
        
        expected_guidance_files = [
            "CLAUDE.md",
            "dags/CLAUDE.md",
            "dbt/CLAUDE.md",
            "transforms/CLAUDE.md", 
            "scripts/CLAUDE.md"
        ]
        
        for guidance_file in expected_guidance_files:
            guidance_path = project_dir / guidance_file
            assert guidance_path.exists(), f"Guidance file {guidance_file} is missing"
            assert guidance_path.is_file(), f"Guidance file {guidance_file} should be a file"
    
    def test_dags_directory_structure(self, template_dir: Path):
        """Test DAGs directory has required structure."""
        dags_dir = template_dir / "{{cookiecutter.repo_slug}}" / "dags"
        
        # Should have guidance and example DAG
        assert (dags_dir / "CLAUDE.md").exists()
        assert (dags_dir / "example_dag.py").exists()
    
    def test_dbt_directory_structure(self, template_dir: Path):
        """Test dbt directory has required structure.""" 
        dbt_dir = template_dir / "{{cookiecutter.repo_slug}}" / "dbt"
        
        required_items = [
            "CLAUDE.md",
            "dbt_project.yml",
            "profiles-example.yml",
            "models/",
            "models/bronze/",
            "models/silver/", 
            "models/gold/"
        ]
        
        for item in required_items:
            item_path = dbt_dir / item
            assert item_path.exists(), f"dbt item {item} is missing"
    
    def test_transforms_directory_structure(self, template_dir: Path):
        """Test transforms directory has required structure."""
        transforms_dir = template_dir / "{{cookiecutter.repo_slug}}" / "transforms"
        
        required_items = [
            "CLAUDE.md",
            "README.md",
            "__init__.py",
            "models.py"
        ]
        
        for item in required_items:
            item_path = transforms_dir / item
            assert item_path.exists(), f"transforms item {item} is missing"
    
    def test_scripts_directory_structure(self, template_dir: Path):
        """Test scripts directory has required structure."""
        scripts_dir = template_dir / "{{cookiecutter.repo_slug}}" / "scripts"
        
        required_items = [
            "CLAUDE.md",
            "airflow-cli.sh",
            "psql.sh"
        ]
        
        for item in required_items:
            item_path = scripts_dir / item
            assert item_path.exists(), f"scripts item {item} is missing"
    
    def test_tests_directory_structure(self, template_dir: Path):
        """Test tests directory has basic structure."""
        tests_dir = template_dir / "{{cookiecutter.repo_slug}}" / "tests"
        
        # Should have at least one test file
        test_files = list(tests_dir.glob("test_*.py"))
        assert len(test_files) > 0, "tests/ directory should contain test files"


class TestFilePermissions:
    """Test file permissions are set correctly."""
    
    def test_script_files_executable(self, template_dir: Path):
        """Test that shell scripts are executable."""
        scripts_dir = template_dir / "{{cookiecutter.repo_slug}}" / "scripts"
        
        shell_scripts = list(scripts_dir.glob("*.sh"))
        
        for script in shell_scripts:
            # Check if file has execute permission
            assert script.stat().st_mode & 0o111, f"Script {script.name} should be executable"
    
    def test_python_files_not_executable(self, template_dir: Path):
        """Test that Python files are not executable (except scripts in scripts/)."""
        project_dir = template_dir / "{{cookiecutter.repo_slug}}"
        
        # Find all Python files except in scripts/
        python_files = []
        for py_file in project_dir.rglob("*.py"):
            # Skip files in scripts/ directory as they might be executable utilities
            if "scripts/" not in str(py_file.relative_to(project_dir)):
                python_files.append(py_file)
        
        for py_file in python_files:
            # Python files should generally not be executable
            mode = py_file.stat().st_mode
            # Check that execute bit is not set for group/others (owner might have it)
            assert not (mode & 0o011), f"Python file {py_file.name} should not be executable by group/others"


class TestTemplateConsistency:
    """Test consistency across template files."""
    
    def test_consistent_naming_patterns(self, template_dir: Path):
        """Test that file naming follows consistent patterns."""
        project_dir = template_dir / "{{cookiecutter.repo_slug}}"
        
        # All Python files should use underscores
        python_files = list(project_dir.rglob("*.py"))
        for py_file in python_files:
            filename = py_file.name
            if filename != "__init__.py":  # Skip __init__.py special case
                assert "_" in filename or filename.islower(), f"Python file {filename} should use underscores or be lowercase"
        
        # Shell scripts should use hyphens
        shell_scripts = list(project_dir.rglob("*.sh"))
        for script in shell_scripts:
            filename = script.stem  # Without extension
            if len(filename) > 1:  # Multi-character names
                assert "-" in filename or filename.islower(), f"Shell script {filename} should use hyphens or be lowercase"
    
    def test_no_empty_directories(self, template_dir: Path):
        """Test that template doesn't contain empty directories."""
        project_dir = template_dir / "{{cookiecutter.repo_slug}}"
        
        # Allow certain directories to be empty (e.g., plugins, logs)
        allowed_empty_dirs = {"plugins", "logs", "__pycache__"}
        
        for dir_path in project_dir.rglob("*"):
            if dir_path.is_dir() and dir_path.name not in allowed_empty_dirs:
                # Check if directory has any files (directly or in subdirectories)
                has_files = any(dir_path.rglob("*"))
                assert has_files, f"Directory {dir_path.name} appears to be empty"