"""
Unit tests for deployment_mode template rendering.
Tests the Jinja2 template rendering without Docker execution.
"""
import pytest
import tempfile
import shutil
import os
import yaml
from pathlib import Path
from cookiecutter.main import cookiecutter


class TestDeploymentModeRendering:
    """Test deployment_mode template variable rendering."""

    @pytest.fixture
    def template_dir(self):
        """Return path to the cookiecutter template."""
        return str(Path(__file__).parent.parent.parent)

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for generated projects."""
        temp_dir = tempfile.mkdtemp(prefix="test_deployment_mode_")
        yield temp_dir
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.mark.unit
    def test_production_mode_rendering(self, template_dir, temp_output_dir):
        """Test that production mode (default) renders without test suffixes."""
        result_dir = cookiecutter(
            template_dir,
            no_input=True,
            output_dir=temp_output_dir,
            extra_context={
                'deployment_mode': 'production',
                'customer_slug': 'test-prod'
            }
        )

        # Check compose.yaml
        compose_file = Path(result_dir) / '.devcontainer' / 'compose.yaml'
        assert compose_file.exists()

        with open(compose_file) as f:
            compose_content = f.read()

        # Project name should NOT have -test suffix
        assert 'name: test-prod-etl-modern' in compose_content
        assert 'test-prod-etl-modern-test' not in compose_content

        # Container names should NOT have -test suffix
        assert 'container_name: test-prod-etl-postgres' in compose_content
        assert 'test-prod-etl-postgres-test' not in compose_content

        # Images should be shared fingerprinted images (fingerprinting system replaces project names)
        assert 'data-eng-airflow-dev:' in compose_content, "Should use fingerprinted shared image names"

        # Labels should show production deployment
        assert 'de-template.deployment=production' in compose_content

    @pytest.mark.unit
    def test_testing_mode_rendering(self, template_dir, temp_output_dir):
        """Test that testing mode renders with test suffixes."""
        result_dir = cookiecutter(
            template_dir,
            no_input=True,
            output_dir=temp_output_dir,
            extra_context={
                'deployment_mode': 'testing',
                'customer_slug': 'test-testing'
            }
        )

        # Check compose.yaml
        compose_file = Path(result_dir) / '.devcontainer' / 'compose.yaml'
        assert compose_file.exists()

        with open(compose_file) as f:
            compose_content = f.read()

        # Project name should have -test suffix
        assert 'name: test-testing-etl-modern-test' in compose_content

        # Container names should have -test suffix
        assert 'container_name: test-testing-etl-postgres-test' in compose_content
        assert 'container_name: test-testing-etl-airflow-webserver-test' in compose_content

        # Images should be shared fingerprinted images (fingerprinting system replaces project names)
        assert 'data-eng-airflow-dev:' in compose_content, "Should use fingerprinted shared image names"

        # Labels should show testing deployment
        assert 'de-template.deployment=testing' in compose_content

    @pytest.mark.unit
    def test_fast_test_compose_rendering(self, template_dir, temp_output_dir):
        """Test that compose.test-fast.yaml also renders correctly."""
        result_dir = cookiecutter(
            template_dir,
            no_input=True,
            output_dir=temp_output_dir,
            extra_context={
                'deployment_mode': 'testing',
                'customer_slug': 'test-fast'
            }
        )

        # Check compose.test-fast.yaml
        compose_file = Path(result_dir) / '.devcontainer' / 'compose.test-fast.yaml'
        assert compose_file.exists()

        with open(compose_file) as f:
            compose_content = f.read()

        # Project name should have -test suffix
        assert 'name: test-fast-etl-test-fast-test' in compose_content

        # Container names should have -test suffix
        assert 'container_name: test-fast-etl-postgres-test' in compose_content
        assert 'container_name: test-fast-etl-airflow-init-test' in compose_content

        # Images should have -test suffix
        assert 'test-fast-etl-airflow-fast-test-test' in compose_content

        # Labels should be present
        assert 'de-template.project=test-fast-etl' in compose_content
        assert 'de-template.deployment=testing' in compose_content

    @pytest.mark.unit
    def test_docker_labels_consistency(self, template_dir, temp_output_dir):
        """Test that all services have consistent Docker labels."""
        result_dir = cookiecutter(
            template_dir,
            no_input=True,
            output_dir=temp_output_dir,
            extra_context={
                'deployment_mode': 'testing',
                'customer_slug': 'label-test'
            }
        )

        compose_file = Path(result_dir) / '.devcontainer' / 'compose.yaml'
        with open(compose_file) as f:
            compose_content = f.read()

        # Parse as YAML to verify structure
        compose_data = yaml.safe_load(compose_content)
        services = compose_data['services']

        # Check that all services have required labels
        expected_services = ['postgres', 'airflow-init', 'airflow-scheduler',
                           'airflow-webserver', 'airflow-dag-processor', 'devcontainer']

        for service_name in expected_services:
            assert service_name in services, f"Service {service_name} not found"
            service = services[service_name]

            # Check required labels exist
            assert 'labels' in service, f"Service {service_name} missing labels"
            labels = service['labels']

            # Convert labels to dict for easier checking
            label_dict = {}
            for label in labels:
                key, value = label.split('=', 1)
                label_dict[key] = value

            assert 'de-template.project' in label_dict
            assert 'de-template.deployment' in label_dict
            assert 'de-template.service' in label_dict

            assert label_dict['de-template.project'] == 'label-test-etl'
            assert label_dict['de-template.deployment'] == 'testing'
            assert label_dict['de-template.service'] in [
                'postgres', 'airflow-init', 'airflow-scheduler',
                'airflow-webserver', 'airflow-dag-processor', 'devcontainer'
            ]

    @pytest.mark.unit
    def test_no_literal_jinja_blocks(self, template_dir, temp_output_dir):
        """Test that no literal {% if %} blocks remain in generated files."""
        result_dir = cookiecutter(
            template_dir,
            no_input=True,
            output_dir=temp_output_dir,
            extra_context={
                'deployment_mode': 'testing',
                'customer_slug': 'jinja-test'
            }
        )

        # Check both compose files
        compose_files = [
            Path(result_dir) / '.devcontainer' / 'compose.yaml',
            Path(result_dir) / '.devcontainer' / 'compose.test-fast.yaml'
        ]

        for compose_file in compose_files:
            assert compose_file.exists()
            with open(compose_file) as f:
                content = f.read()

            # Should not contain literal Jinja blocks
            assert '{% if' not in content, f"Found literal Jinja in {compose_file}"
            assert '%}' not in content, f"Found literal Jinja in {compose_file}"
            assert '{{cookiecutter.' not in content, f"Found unrendered cookiecutter var in {compose_file}"

    @pytest.mark.unit
    def test_default_deployment_mode(self, template_dir, temp_output_dir):
        """Test that default deployment mode is production."""
        result_dir = cookiecutter(
            template_dir,
            no_input=True,
            output_dir=temp_output_dir,
            extra_context={
                'customer_slug': 'default-test'
            }
        )

        compose_file = Path(result_dir) / '.devcontainer' / 'compose.yaml'
        with open(compose_file) as f:
            compose_content = f.read()

        # Should default to production mode (no -test suffix)
        assert 'name: default-test-etl-modern' in compose_content
        assert 'default-test-etl-modern-test' not in compose_content
        assert 'de-template.deployment=production' in compose_content