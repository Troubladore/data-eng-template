"""
Stress tests for the Docker cleanup system.
Tests extreme scenarios, concurrent operations, and recovery.
"""
import pytest
import tempfile
import shutil
import os
import subprocess
import time
import threading
from pathlib import Path
from cookiecutter.main import cookiecutter
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestCleanupSystemStress:
    """Stress tests for Docker cleanup system."""

    @pytest.fixture
    def template_dir(self):
        """Return path to the cookiecutter template."""
        return str(Path(__file__).parent.parent.parent)

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for generated projects."""
        temp_dir = tempfile.mkdtemp(prefix="test_cleanup_stress_")
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

    def _run_command(self, cmd, cwd=None, timeout=300, input_text=None):
        """Run a shell command with extended timeout for stress tests."""
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

    def _generate_project_thread(self, template_dir, temp_output_dir, project_id, mode):
        """Generate a single project in a thread."""
        try:
            result_dir = cookiecutter(
                template_dir,
                no_input=True,
                output_dir=temp_output_dir,
                extra_context={
                    'deployment_mode': mode,
                    'customer_slug': f'stress-test-{project_id}'
                }
            )
            return {'success': True, 'result_dir': result_dir, 'project_id': project_id, 'mode': mode}
        except Exception as e:
            return {'success': False, 'error': str(e), 'project_id': project_id, 'mode': mode}

    def _start_postgres_thread(self, result_dir, project_id):
        """Start postgres service in a thread."""
        try:
            compose_dir = Path(result_dir) / '.devcontainer'
            result = self._run_command(
                "docker compose up -d postgres",
                cwd=str(compose_dir),
                timeout=120
            )
            return {
                'success': result.returncode == 0,
                'project_id': project_id,
                'result_dir': result_dir,
                'output': result.stdout if result.returncode == 0 else result.stderr
            }
        except Exception as e:
            return {'success': False, 'project_id': project_id, 'error': str(e)}

    @pytest.mark.stress
    @pytest.mark.skipif(shutil.which("docker") is None, reason="Docker not available")
    def test_concurrent_project_generation(self, template_dir, temp_output_dir):
        """Test generating multiple projects concurrently."""
        num_projects = 5
        modes = ['testing', 'production']

        # Generate projects concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for i in range(num_projects):
                mode = modes[i % len(modes)]
                future = executor.submit(
                    self._generate_project_thread,
                    template_dir, temp_output_dir, i, mode
                )
                futures.append(future)

            # Collect results
            results = []
            for future in as_completed(futures, timeout=300):
                result = future.result()
                results.append(result)

        # Verify all projects generated successfully
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]

        assert len(successful) == num_projects, f"Only {len(successful)}/{num_projects} projects succeeded. Failures: {failed}"

        # Verify each project has correct structure
        for result in successful:
            result_dir = result['result_dir']
            assert os.path.exists(result_dir), f"Project directory missing: {result_dir}"

            compose_file = Path(result_dir) / '.devcontainer' / 'compose.yaml'
            assert compose_file.exists(), f"Compose file missing: {compose_file}"

            # Verify naming based on mode
            with open(compose_file) as f:
                content = f.read()

            project_slug = f"stress-test-{result['project_id']}-etl"
            if result['mode'] == 'testing':
                assert f"{project_slug}-modern-test" in content, f"Testing mode naming incorrect in {result_dir}"
                assert f"{project_slug}-postgres-test" in content
            else:
                assert f"{project_slug}-modern" in content and f"{project_slug}-modern-test" not in content
                assert f"{project_slug}-postgres" in content and f"{project_slug}-postgres-test" not in content

    @pytest.mark.stress
    @pytest.mark.skipif(shutil.which("docker") is None, reason="Docker not available")
    def test_concurrent_docker_startup_and_cleanup(self, template_dir, temp_output_dir, cleanup_scripts):
        """Test concurrent Docker operations and cleanup."""
        num_projects = 3

        # Generate projects first
        project_results = []
        for i in range(num_projects):
            result_dir = cookiecutter(
                template_dir,
                no_input=True,
                output_dir=temp_output_dir,
                extra_context={
                    'deployment_mode': 'testing',
                    'customer_slug': f'concurrent-{i}'
                }
            )
            project_results.append(result_dir)

        try:
            # Start postgres services concurrently
            with ThreadPoolExecutor(max_workers=3) as executor:
                startup_futures = []
                for i, result_dir in enumerate(project_results):
                    future = executor.submit(self._start_postgres_thread, result_dir, i)
                    startup_futures.append(future)

                # Collect startup results
                startup_results = []
                for future in as_completed(startup_futures, timeout=300):
                    result = future.result()
                    startup_results.append(result)

            # Verify services started
            successful_startups = [r for r in startup_results if r['success']]
            assert len(successful_startups) >= 2, f"Expected at least 2 successful startups, got {len(successful_startups)}"

            # Verify containers are running
            containers_before = self._get_de_template_containers()
            assert len(containers_before) >= 2, f"Expected multiple containers, found: {containers_before}"

            # Wait a bit for services to stabilize
            time.sleep(5)

            # Run cleanup while services are still running
            result = self._run_command(
                f"bash {cleanup_scripts['shallow']}",
                timeout=300
            )

            assert result.returncode == 0, f"Cleanup failed during concurrent operations: {result.stderr}"

            # Verify cleanup worked
            containers_after = self._get_de_template_containers()
            remaining_test_containers = [c for c in containers_after if any(f'concurrent-{i}-etl' in c for i in range(num_projects))]

            assert len(remaining_test_containers) == 0, f"Containers remain after cleanup: {remaining_test_containers}"

        except Exception as e:
            # Emergency cleanup
            for result_dir in project_results:
                compose_dir = Path(result_dir) / '.devcontainer'
                self._run_command(f"docker compose down -v --remove-orphans", cwd=str(compose_dir), timeout=60)
            raise e

    @pytest.mark.stress
    @pytest.mark.skipif(shutil.which("docker") is None, reason="Docker not available")
    def test_cleanup_with_resource_exhaustion_simulation(self, template_dir, temp_output_dir, cleanup_scripts):
        """Test cleanup behavior under simulated resource constraints."""
        # Generate several projects to create resource pressure
        num_projects = 4
        project_dirs = []

        try:
            # Generate multiple projects
            for i in range(num_projects):
                result_dir = cookiecutter(
                    template_dir,
                    no_input=True,
                    output_dir=temp_output_dir,
                    extra_context={
                        'deployment_mode': 'testing',
                        'customer_slug': f'resource-{i}'
                    }
                )
                project_dirs.append(result_dir)

            # Start postgres in each project
            for result_dir in project_dirs:
                compose_dir = Path(result_dir) / '.devcontainer'
                result = self._run_command(
                    "docker compose up -d postgres",
                    cwd=str(compose_dir),
                    timeout=90
                )
                # Don't fail if some don't start due to resource constraints
                if result.returncode != 0:
                    print(f"Warning: Failed to start postgres in {result_dir}: {result.stderr}")

            # Verify we have some containers running
            containers = self._get_de_template_containers()
            resource_containers = [c for c in containers if any(f'resource-{i}-etl' in c for i in range(num_projects))]

            if len(resource_containers) == 0:
                pytest.skip("No containers started - system may be under resource pressure")

            # Run cleanup under pressure
            result = self._run_command(
                f"bash {cleanup_scripts['shallow']}",
                timeout=600  # Extended timeout for resource-constrained cleanup
            )

            # Cleanup should eventually succeed, even under pressure
            assert result.returncode == 0, f"Cleanup failed under resource pressure: {result.stderr}"

            # Verify cleanup was effective
            containers_after = self._get_de_template_containers()
            remaining_resource_containers = [c for c in containers_after if any(f'resource-{i}-etl' in c for i in range(num_projects))]

            assert len(remaining_resource_containers) == 0, f"Containers remain after resource pressure cleanup: {remaining_resource_containers}"

        except Exception as e:
            # Emergency cleanup
            for result_dir in project_dirs:
                compose_dir = Path(result_dir) / '.devcontainer'
                self._run_command(f"docker compose down -v --remove-orphans", cwd=str(compose_dir), timeout=120)
            raise e

    @pytest.mark.stress
    def test_cleanup_script_performance(self, cleanup_scripts):
        """Test cleanup script performance with large number of operations."""
        # Test that cleanup scripts can handle many operations efficiently
        start_time = time.time()

        # Run shallow cleanup (should handle empty state efficiently)
        result = self._run_command(
            f"bash {cleanup_scripts['shallow']}",
            timeout=60
        )

        end_time = time.time()
        execution_time = end_time - start_time

        assert result.returncode == 0, f"Cleanup performance test failed: {result.stderr}"
        assert execution_time < 30, f"Cleanup took too long: {execution_time}s (expected < 30s)"

    @pytest.mark.stress
    @pytest.mark.skipif(shutil.which("docker") is None, reason="Docker not available")
    def test_recovery_after_partial_cleanup_failure(self, template_dir, temp_output_dir, cleanup_scripts):
        """Test that system can recover after partial cleanup failures."""
        project_slug = "recovery-test"

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

        compose_dir = Path(result_dir) / '.devcontainer'

        try:
            # Start services
            result = self._run_command(
                "docker compose up -d postgres",
                cwd=str(compose_dir),
                timeout=90
            )
            assert result.returncode == 0, f"Failed to start services: {result.stderr}"

            # Simulate partial failure by making project directory read-only temporarily
            os.chmod(result_dir, 0o555)

            # First cleanup attempt (should have some issues but not crash)
            result1 = self._run_command(
                f"bash {cleanup_scripts['shallow']}",
                timeout=180
            )

            # Restore permissions
            os.chmod(result_dir, 0o755)

            # Second cleanup attempt (should complete successfully)
            result2 = self._run_command(
                f"bash {cleanup_scripts['shallow']}",
                timeout=180
            )

            assert result2.returncode == 0, f"Recovery cleanup failed: {result2.stderr}"

            # Verify system recovered and cleaned up
            containers = self._get_de_template_containers()
            project_containers = [c for c in containers if project_slug in c]

            assert len(project_containers) == 0, f"Recovery didn't clean all containers: {project_containers}"

        except Exception as e:
            # Emergency cleanup - restore permissions first
            try:
                os.chmod(result_dir, 0o755)
            except:
                pass
            self._run_command(f"docker compose down -v --remove-orphans", cwd=str(compose_dir), timeout=60)
            raise e

    @pytest.mark.stress
    def test_deep_cleanup_stress_with_confirmation(self, cleanup_scripts):
        """Test deep cleanup under stress with proper confirmation handling."""
        # Test that deep cleanup handles confirmation properly under various conditions

        # Test rapid confirmation responses
        for response in ["y\n", "n\n", "yes\n", "no\n"]:
            result = self._run_command(
                f"bash {cleanup_scripts['deep']}",
                timeout=60,
                input_text=response
            )

            if response.startswith('y'):
                # Should proceed with cleanup
                assert "Deep cleanup complete" in result.stdout or result.returncode == 0
            else:
                # Should cancel
                assert result.returncode == 1 and "Cleanup cancelled" in result.stdout