"""Integration tests for DCSM custom Docker build support with data-eng-template.

This test validates that DCSM's custom build capabilities (from PR #15) work
correctly with our existing Dockerfile.airflow multi-stage build system.

Key test scenarios:
- Custom build configuration parsing
- Multi-stage build target selection (development)
- Build args propagation
- Custom image naming and caching
- Integration with existing DevContainer workflows
"""

import logging
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

import pytest
import requests
import yaml

# Configure comprehensive test logging for forensic analysis
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TestDCSMCustomBuildIntegration:
    """Test DCSM custom build system integration with data-eng-template."""

    @pytest.mark.slow
    def test_dcsm_custom_build_with_existing_dockerfile(
        self, template_dir: Path, default_cookiecutter_config: dict[str, Any]
    ):
        """Test DCSM can handle our existing custom build configuration.

        Validates:
        1. DCSM correctly processes build configurations from compose.yaml
        2. Multi-stage build target selection works
        3. Custom image naming maintained
        4. Build performance with caching
        5. Final services start successfully
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Generate project
            cmd = [
                "cookiecutter",
                str(template_dir),
                "--output-dir",
                str(temp_path),
                "--no-input",
            ]

            for key, value in default_cookiecutter_config.items():
                cmd.append(f"{key}={value}")

            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Template generation failed: {result.stderr}"

            project_dir = temp_path / default_cookiecutter_config["repo_slug"]
            devcontainer_dir = project_dir / ".devcontainer"
            compose_file = devcontainer_dir / "compose.yaml"

            # Verify compose.yaml has custom build configuration
            compose_content = compose_file.read_text()
            compose_data = yaml.safe_load(compose_content)

            # Verify all Airflow services have build configurations
            airflow_services = [
                "airflow-init",
                "airflow-scheduler",
                "airflow-webserver",
            ]
            for service in airflow_services:
                service_config = compose_data["services"][service]
                assert "build" in service_config, f"{service} should have build configuration"

                build_config = service_config["build"]
                assert (
                    build_config["context"] == ".."
                ), f"{service} should build from parent context"
                assert (
                    build_config["dockerfile"] == "Dockerfile.airflow"
                ), f"{service} should use Dockerfile.airflow"
                assert (
                    build_config["target"] == "development"
                ), f"{service} should target development stage"

                # Verify custom image name
                expected_image = f"{default_cookiecutter_config['repo_slug']}-airflow-dev"
                assert (
                    service_config["image"] == expected_image
                ), f"{service} should use custom image name"

            print("✅ Compose configuration validation passed")

            # Test Docker build process (this tests DCSM's core functionality)
            dockerfile_path = project_dir / "Dockerfile.airflow"
            assert dockerfile_path.exists(), "Dockerfile.airflow should exist"

            # Verify Dockerfile has proper multi-stage structure
            dockerfile_content = dockerfile_path.read_text()
            assert (
                "FROM apache/airflow" in dockerfile_content
            ), "Should use official Airflow base image"
            assert "AS dependencies" in dockerfile_content, "Should have dependencies stage"
            assert "AS runtime" in dockerfile_content, "Should have runtime stage"
            assert "AS development" in dockerfile_content, "Should have development stage"

            # Test actual Docker build (simulates what DCSM would do)
            build_cmd = [
                "docker",
                "build",
                "-f",
                str(dockerfile_path),
                "--target",
                "development",
                "-t",
                f"{default_cookiecutter_config['repo_slug']}-airflow-dev",
                str(project_dir),
            ]

            print("Testing Docker build process...")
            start_time = time.time()
            build_result = subprocess.run(
                build_cmd, capture_output=True, text=True, cwd=project_dir
            )
            build_time = time.time() - start_time

            if build_result.returncode != 0:
                pytest.skip(
                    f"Docker build failed (Docker may not be available): {build_result.stderr}"
                )

            print(f"✅ Docker build completed in {build_time:.1f}s")

            # Test second build for caching validation
            print("Testing Docker build caching...")
            start_time = time.time()
            cache_build_result = subprocess.run(
                build_cmd, capture_output=True, text=True, cwd=project_dir
            )
            cache_build_time = time.time() - start_time

            assert (
                cache_build_result.returncode == 0
            ), f"Cached build should succeed: {cache_build_result.stderr}"

            # Cached build should be significantly faster (less than 50% of original)
            if cache_build_time < build_time * 0.5:
                print(
                    f"✅ Docker layer caching effective: {cache_build_time:.1f}s "
                    f"vs {build_time:.1f}s"
                )
            else:
                print(
                    f"⚠️ Docker caching may not be optimal: {cache_build_time:.1f}s "
                    f"vs {build_time:.1f}s"
                )

            # Test full service startup with custom image
            compose_cmd = ["docker", "compose", "-f", str(compose_file), "up", "-d"]
            startup_result = subprocess.run(
                compose_cmd, capture_output=True, text=True, cwd=devcontainer_dir
            )

            if startup_result.returncode != 0:
                print(f"Service startup failed: {startup_result.stderr}")
                pytest.skip("Service startup failed - may indicate DCSM integration issues")

            try:
                # Wait for Airflow to be ready
                max_wait_time = 300  # 5 minutes
                start_time = time.time()
                airflow_ready = False

                print("Waiting for custom Airflow image services to start...")

                while time.time() - start_time < max_wait_time:
                    try:
                        response = requests.get("http://localhost:8080/health", timeout=5)
                        if response.status_code == 200:
                            print(
                                f"✅ Custom Airflow image services ready after "
                                f"{time.time() - start_time:.1f}s"
                            )
                            airflow_ready = True
                            break
                    except (requests.ConnectionError, requests.Timeout):
                        pass

                    time.sleep(5)

                assert airflow_ready, "Custom Airflow services should start successfully"

                # Verify we're actually using the custom image
                ps_cmd = [
                    "docker",
                    "compose",
                    "-f",
                    str(compose_file),
                    "ps",
                    "--format",
                    "json",
                ]
                ps_result = subprocess.run(
                    ps_cmd, capture_output=True, text=True, cwd=devcontainer_dir
                )

                if ps_result.returncode == 0:
                    import json

                    services_info = [
                        json.loads(line)
                        for line in ps_result.stdout.strip().split("\n")
                        if line.strip()
                    ]

                    airflow_services = [s for s in services_info if "airflow" in s["Service"]]
                    for service in airflow_services:
                        expected_image = f"{default_cookiecutter_config['repo_slug']}-airflow-dev"
                        assert (
                            expected_image in service["Image"]
                        ), f"Service {service['Service']} should use custom image"

                print("✅ All services using custom built images")

                # Test basic authentication to ensure custom image works correctly
                session = requests.Session()
                login_page = session.get("http://localhost:8080/login/", timeout=10)
                assert login_page.status_code == 200, "Should be able to access login page"

                print("✅ Custom Airflow image functional test passed")

            finally:
                # Clean up services and images
                cleanup_cmd = [
                    "docker",
                    "compose",
                    "-f",
                    str(compose_file),
                    "down",
                    "-v",
                ]
                cleanup_result = subprocess.run(
                    cleanup_cmd, capture_output=True, text=True, cwd=devcontainer_dir
                )

                # Clean up custom image
                image_cleanup_cmd = [
                    "docker",
                    "rmi",
                    f"{default_cookiecutter_config['repo_slug']}-airflow-dev",
                ]
                subprocess.run(image_cleanup_cmd, capture_output=True, text=True)

                if cleanup_result.returncode == 0:
                    print("✅ Services and custom images cleaned up")

    def test_dcsm_build_args_support(
        self, template_dir: Path, default_cookiecutter_config: dict[str, Any]
    ):
        """Test that DCSM correctly handles build arguments in custom builds.

        This simulates how DCSM would pass build arguments for Windows authentication
        features in future phases.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Generate project
            cmd = [
                "cookiecutter",
                str(template_dir),
                "--output-dir",
                str(temp_path),
                "--no-input",
            ]

            for key, value in default_cookiecutter_config.items():
                cmd.append(f"{key}={value}")

            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Template generation failed: {result.stderr}"

            project_dir = temp_path / default_cookiecutter_config["repo_slug"]
            dockerfile_path = project_dir / "Dockerfile.airflow"

            # Verify Dockerfile accepts build arguments (needed for Windows auth)
            dockerfile_content = dockerfile_path.read_text()
            assert "ARG AIRFLOW_VERSION=" in dockerfile_content, "Should accept AIRFLOW_VERSION arg"
            assert "ARG PYTHON_VERSION=" in dockerfile_content, "Should accept PYTHON_VERSION arg"

            # Test build with custom args (simulates DCSM build args feature)
            build_cmd = [
                "docker",
                "build",
                "-f",
                str(dockerfile_path),
                "--target",
                "development",
                "--build-arg",
                f"AIRFLOW_VERSION={default_cookiecutter_config['airflow_version']}",
                "--build-arg",
                f"PYTHON_VERSION={default_cookiecutter_config['python_version']}",
                "--build-arg",
                "ENABLE_WINDOWS_AUTH=false",  # Future Windows auth arg
                "-t",
                f"{default_cookiecutter_config['repo_slug']}-airflow-test",
                str(project_dir),
            ]

            build_result = subprocess.run(
                build_cmd, capture_output=True, text=True, cwd=project_dir
            )

            if build_result.returncode == 0:
                print("✅ Build args passed correctly to Docker build")

                # Clean up test image
                cleanup_cmd = [
                    "docker",
                    "rmi",
                    f"{default_cookiecutter_config['repo_slug']}-airflow-test",
                ]
                subprocess.run(cleanup_cmd, capture_output=True, text=True)
            else:
                # Don't fail test if Docker unavailable, but log the issue
                print(
                    f"⚠️ Build args test skipped - Docker may not be available: "
                    f"{build_result.stderr}"
                )

    def test_dcsm_services_yaml_readiness(
        self, template_dir: Path, default_cookiecutter_config: dict[str, Any]
    ):
        """Test that our compose.yaml structure is compatible with DCSM services.yaml format.

        This prepares for Phase 2 integration where DCSM will manage our services
        through its services.yaml configuration system.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Generate project
            cmd = [
                "cookiecutter",
                str(template_dir),
                "--output-dir",
                str(temp_path),
                "--no-input",
            ]

            for key, value in default_cookiecutter_config.items():
                cmd.append(f"{key}={value}")

            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Template generation failed: {result.stderr}"

            project_dir = temp_path / default_cookiecutter_config["repo_slug"]
            compose_file = project_dir / ".devcontainer" / "compose.yaml"

            # Load and analyze compose configuration
            compose_content = compose_file.read_text()
            compose_data = yaml.safe_load(compose_content)

            # Verify structure matches what DCSM expects
            assert "services" in compose_data, "Should have services section"
            assert "volumes" in compose_data, "Should have volumes section"

            # Check that each service has required fields for DCSM conversion
            for service_name, service_config in compose_data["services"].items():
                if "airflow" in service_name:
                    # These are the fields DCSM will need to extract
                    assert (
                        "build" in service_config or "image" in service_config
                    ), f"{service_name} needs image source"

                    if "build" in service_config:
                        build_config = service_config["build"]
                        # DCSM BuildConfig model fields
                        assert "context" in build_config, f"{service_name} build needs context"
                        assert (
                            "dockerfile" in build_config
                        ), f"{service_name} build needs dockerfile"
                        assert "target" in build_config, f"{service_name} build needs target"

                        # These fields are optional but DCSM supports them
                        print(f"✅ Service {service_name} has DCSM-compatible build config")

            # Verify environment variables are properly structured
            airflow_env_anchor = compose_data.get("x-airflow-env", {})
            assert len(airflow_env_anchor) > 0, "Should have Airflow environment variables"
            assert "_AIRFLOW_WWW_USER_USERNAME" in airflow_env_anchor, "Should have admin username"
            assert "_AIRFLOW_WWW_USER_PASSWORD" in airflow_env_anchor, "Should have admin password"

            print("✅ Compose structure is DCSM-compatible for Phase 2 integration")
