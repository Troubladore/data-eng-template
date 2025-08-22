"""Test-driven development tests for enhanced Airflow deployment with caching mechanisms.

These tests define the expected behavior for our Astronomer-inspired packaged
developer deployment model before implementation.
"""

import json
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, Any
import pytest


class TestDockerCachingAndMultiStage:
    """Test Docker layer caching and multi-stage build capabilities."""
    
    def test_dockerfile_exists_with_multistage_structure(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that optimized Dockerfile with multi-stage builds exists."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        dockerfile_path = project_dir / "Dockerfile.airflow"
        
        assert dockerfile_path.exists(), "Optimized Dockerfile.airflow must exist"
        
        dockerfile_content = dockerfile_path.read_text()
        
        # Test multi-stage build structure
        assert "FROM" in dockerfile_content, "Dockerfile must have base image"
        assert "AS dependencies" in dockerfile_content, "Must have dependencies stage"
        assert "AS runtime" in dockerfile_content, "Must have runtime stage"
        
        # Test dependency caching optimization
        assert "requirements.txt" in dockerfile_content, "Must copy requirements first for caching"
        assert "RUN uv pip install" in dockerfile_content or "RUN pip install" in dockerfile_content, "Must install dependencies in separate layer"
        
        # Test .dockerignore exists
        dockerignore_path = project_dir / ".dockerignore"
        assert dockerignore_path.exists(), ".dockerignore must exist for build optimization"
        
        dockerignore_content = dockerignore_path.read_text()
        assert "*.pyc" in dockerignore_content or "*.py[cod]" in dockerignore_content, "Must ignore Python cache files"
        assert "__pycache__" in dockerignore_content, "Must ignore Python cache directories"
        assert ".git" in dockerignore_content, "Must ignore git directory"
    
    def test_dockerfile_has_dependency_caching_layers(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that Dockerfile properly separates dependency installation for caching."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        dockerfile_path = project_dir / "Dockerfile.airflow"
        
        dockerfile_content = dockerfile_path.read_text()
        
        # Test that dependencies stage exists and has proper structure
        assert "FROM apache/airflow" in dockerfile_content, "Must have Airflow base image"
        assert "AS dependencies" in dockerfile_content, "Must have dependencies stage"
        assert "AS runtime" in dockerfile_content, "Must have runtime stage"
        
        # Test that requirements are copied before installation in dependencies stage
        dependencies_section = dockerfile_content.split("AS runtime")[0]
        runtime_section = dockerfile_content.split("AS runtime")[1] if "AS runtime" in dockerfile_content else ""
        
        assert "requirements.txt" in dependencies_section, "Requirements must be in dependencies stage"
        assert "uv pip install" in dependencies_section or "pip install" in dependencies_section, "Dependencies must be installed in dependencies stage"
        
        # Test that application code is copied in runtime stage
        assert "dags/" in runtime_section or "COPY" in runtime_section, "Application code must be copied in runtime stage"


class TestDAGOnlyDeployment:
    """Test DAG-only deployment capabilities for fast iterations."""
    
    def test_dag_deploy_script_exists(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that DAG-only deployment script exists."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        deploy_script = project_dir / "scripts" / "deploy.py"
        
        assert deploy_script.exists(), "DAG deployment script must exist"
        assert deploy_script.is_file(), "Deploy script must be a file"
        
        # Test script is executable
        import stat
        file_stat = deploy_script.stat()
        assert file_stat.st_mode & stat.S_IEXEC, "Deploy script must be executable"
    
    def test_deploy_script_supports_dag_only_mode(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that deployment script supports DAG-only deployment mode."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        
        # Test help output includes DAG-only option
        result = subprocess.run(
            ['python', 'scripts/deploy.py', '--help'],
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, "Deploy script help should work"
        assert "--dags-only" in result.stdout, "Must support --dags-only flag"
        assert "--detect-changes" in result.stdout, "Must support automatic change detection"
        assert "--full" in result.stdout, "Must support full deployment mode"
    
    def test_change_detection_logic(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that deployment script can detect what changed and choose appropriate strategy."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        
        # Test dry-run mode to check change detection
        result = subprocess.run(
            ['python', 'scripts/deploy.py', '--detect-changes', '--dry-run'],
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, "Change detection should work"
        assert "Recommended strategy:" in result.stdout or "Deployment strategy:" in result.stdout, "Should output detected strategy"


class TestLocalDevelopmentOptimization:
    """Test local development workflow optimizations."""
    
    def test_dev_compose_has_caching_optimizations(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that dev compose configuration includes caching optimizations."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        compose_file = project_dir / ".devcontainer" / "compose.yaml"
        
        compose_content = compose_file.read_text()
        
        # Test for volume caching optimizations
        assert "cached" in compose_content or "delegated" in compose_content, "Should have volume mount optimizations"
        
        # Test for dependency caching
        assert "pip_cache" in compose_content or "uv_cache" in compose_content, "Should cache Python dependencies"
    
    def test_dev_environment_supports_hot_reload(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that development environment supports DAG hot-reloading."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        
        # Check Airflow configuration for hot-reload settings
        airflow_config = project_dir / "conf" / "orchestration" / "airflow_local.yaml"
        config_content = airflow_config.read_text()
        
        # Test for development-friendly settings
        assert "dag_dir_list_interval" in config_content, "Must have DAG scanning interval"
        assert "dag_discovery_safe_mode: false" in config_content, "Should disable safe mode for faster reload"


class TestDeploymentConfiguration:
    """Test Hydra configuration for different deployment strategies."""
    
    def test_deployment_config_exists(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that deployment configuration files exist."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        
        # Test for deployment configuration files
        deployment_configs = [
            "conf/deployment/local.yaml",
            "conf/deployment/dev.yaml", 
            "conf/deployment/prod.yaml"
        ]
        
        for config_path in deployment_configs:
            config_file = project_dir / config_path
            assert config_file.exists(), f"Deployment config {config_path} must exist"
    
    def test_deployment_config_has_caching_settings(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that deployment configs include caching-related settings."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        
        local_config = project_dir / "conf" / "deployment" / "local.yaml"
        config_content = local_config.read_text()
        
        # Test for caching-related configuration
        assert "docker" in config_content, "Should have Docker configuration"
        assert "build_args" in config_content or "cache" in config_content, "Should have caching configuration"


class TestPerformanceOptimization:
    """Test performance optimizations and monitoring."""
    
    def test_build_time_measurement_exists(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that build time measurement is included."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        
        # Test that deployment script includes timing
        deploy_script = project_dir / "scripts" / "deploy.py"
        script_content = deploy_script.read_text()
        
        assert "time" in script_content.lower(), "Deploy script should measure timing"
        assert "duration" in script_content.lower() or "elapsed" in script_content.lower(), "Should report deployment duration"
    
    def test_makefile_has_deployment_targets(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that Makefile includes deployment targets."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        makefile = project_dir / "Makefile"
        
        makefile_content = makefile.read_text()
        
        # Test for deployment-related make targets
        assert "deploy-dags:" in makefile_content, "Should have DAG-only deploy target"
        assert "deploy-full:" in makefile_content, "Should have full deploy target"  
        assert "deploy-auto:" in makefile_content, "Should have auto-detect deploy target"


class TestDocumentationAndExamples:
    """Test that deployment features are properly documented."""
    
    def test_deployment_documentation_exists(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that deployment documentation exists and is comprehensive."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        
        # Test for deployment documentation
        deployment_docs = project_dir / "docs" / "deployment"
        assert deployment_docs.exists(), "Deployment documentation directory must exist"
        
        readme = deployment_docs / "README.md"
        assert readme.exists(), "Deployment README must exist"
        
        readme_content = readme.read_text()
        
        # Test documentation coverage
        assert "DAG-only deployment" in readme_content, "Must document DAG-only deployment"
        assert "Docker Caching Optimization" in readme_content or "Docker layer caching" in readme_content, "Must document Docker caching"
        assert "deployment strategies" in readme_content.lower(), "Must document deployment strategies"
    
    def test_example_cicd_workflow_exists(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that example CI/CD workflows exist."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        
        # Test for GitHub Actions workflow
        github_workflows = project_dir / ".github" / "workflows"
        assert github_workflows.exists(), "GitHub workflows directory must exist"
        
        deploy_workflow = github_workflows / "deploy.yml"
        assert deploy_workflow.exists(), "Deploy workflow must exist"
        
        workflow_content = deploy_workflow.read_text()
        
        # Test workflow includes smart deployment logic
        assert "detect-changes" in workflow_content or "dags-only" in workflow_content, "Workflow should use smart deployment"