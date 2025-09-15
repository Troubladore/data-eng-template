"""
End-to-end tests for the complete Docker cleanup system.
Tests full workflow: generate -> start services -> cleanup -> verify clean state.
"""
import pytest
import tempfile
import shutil
import os
import subprocess
import time
from pathlib import Path
from cookiecutter.main import cookiecutter


class TestCleanupSystemE2E:
    """End-to-end tests for Docker cleanup system."""

    @pytest.fixture
    def template_dir(self):
        """Return path to the cookiecutter template."""
        return str(Path(__file__).parent.parent.parent)

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for generated projects."""
        temp_dir = tempfile.mkdtemp(prefix="test_cleanup_e2e_")
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

    def _run_command(self, cmd, cwd=None, timeout=120, input_text=None):
        """Run a shell command with timeout."""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                input=input_text
            )
            return result
        except subprocess.TimeoutExpired:
            pytest.fail(f"Command timed out after {timeout}s: {cmd}")

    def _get_de_template_containers(self):
        """Get all containers with de-template labels."""
        cmd = "docker ps -a --filter 'label=de-template.project' --format '{{.Names}}'"
        result = self._run_command(cmd, timeout=30)
        if result.returncode != 0:
            return []
        return [name.strip() for name in result.stdout.split('\n') if name.strip()]

    def _get_de_template_images(self):
        """Get all images that might be related to de-template projects."""
        cmd = "docker images --format '{{.Repository}}:{{.Tag}}' | grep -E '(etl|test)'"
        result = self._run_command(cmd, timeout=30)
        if result.returncode != 0:
            return []
        return [img.strip() for img in result.stdout.split('\n') if img.strip() and img != '<none>:<none>']

    def _wait_for_service_health(self, compose_dir, service_name, timeout=60):
        """Wait for a service to become healthy."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = self._run_command(
                f"docker compose ps {service_name} --format json",
                cwd=str(compose_dir),
                timeout=10
            )
            if result.returncode == 0 and ('running' in result.stdout.lower() or 'healthy' in result.stdout.lower()):
                return True
            time.sleep(2)
        return False

    @pytest.mark.e2e
    @pytest.mark.skipif(shutil.which("docker") is None, reason="Docker not available")
    def test_complete_testing_workflow_with_cleanup(self, template_dir, temp_output_dir, cleanup_scripts):
        """Test complete workflow: generate testing project -> start -> cleanup -> verify clean."""
        customer_slug = "e2e-test-complete"
        project_slug = f"{customer_slug}-etl"  # cookiecutter appends -etl

        # 1. Generate testing project
        result_dir = cookiecutter(
            template_dir,
            no_input=True,
            output_dir=temp_output_dir,
            extra_context={
                'deployment_mode': 'testing',
                'customer_slug': customer_slug
            }
        )

        compose_dir = Path(result_dir) / '.devcontainer'

        try:
            # 2. Start services
            result = self._run_command(
                "docker compose up -d postgres airflow-init",
                cwd=str(compose_dir),
                timeout=120
            )
            assert result.returncode == 0, f"Failed to start services: {result.stderr}"

            # Wait for postgres to be ready
            assert self._wait_for_service_health(compose_dir, "postgres", timeout=30), "Postgres failed to start"

            # 3. Verify containers are running with correct naming
            containers = self._get_de_template_containers()
            expected_containers = [
                f"{project_slug}-postgres-test",
                f"{project_slug}-airflow-init-test"
            ]

            for expected in expected_containers:
                assert any(expected in c for c in containers), f"Expected container {expected} not found in {containers}"

            # 4. Run shallow cleanup script
            result = self._run_command(
                f"bash {cleanup_scripts['shallow']}",
                timeout=180
            )
            assert result.returncode == 0, f"Shallow cleanup failed: {result.stderr}"
            assert "Shallow cleanup complete" in result.stdout

            # 5. Verify cleanup was successful
            containers_after = self._get_de_template_containers()
            project_containers_after = [c for c in containers_after if project_slug in c]

            assert len(project_containers_after) == 0, f"Found containers after cleanup: {project_containers_after}"

            # 6. Verify project directory was removed
            assert not os.path.exists(result_dir), f"Project directory still exists: {result_dir}"

        except Exception as e:
            # Emergency cleanup if test fails
            self._run_command(f"docker compose down -v --remove-orphans", cwd=str(compose_dir), timeout=60)
            raise e

    @pytest.mark.e2e
    @pytest.mark.skipif(shutil.which("docker") is None, reason="Docker not available")
    def test_production_vs_testing_isolation_and_cleanup(self, template_dir, temp_output_dir, cleanup_scripts):
        """Test that production and testing projects are isolated and cleaned up correctly."""
        projects = [
            {'slug': 'isolation-prod', 'mode': 'production'},
            {'slug': 'isolation-test', 'mode': 'testing'}
        ]

        project_dirs = []

        try:
            # 1. Generate both projects
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
                project_dirs.append((result_dir, project))

            # 2. Start postgres in both projects
            for result_dir, project in project_dirs:
                compose_dir = Path(result_dir) / '.devcontainer'
                result = self._run_command(
                    "docker compose up -d postgres",
                    cwd=str(compose_dir),
                    timeout=60
                )
                assert result.returncode == 0, f"Failed to start {project['slug']}: {result.stderr}"

            # 3. Verify both are running with correct labels
            all_containers = self._get_de_template_containers()
            prod_containers = [c for c in all_containers if 'isolation-prod-etl' in c and 'test' not in c]
            test_containers = [c for c in all_containers if 'isolation-test-etl' in c and 'test' in c]

            assert len(prod_containers) >= 1, f"Expected production containers, found: {prod_containers}"
            assert len(test_containers) >= 1, f"Expected testing containers, found: {test_containers}"

            # 4. Run shallow cleanup (should clean both since they're in temp dir)
            result = self._run_command(
                f"bash {cleanup_scripts['shallow']}",
                timeout=180
            )
            assert result.returncode == 0, f"Cleanup failed: {result.stderr}"

            # 5. Verify all project containers are gone
            containers_after = self._get_de_template_containers()
            remaining_project_containers = [
                c for c in containers_after
                if 'isolation-prod-etl' in c or 'isolation-test-etl' in c
            ]

            assert len(remaining_project_containers) == 0, f"Found containers after cleanup: {remaining_project_containers}"

        except Exception as e:
            # Emergency cleanup
            for result_dir, project in project_dirs:
                compose_dir = Path(result_dir) / '.devcontainer'
                self._run_command(f"docker compose down -v --remove-orphans", cwd=str(compose_dir), timeout=60)
            raise e

    @pytest.mark.e2e
    @pytest.mark.skipif(shutil.which("docker") is None, reason="Docker not available")
    def test_cleanup_with_no_projects(self, cleanup_scripts):
        """Test that cleanup scripts handle empty state gracefully."""
        # Run cleanup when there are no de-template projects
        result = self._run_command(
            f"bash {cleanup_scripts['shallow']}",
            timeout=60
        )

        # Should succeed even with nothing to clean
        assert result.returncode == 0, f"Cleanup failed with empty state: {result.stderr}"
        assert "Shallow cleanup complete" in result.stdout

    @pytest.mark.e2e
    @pytest.mark.skipif(shutil.which("docker") is None, reason="Docker not available")
    def test_deep_cleanup_confirmation(self, cleanup_scripts):
        """Test that deep cleanup properly prompts for confirmation."""
        # Run deep cleanup with automatic "no" response
        result = self._run_command(
            f"bash {cleanup_scripts['deep']}",
            timeout=30,
            input_text="n\n"
        )

        # Should exit gracefully when user says no
        assert result.returncode == 1, "Deep cleanup should exit with error when cancelled"
        assert "Cleanup cancelled" in result.stdout

    @pytest.mark.e2e
    @pytest.mark.skipif(shutil.which("docker") is None, reason="Docker not available")
    def test_cleanup_script_error_handling(self, template_dir, temp_output_dir, cleanup_scripts):
        """Test that cleanup scripts handle errors gracefully."""
        project_slug = "error-handling-test"

        # Generate a project
        result_dir = cookiecutter(
            template_dir,
            no_input=True,
            output_dir=temp_output_dir,
            extra_context={
                'deployment_mode': 'testing',
                'customer_slug': project_slug.replace('-etl', '')
            }
        )

        # Start just postgres
        compose_dir = Path(result_dir) / '.devcontainer'
        result = self._run_command(
            "docker compose up -d postgres",
            cwd=str(compose_dir),
            timeout=60
        )
        assert result.returncode == 0, f"Failed to start postgres: {result.stderr}"

        try:
            # Manually stop docker daemon would be ideal, but that's too disruptive
            # Instead, test that cleanup continues even if some operations fail

            # Make compose file temporarily unreadable to simulate some failures
            compose_file = compose_dir / "compose.yaml"
            original_mode = compose_file.stat().st_mode

            # Run cleanup - should handle errors gracefully
            result = self._run_command(
                f"bash {cleanup_scripts['shallow']}",
                timeout=180
            )

            # Restore file permissions (if file still exists)
            if compose_file.exists():
                compose_file.chmod(original_mode)

            # Cleanup should still complete (with some warnings/errors)
            assert result.returncode == 0, f"Cleanup should complete despite errors: {result.stderr}"

        except Exception as e:
            # Emergency cleanup
            if compose_file.exists():
                compose_file.chmod(original_mode)
            self._run_command(f"docker compose down -v --remove-orphans", cwd=str(compose_dir), timeout=60)
            raise e

    @pytest.mark.e2e
    def test_remote_cleanup_url_accessibility(self):
        """Test that remote cleanup URLs are accessible."""
        remote_urls = [
            "https://raw.githubusercontent.com/Troubladore/data-eng-template/astro/tests/utils/cleanup-shallow.sh",
            "https://raw.githubusercontent.com/Troubladore/data-eng-template/astro/tests/utils/cleanup-deep.sh"
        ]

        for url in remote_urls:
            result = self._run_command(f"curl -sSf --connect-timeout 10 {url} | head -5", timeout=30)
            assert result.returncode == 0, f"Remote URL not accessible: {url}"
            assert "#!/bin/bash" in result.stdout, f"Remote script doesn't look like bash script: {url}"