"""
Integration tests for Docker cleanup and naming system.
Tests Docker container creation, labeling, and cleanup script functionality.
"""
import pytest
import tempfile
import shutil
import os
import subprocess
import time
from pathlib import Path
from cookiecutter.main import cookiecutter


class TestDockerCleanupIntegration:
    """Integration tests for Docker cleanup system."""

    @pytest.fixture
    def template_dir(self):
        """Return path to the cookiecutter template."""
        return str(Path(__file__).parent.parent.parent)

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for generated projects."""
        temp_dir = tempfile.mkdtemp(prefix="test_docker_cleanup_")
        yield temp_dir
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def cleanup_scripts(self):
        """Return paths to cleanup scripts."""
        base_path = Path(__file__).parent.parent.parent
        return {
            'shallow': base_path / 'tests' / 'utils' / 'cleanup-shallow.sh',
            'deep': base_path / 'tests' / 'utils' / 'cleanup-deep.sh'
        }

    def _run_command(self, cmd, cwd=None, timeout=60):
        """Run a shell command with timeout."""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd
            )
            return result
        except subprocess.TimeoutExpired:
            pytest.fail(f"Command timed out after {timeout}s: {cmd}")

    def _get_docker_containers(self, filter_label=None):
        """Get Docker containers matching filter."""
        cmd = "docker ps -a --format '{{.Names}}'"
        if filter_label:
            cmd += f" --filter 'label={filter_label}'"

        result = self._run_command(cmd)
        if result.returncode != 0:
            return []

        return [name.strip() for name in result.stdout.split('\n') if name.strip()]

    def _get_docker_images(self, filter_reference=None):
        """Get Docker images matching filter."""
        cmd = "docker images --format '{{.Repository}}:{{.Tag}}'"
        if filter_reference:
            cmd += f" --filter 'reference={filter_reference}'"

        result = self._run_command(cmd)
        if result.returncode != 0:
            return []

        return [img.strip() for img in result.stdout.split('\n') if img.strip() and img != '<none>:<none>']

    @pytest.mark.integration
    @pytest.mark.skipif(shutil.which("docker") is None, reason="Docker not available")
    def test_testing_mode_docker_naming(self, template_dir, temp_output_dir):
        """Test that testing mode creates properly named Docker artifacts."""
        project_slug = "docker-test-integration"

        # Generate project in testing mode
        result_dir = cookiecutter(
            template_dir,
            no_input=True,
            output_dir=temp_output_dir,
            extra_context={
                'deployment_mode': 'testing',
                'customer_slug': project_slug.replace('-etl', '')
            }
        )

        # Try to start Docker Compose (don't wait for full startup)
        compose_dir = Path(result_dir) / '.devcontainer'
        result = self._run_command(
            "docker compose up -d --no-deps postgres",
            cwd=str(compose_dir),
            timeout=30
        )

        # Should start without naming errors
        assert result.returncode == 0, f"Docker compose failed: {result.stderr}"

        try:
            # Check that containers have correct names and labels
            containers = self._get_docker_containers("de-template.deployment=testing")

            # Should have at least the postgres container
            postgres_containers = [c for c in containers if 'postgres-test' in c and project_slug in c]
            assert len(postgres_containers) >= 1, f"Expected postgres-test container, found: {containers}"

            # Check specific container naming
            expected_container = f"{project_slug}-postgres-test"
            assert expected_container in containers, f"Expected {expected_container} in {containers}"

            # Verify labels are correct
            result = self._run_command(
                f"docker inspect {expected_container} --format '{{{{json .Config.Labels}}}}'"
            )
            if result.returncode == 0:
                import json
                labels = json.loads(result.stdout.strip())
                assert labels.get('de-template.project') == project_slug
                assert labels.get('de-template.deployment') == 'testing'
                assert labels.get('de-template.service') == 'postgres'

        finally:
            # Cleanup - stop and remove containers
            self._run_command(
                "docker compose down -v --remove-orphans",
                cwd=str(compose_dir),
                timeout=30
            )

    @pytest.mark.integration
    @pytest.mark.skipif(shutil.which("docker") is None, reason="Docker not available")
    def test_production_mode_docker_naming(self, template_dir, temp_output_dir):
        """Test that production mode creates properly named Docker artifacts without test suffixes."""
        project_slug = "docker-prod-integration"

        # Generate project in production mode
        result_dir = cookiecutter(
            template_dir,
            no_input=True,
            output_dir=temp_output_dir,
            extra_context={
                'deployment_mode': 'production',
                'customer_slug': project_slug.replace('-etl', '')
            }
        )

        # Try to start Docker Compose postgres service
        compose_dir = Path(result_dir) / '.devcontainer'
        result = self._run_command(
            "docker compose up -d --no-deps postgres",
            cwd=str(compose_dir),
            timeout=30
        )

        # Should start without naming errors
        assert result.returncode == 0, f"Docker compose failed: {result.stderr}"

        try:
            # Check that containers have correct names (no -test suffix)
            containers = self._get_docker_containers("de-template.deployment=production")

            # Should have the postgres container without -test suffix
            expected_container = f"{project_slug}-postgres"
            assert expected_container in containers, f"Expected {expected_container} in {containers}"

            # Should NOT have -test suffix
            test_container = f"{project_slug}-postgres-test"
            assert test_container not in containers, f"Found unexpected test container: {test_container}"

        finally:
            # Cleanup
            self._run_command(
                "docker compose down -v --remove-orphans",
                cwd=str(compose_dir),
                timeout=30
            )

    @pytest.mark.integration
    @pytest.mark.skipif(shutil.which("docker") is None, reason="Docker not available")
    def test_docker_labels_filtering(self, template_dir, temp_output_dir):
        """Test that Docker labels allow proper filtering for cleanup."""
        project_slug = "docker-labels-test"

        # Generate project
        result_dir = cookiecutter(
            template_dir,
            no_input=True,
            output_dir=temp_output_dir,
            extra_context={
                'deployment_mode': 'testing',
                'customer_slug': project_slug.replace('-etl', '')
            }
        )

        # Start postgres service
        compose_dir = Path(result_dir) / '.devcontainer'
        result = self._run_command(
            "docker compose up -d --no-deps postgres",
            cwd=str(compose_dir),
            timeout=30
        )

        assert result.returncode == 0, f"Docker compose failed: {result.stderr}"

        try:
            # Test various label filters
            all_de_template = self._get_docker_containers("de-template.project")
            testing_only = self._get_docker_containers("de-template.deployment=testing")
            this_project = self._get_docker_containers(f"de-template.project={project_slug}")
            postgres_only = self._get_docker_containers("de-template.service=postgres")

            # Should find containers with each filter
            assert len(all_de_template) >= 1, "Should find containers with de-template.project label"
            assert len(testing_only) >= 1, "Should find containers with testing deployment"
            assert len(this_project) >= 1, f"Should find containers for project {project_slug}"
            assert len(postgres_only) >= 1, "Should find postgres service containers"

            # The specific container should appear in all relevant filters
            expected_container = f"{project_slug}-postgres-test"
            assert expected_container in all_de_template
            assert expected_container in testing_only
            assert expected_container in this_project
            assert expected_container in postgres_only

        finally:
            # Cleanup
            self._run_command(
                "docker compose down -v --remove-orphans",
                cwd=str(compose_dir),
                timeout=30
            )

    @pytest.mark.integration
    @pytest.mark.skipif(shutil.which("docker") is None, reason="Docker not available")
    def test_multiple_projects_isolation(self, template_dir, temp_output_dir):
        """Test that multiple projects with different modes are properly isolated."""
        # Generate two projects with different modes
        projects = [
            {'slug': 'multi-test-1', 'mode': 'testing'},
            {'slug': 'multi-test-2', 'mode': 'production'}
        ]

        project_dirs = []

        for project in projects:
            result_dir = cookiecutter(
                template_dir,
                no_input=True,
                output_dir=temp_output_dir,
                extra_context={
                    'deployment_mode': project['mode'],
                    'customer_slug': project['slug']
                }
            )
            project_dirs.append(result_dir)

        try:
            # Start both projects' postgres services
            for i, result_dir in enumerate(project_dirs):
                compose_dir = Path(result_dir) / '.devcontainer'
                result = self._run_command(
                    "docker compose up -d --no-deps postgres",
                    cwd=str(compose_dir),
                    timeout=30
                )
                assert result.returncode == 0, f"Project {i} failed to start: {result.stderr}"

            # Check isolation - should have distinct containers
            testing_containers = self._get_docker_containers("de-template.deployment=testing")
            production_containers = self._get_docker_containers("de-template.deployment=production")

            # Should have one container in each category
            assert len(testing_containers) >= 1, "Should have testing containers"
            assert len(production_containers) >= 1, "Should have production containers"

            # Container names should be distinct
            testing_names = {c for c in testing_containers if 'multi-test-1-etl' in c}
            production_names = {c for c in production_containers if 'multi-test-2-etl' in c}

            assert len(testing_names) >= 1, "Should have multi-test-1 testing containers"
            assert len(production_names) >= 1, "Should have multi-test-2 production containers"

            # Names should not overlap
            assert testing_names.isdisjoint(production_names), "Container names should not overlap"

        finally:
            # Cleanup both projects
            for result_dir in project_dirs:
                compose_dir = Path(result_dir) / '.devcontainer'
                self._run_command(
                    "docker compose down -v --remove-orphans",
                    cwd=str(compose_dir),
                    timeout=30
                )

    @pytest.mark.integration
    def test_cleanup_script_syntax(self, cleanup_scripts):
        """Test that cleanup scripts have valid syntax."""
        for script_type, script_path in cleanup_scripts.items():
            assert script_path.exists(), f"{script_type} cleanup script not found: {script_path}"

            # Test bash syntax
            result = self._run_command(f"bash -n {script_path}")
            assert result.returncode == 0, f"{script_type} script has syntax errors: {result.stderr}"

    @pytest.mark.integration
    def test_cleanup_script_help_mode(self, cleanup_scripts):
        """Test that cleanup scripts can run in dry-run/help mode."""
        # Test shallow cleanup script
        shallow_script = cleanup_scripts['shallow']

        # The script should handle empty directories gracefully
        result = self._run_command(f"bash {shallow_script}", timeout=30)
        # Should not fail even if no containers to clean
        assert result.returncode == 0, f"Shallow cleanup failed: {result.stderr}"
        assert "Shallow cleanup complete" in result.stdout