#!/usr/bin/env python3
"""
DCSM Integration Validation Script

This script validates that the data-eng-template is ready for DCSM integration
and tests the custom build system functionality from DCSM PR #15.

Run this before human testing to ensure all automated checks pass.

Usage:
    python scripts/validate-dcsm-integration.py [--quick] [--no-docker]

    --quick: Skip slow integration tests (Docker builds, service startup)
    --no-docker: Skip all Docker-dependent tests
"""

import argparse
import subprocess
import sys
import tempfile
import time
from pathlib import Path

try:
    import yaml
except ImportError:
    print("❌ PyYAML is required for this validation script.")
    print("📋 Install dependencies with uv: uv sync")
    print("📋 Or install PyYAML directly: uv add PyYAML")
    print("📋 (This template uses uv exclusively for package management)")
    sys.exit(1)


class ValidationError(Exception):
    """Custom exception for validation failures."""

    pass


class DCSMValidator:
    """Validates DCSM integration readiness for data-eng-template."""

    def __init__(self, quick_mode: bool = False, no_docker: bool = False):
        self.quick_mode = quick_mode
        self.no_docker = no_docker
        self.errors: list[str] = []
        self.warnings: list[str] = []

        # Default cookiecutter configuration for testing
        self.test_config = {
            "project_name": "DCSM Test Project",
            "repo_slug": "dcsm-test-project",
            "author_name": "Test Author",
            "db_name": "dcsm_test_db",
            "airflow_version": "3.0.6",
            "python_version": "3.12",
            "postgres_version": "16",
        }

    def log_success(self, message: str) -> None:
        """Log a successful validation step."""
        print(f"✅ {message}")

    def log_warning(self, message: str) -> None:
        """Log a warning."""
        print(f"⚠️  {message}")
        self.warnings.append(message)

    def log_error(self, message: str) -> None:
        """Log an error."""
        print(f"❌ {message}")
        self.errors.append(message)

    def validate_template_structure(self) -> None:
        """Validate basic template structure for DCSM compatibility."""
        print("\\n🔍 Validating template structure...")

        template_root = Path.cwd()

        # Check critical files exist
        critical_files = [
            "cookiecutter.json",
            "hooks/post_gen_project.py",
            "{{cookiecutter.repo_slug}}/Dockerfile.airflow",
            "{{cookiecutter.repo_slug}}/.devcontainer/compose.yaml",
        ]

        for file_path in critical_files:
            full_path = template_root / file_path
            if not full_path.exists():
                self.log_error(f"Missing critical file: {file_path}")
            else:
                self.log_success(f"Found required file: {file_path}")

        # Validate cookiecutter.json
        try:
            cookiecutter_file = template_root / "cookiecutter.json"
            with open(cookiecutter_file) as f:
                config = yaml.safe_load(f)

            required_vars = [
                "project_name",
                "repo_slug",
                "airflow_version",
                "python_version",
            ]
            for var in required_vars:
                if var not in config:
                    self.log_error(f"Missing cookiecutter variable: {var}")
                else:
                    self.log_success(f"Found cookiecutter variable: {var}")
        except Exception as e:
            self.log_error(f"Failed to validate cookiecutter.json: {e}")

    def validate_dockerfile_structure(self) -> None:
        """Validate Dockerfile.airflow structure for DCSM custom builds."""
        print("\\n🐳 Validating Dockerfile.airflow structure...")

        dockerfile_path = Path.cwd() / "{{cookiecutter.repo_slug}}" / "Dockerfile.airflow"

        if not dockerfile_path.exists():
            self.log_error("Dockerfile.airflow not found")
            return

        content = dockerfile_path.read_text()

        # Check for multi-stage build structure
        required_stages = ["dependencies", "runtime", "development"]
        for stage in required_stages:
            if f"AS {stage}" in content:
                self.log_success(f"Found required build stage: {stage}")
            else:
                self.log_error(f"Missing build stage: {stage}")

        # Check for build args (needed for DCSM BuildConfig)
        required_args = ["AIRFLOW_VERSION", "PYTHON_VERSION"]
        for arg in required_args:
            if f"ARG {arg}=" in content:
                self.log_success(f"Found required build arg: {arg}")
            else:
                self.log_warning(f"Missing build arg: {arg} (may affect DCSM integration)")

        # Check for proper base image
        if "FROM apache/airflow:" in content:
            self.log_success("Uses official Airflow base image")
        else:
            self.log_error("Does not use official Airflow base image")

    def validate_compose_configuration(self, project_path: Path = None) -> None:
        """Validate Docker Compose configuration for DCSM compatibility."""
        print("\\n🔧 Validating Docker Compose configuration...")

        if project_path:
            # Validate generated project compose.yaml
            compose_path = project_path / ".devcontainer" / "compose.yaml"
        else:
            # Just check template file exists (don't parse it due to cookiecutter syntax)
            compose_path = (
                Path.cwd() / "{{cookiecutter.repo_slug}}" / ".devcontainer" / "compose.yaml"
            )
            if compose_path.exists():
                self.log_success("Found template compose.yaml file")
                return
            else:
                self.log_error("Template compose.yaml not found")
                return

        if not compose_path.exists():
            self.log_error("compose.yaml not found in generated project")
            return

        try:
            content = compose_path.read_text()
            compose_data = yaml.safe_load(content)
        except Exception as e:
            self.log_error(f"Failed to parse compose.yaml: {e}")
            return

        # Check service structure
        if "services" not in compose_data:
            self.log_error("No services section in compose.yaml")
            return

        services = compose_data["services"]
        airflow_services = ["airflow-init", "airflow-scheduler", "airflow-webserver"]

        for service in airflow_services:
            if service not in services:
                self.log_error(f"Missing required service: {service}")
                continue

            service_config = services[service]

            # Check for build configuration (DCSM requirement)
            if "build" not in service_config:
                self.log_error(f"Service {service} missing build configuration")
                continue

            build_config = service_config["build"]

            # Validate build configuration fields
            required_build_fields = ["context", "dockerfile", "target"]
            for field in required_build_fields:
                if field not in build_config:
                    self.log_error(f"Service {service} missing build.{field}")
                else:
                    self.log_success(f"Service {service} has build.{field}")

            # Check for custom image name
            if "image" not in service_config:
                self.log_warning(f"Service {service} missing custom image name")
            else:
                self.log_success(f"Service {service} has custom image name")

        # Check for environment configuration
        if "x-airflow-env" not in compose_data:
            self.log_error("Missing x-airflow-env anchor for authentication")
        else:
            auth_env = compose_data["x-airflow-env"]
            if (
                "_AIRFLOW_WWW_USER_USERNAME" in auth_env
                and "_AIRFLOW_WWW_USER_PASSWORD" in auth_env
            ):
                self.log_success("Authentication environment properly configured")
            else:
                self.log_error("Missing authentication credentials in environment")

    def test_template_generation(self) -> Path:
        """Test template generation with test configuration."""
        print("\\n🏗️  Testing template generation...")

        # Create a temporary directory that we'll clean up manually
        self.temp_dir = tempfile.mkdtemp()
        temp_path = Path(self.temp_dir)

        # Build cookiecutter command
        cmd = [
            "cookiecutter",
            str(Path.cwd()),
            "--output-dir",
            str(temp_path),
            "--no-input",
        ]

        # Add test configuration
        for key, value in self.test_config.items():
            cmd.append(f"{key}={value}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                self.log_success("Template generation completed successfully")
                project_path = temp_path / self.test_config["repo_slug"]
                return project_path
            else:
                self.log_error(f"Template generation failed: {result.stderr}")
                return None
        except subprocess.TimeoutExpired:
            self.log_error("Template generation timed out")
            return None
        except Exception as e:
            self.log_error(f"Template generation error: {e}")
            return None

    def test_docker_build(self, project_path: Path) -> bool:
        """Test Docker build functionality."""
        if self.no_docker:
            self.log_warning("Skipping Docker build test (--no-docker flag)")
            return True

        print("\\n🐳 Testing Docker build functionality...")

        dockerfile_path = project_path / "Dockerfile.airflow"
        if not dockerfile_path.exists():
            self.log_error("Generated project missing Dockerfile.airflow")
            return False

        # Test Docker build
        build_cmd = [
            "docker",
            "build",
            "-f",
            str(dockerfile_path),
            "--target",
            "development",
            "-t",
            f"{self.test_config['repo_slug']}-airflow-test",
            str(project_path),
        ]

        try:
            start_time = time.time()
            result = subprocess.run(build_cmd, capture_output=True, text=True, timeout=600)
            build_time = time.time() - start_time

            if result.returncode == 0:
                self.log_success(f"Docker build completed successfully in {build_time:.1f}s")

                # Test build caching
                self.log_success("Testing Docker layer caching...")
                start_time = time.time()
                cache_result = subprocess.run(
                    build_cmd, capture_output=True, text=True, timeout=300
                )
                cache_time = time.time() - start_time

                if cache_result.returncode == 0:
                    if cache_time < build_time * 0.5:
                        self.log_success(
                            f"Docker caching effective: {cache_time:.1f}s vs {build_time:.1f}s"
                        )
                    else:
                        self.log_warning(
                            f"Docker caching may be suboptimal: {cache_time:.1f}s "
                            f"vs {build_time:.1f}s"
                        )

                # Clean up test image
                cleanup_cmd = [
                    "docker",
                    "rmi",
                    f"{self.test_config['repo_slug']}-airflow-test",
                ]
                subprocess.run(cleanup_cmd, capture_output=True, text=True)

                return True
            else:
                self.log_error(f"Docker build failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.log_error("Docker build timed out")
            return False
        except FileNotFoundError:
            self.log_warning("Docker not available - skipping build test")
            return True
        except Exception as e:
            self.log_error(f"Docker build test failed: {e}")
            return False

    def test_service_startup(self, project_path: Path) -> bool:
        """Test service startup with generated configuration."""
        if self.no_docker or self.quick_mode:
            self.log_warning("Skipping service startup test (quick mode or no-docker)")
            return True

        print("\\n🚀 Testing service startup...")

        compose_file = project_path / ".devcontainer" / "compose.yaml"
        if not compose_file.exists():
            self.log_error("Generated project missing compose.yaml")
            return False

        # Start services (build images first if they don't exist)
        startup_cmd = [
            "docker",
            "compose",
            "-f",
            str(compose_file),
            "up",
            "-d",
            "--build",
        ]

        try:
            result = subprocess.run(
                startup_cmd,
                capture_output=True,
                text=True,
                cwd=compose_file.parent,
                timeout=300,
            )

            if result.returncode == 0:
                self.log_success("Services started successfully")

                # Wait for services to be ready (short test)
                time.sleep(30)

                # Check service health
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
                    ps_cmd, capture_output=True, text=True, cwd=compose_file.parent
                )

                if ps_result.returncode == 0:
                    import json

                    try:
                        # Parse each line as a separate JSON object
                        services_info = []
                        for line in ps_result.stdout.strip().split("\\n"):
                            if line.strip():
                                try:
                                    services_info.append(json.loads(line.strip()))
                                except json.JSONDecodeError:
                                    # Skip invalid JSON lines
                                    continue

                        running_services = [s for s in services_info if s.get("State") == "running"]
                        if len(running_services) >= 3:  # postgres, scheduler, webserver minimum
                            self.log_success(f"Found {len(running_services)} running services")
                            return True
                        else:
                            self.log_error(
                                f"Only {len(running_services)} services running, expected at least 3"
                            )
                            return False
                    except Exception as json_error:
                        # Fall back to simple container count check
                        self.log_warning(f"JSON parsing failed ({json_error}), using simple container check")
                        # Count running containers with basic docker compose ps
                        simple_ps_cmd = [
                            "docker", "compose", "-f", str(compose_file), "ps", "--services", "--filter", "status=running"
                        ]
                        simple_result = subprocess.run(
                            simple_ps_cmd, capture_output=True, text=True, cwd=compose_file.parent
                        )
                        if simple_result.returncode == 0:
                            running_count = len([s for s in simple_result.stdout.strip().split("\\n") if s.strip()])
                            if running_count >= 3:
                                self.log_success(f"Found {running_count} running services (simple check)")
                                return True
                            else:
                                self.log_error(f"Only {running_count} services running (simple check), expected at least 3")
                                return False
                        else:
                            self.log_error("Could not determine service status")
                            return False
            else:
                self.log_error(f"Service startup failed: {result.stderr}")
                return False

        except Exception as e:
            self.log_error(f"Service startup test failed: {e}")
            return False
        finally:
            # Clean up services
            cleanup_cmd = ["docker", "compose", "-f", str(compose_file), "down", "-v"]
            subprocess.run(cleanup_cmd, capture_output=True, text=True, cwd=compose_file.parent)

    def run_validation(self) -> bool:
        """Run complete validation suite."""
        print("🎯 Starting DCSM Integration Validation")
        print(f"Mode: {'Quick' if self.quick_mode else 'Full'}")
        print(f"Docker: {'Disabled' if self.no_docker else 'Enabled'}")
        print("=" * 60)

        # Step 1: Template structure validation
        self.validate_template_structure()

        # Step 2: Dockerfile validation
        self.validate_dockerfile_structure()

        # Step 3: Template compose file existence check
        self.validate_compose_configuration()

        # Step 4: Template generation test
        project_path = self.test_template_generation()
        if not project_path:
            self.log_error("Cannot continue - template generation failed")
            return False

        # Step 5: Validate generated compose configuration
        self.validate_compose_configuration(project_path)

        # Step 6: Docker build test
        if not self.test_docker_build(project_path):
            self.log_warning("Docker build test failed - may affect DCSM integration")

        # Step 7: Service startup test
        if not self.test_service_startup(project_path):
            self.log_error("Service startup test failed - services are not running properly")

        # Summary
        self.print_summary()

        # Cleanup
        self.cleanup()

        return len(self.errors) == 0

    def cleanup(self) -> None:
        """Clean up temporary files and directories."""
        if hasattr(self, "temp_dir") and Path(self.temp_dir).exists():
            import shutil

            try:
                shutil.rmtree(self.temp_dir)
            except Exception:
                pass  # Don't fail validation due to cleanup issues

    def print_summary(self) -> None:
        """Print validation summary."""
        print("\\n" + "=" * 60)
        print("🎯 VALIDATION SUMMARY")
        print("=" * 60)

        if len(self.errors) == 0:
            print("✅ All critical validations passed!")
            print("🚀 Template is ready for DCSM integration")
        else:
            print(f"❌ {len(self.errors)} critical errors found")
            print("\\nErrors:")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print(f"\\n⚠️  {len(self.warnings)} warnings:")
            for warning in self.warnings:
                print(f"  • {warning}")

        print("\\n📋 Next Steps for Human Tester:")
        print(
            "1. Run full integration tests: "
            "pytest tests/integration/test_dcsm_custom_build_integration.py -v"
        )
        print("2. Test DCSM custom build with actual DCSM installation")
        print("3. Validate Windows authentication preparation")
        print("4. Test with different cookiecutter configurations")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate DCSM integration readiness")
    parser.add_argument("--quick", action="store_true", help="Skip slow integration tests")
    parser.add_argument("--no-docker", action="store_true", help="Skip Docker-dependent tests")

    args = parser.parse_args()

    validator = DCSMValidator(quick_mode=args.quick, no_docker=args.no_docker)
    success = validator.run_validation()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
