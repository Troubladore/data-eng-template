"""
Test fingerprinting functionality for Docker image caching optimization.

Validates that the build fingerprint generation works correctly and produces
deterministic results for identical build configurations.
"""

import json
import tempfile
from pathlib import Path

import pytest


class TestFingerprintGeneration:
    """Test the fingerprinting script functionality."""

    def test_fingerprint_script_exists_in_template(self):
        """Test that the fingerprint script exists in the template structure."""
        # Direct file existence check instead of using non-existent validator
        fingerprint_script_path = Path(__file__).parent.parent.parent / "{{cookiecutter.customer_slug}}-etl" / "scripts" / "generate_build_fingerprint.py"
        assert fingerprint_script_path.exists(), f"Fingerprint script should exist at {fingerprint_script_path}"

    def test_fingerprint_script_syntax(self):
        """Test that the fingerprint script has valid Python syntax."""
        script_path = Path(__file__).parent.parent.parent / "{{cookiecutter.customer_slug}}-etl" / "scripts" / "generate_build_fingerprint.py"

        # Basic syntax validation
        with open(script_path, 'r') as f:
            content = f.read()
            compile(content, str(script_path), 'exec')

    def test_fingerprint_deterministic(self):
        """Test that fingerprinting produces consistent results for identical inputs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            # Create mock files
            (project_root / "airflow").mkdir()
            (project_root / "airflow" / "requirements.txt").write_text("apache-airflow==2.8.0\npandas==2.1.0")
            (project_root / "Dockerfile.airflow").write_text("FROM apache/airflow:2.8.0\nCOPY requirements.txt .")
            (project_root / "pyproject.toml").write_text('[project]\nname = "test-project"\nversion = "0.1.0"')

            # Mock cookiecutter.json
            cookiecutter_config = {
                "airflow_version": "2.8.0",
                "python_version": "3.12",
                "postgres_version": "16"
            }
            (project_root / "cookiecutter.json").write_text(json.dumps(cookiecutter_config))

            # Import and test the fingerprinting function
            import sys
            script_path = Path(__file__).parent.parent.parent / "{{cookiecutter.customer_slug}}-etl" / "scripts" / "generate_build_fingerprint.py"

            # Load the module dynamically
            import importlib.util
            spec = importlib.util.spec_from_file_location("fingerprint_module", script_path)
            fingerprint_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(fingerprint_module)

            # Generate fingerprint twice
            fingerprint1 = fingerprint_module.generate_build_fingerprint(project_root)
            fingerprint2 = fingerprint_module.generate_build_fingerprint(project_root)

            assert fingerprint1 == fingerprint2, "Fingerprints should be deterministic"
            assert len(fingerprint1) == 8, "Fingerprint should be 8 characters"

    def test_fingerprint_different_for_different_configs(self):
        """Test that different build configurations produce different fingerprints."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root1 = Path(temp_dir) / "project1"
            project_root2 = Path(temp_dir) / "project2"

            for project_root in [project_root1, project_root2]:
                project_root.mkdir()
                (project_root / "airflow").mkdir()
                (project_root / "Dockerfile.airflow").write_text("FROM apache/airflow:2.8.0\nCOPY requirements.txt .")
                (project_root / "pyproject.toml").write_text('[project]\nname = "test-project"\nversion = "0.1.0"')

            # Different requirements files
            (project_root1 / "airflow" / "requirements.txt").write_text("apache-airflow==2.8.0\npandas==2.1.0")
            (project_root2 / "airflow" / "requirements.txt").write_text("apache-airflow==2.8.0\nnumpy==1.25.0")

            # Same cookiecutter config
            cookiecutter_config = {
                "airflow_version": "2.8.0",
                "python_version": "3.12",
                "postgres_version": "16"
            }
            for project_root in [project_root1, project_root2]:
                (project_root / "cookiecutter.json").write_text(json.dumps(cookiecutter_config))

            # Import the fingerprinting function
            script_path = Path(__file__).parent.parent.parent / "{{cookiecutter.customer_slug}}-etl" / "scripts" / "generate_build_fingerprint.py"

            import importlib.util
            spec = importlib.util.spec_from_file_location("fingerprint_module", script_path)
            fingerprint_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(fingerprint_module)

            # Generate fingerprints
            fingerprint1 = fingerprint_module.generate_build_fingerprint(project_root1)
            fingerprint2 = fingerprint_module.generate_build_fingerprint(project_root2)

            assert fingerprint1 != fingerprint2, "Different configurations should produce different fingerprints"

    def test_image_name_generation(self):
        """Test that image name generation works correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            # Mock cookiecutter.json
            cookiecutter_config = {
                "airflow_version": "2.8.0",
                "python_version": "3.12",
                "postgres_version": "16"
            }
            (project_root / "cookiecutter.json").write_text(json.dumps(cookiecutter_config))

            # Import the image name generation function
            script_path = Path(__file__).parent.parent.parent / "{{cookiecutter.customer_slug}}-etl" / "scripts" / "generate_build_fingerprint.py"

            import importlib.util
            spec = importlib.util.spec_from_file_location("fingerprint_module", script_path)
            fingerprint_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(fingerprint_module)

            # Test image name generation
            test_fingerprint = "abc12345"
            image_name = fingerprint_module.generate_image_name(test_fingerprint, project_root)

            expected_pattern = "data-eng-airflow-dev:2.8.0-py3.12-abc12345"
            assert image_name == expected_pattern, f"Expected {expected_pattern}, got {image_name}"

    def test_fingerprint_normalization(self):
        """Test that customer-specific content is properly normalized."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            # Create files with customer-specific content
            (project_root / "airflow").mkdir()
            (project_root / "airflow" / "requirements.txt").write_text("apache-airflow==2.8.0")

            # Dockerfile with customer references
            dockerfile_content = """FROM apache/airflow:2.8.0
COPY {{cookiecutter.customer_slug}}-requirements.txt .
RUN pip install customer-specific-package"""
            (project_root / "Dockerfile.airflow").write_text(dockerfile_content)

            # pyproject.toml with customer name
            pyproject_content = '''[project]
name = "acme-corp-etl"
description = "Data pipeline for ACME Corporation"
version = "0.1.0"'''
            (project_root / "pyproject.toml").write_text(pyproject_content)

            cookiecutter_config = {
                "airflow_version": "2.8.0",
                "python_version": "3.12",
                "postgres_version": "16"
            }
            (project_root / "cookiecutter.json").write_text(json.dumps(cookiecutter_config))

            # Import normalization functions
            script_path = Path(__file__).parent.parent.parent / "{{cookiecutter.customer_slug}}-etl" / "scripts" / "generate_build_fingerprint.py"

            import importlib.util
            spec = importlib.util.spec_from_file_location("fingerprint_module", script_path)
            fingerprint_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(fingerprint_module)

            # Test Dockerfile normalization
            normalized_dockerfile = fingerprint_module._normalize_dockerfile(dockerfile_content)
            assert "NORMALIZED_CUSTOMER" in normalized_dockerfile
            assert "{{cookiecutter.customer_slug}}" not in normalized_dockerfile

            # Test pyproject.toml normalization
            normalized_pyproject = fingerprint_module._normalize_pyproject(pyproject_content)
            assert "NORMALIZED_PROJECT" in normalized_pyproject
            assert "NORMALIZED_DESCRIPTION" in normalized_pyproject
            assert "acme-corp-etl" not in normalized_pyproject


class TestFingerprintIntegration:
    """Test fingerprinting integration with post-generation hooks."""

    def test_post_gen_hook_has_fingerprint_logic(self):
        """Test that post-generation hook includes fingerprinting logic."""
        hook_file = Path(__file__).parent.parent.parent / "hooks" / "post_gen_project.py"

        with open(hook_file, 'r') as f:
            content = f.read()

        # Check for fingerprinting-related code
        assert "generate_build_fingerprint.py" in content
        assert "Build fingerprinting" in content
        assert "shared_image_name" in content

    def test_fingerprint_fallback_behavior(self):
        """Test that the system gracefully handles fingerprinting failures."""
        hook_file = Path(__file__).parent.parent.parent / "hooks" / "post_gen_project.py"

        with open(hook_file, 'r') as f:
            content = f.read()

        # Check for proper error handling
        assert "except subprocess.CalledProcessError" in content
        assert "Warning: Build fingerprinting failed" in content
        assert "Continuing with project-specific image names" in content