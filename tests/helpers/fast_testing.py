"""Fast testing utilities for development workflow."""

import subprocess
import time
from pathlib import Path
from typing import Dict, Any


def quick_cookiecutter_generation(template_dir: str, temp_dir: Path, config: Dict[str, Any]) -> Path:
    """Generate cookiecutter project with minimal overhead for fast testing."""
    cmd = [
        'cookiecutter', template_dir,
        '--output-dir', str(temp_dir),
        '--no-input'
    ]
    
    for key, value in config.items():
        cmd.append(f"{key}={value}")
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    
    if result.returncode != 0:
        raise RuntimeError(f"Fast generation failed: {result.stderr}")
    
    return temp_dir / config["project_slug"]


def is_compose_healthy(compose_file: Path, timeout: int = 60) -> bool:
    """Quick health check for Docker Compose services."""
    try:
        # Quick check without full startup
        result = subprocess.run([
            'docker', 'compose', '-f', str(compose_file), 'config'
        ], capture_output=True, text=True, timeout=10)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def fast_service_validation(project_dir: Path) -> Dict[str, bool]:
    """Validate generated project structure quickly without Docker startup."""
    checks = {
        "compose_valid": False,
        "airflow_config_exists": False,
        "env_files_exist": False,
        "claude_docs_exist": False,
    }
    
    # Check compose file validity
    compose_file = project_dir / ".devcontainer" / "compose.yaml"
    if compose_file.exists():
        checks["compose_valid"] = is_compose_healthy(compose_file)
    
    # Check Airflow configuration
    airflow_cfg = project_dir / "airflow" / "airflow.cfg"
    checks["airflow_config_exists"] = airflow_cfg.exists()
    
    # Check environment files
    env_file = project_dir / ".devcontainer" / ".env"
    airflow_env = project_dir / ".devcontainer" / "airflow.env"
    checks["env_files_exist"] = env_file.exists() and airflow_env.exists()
    
    # Check CLAUDE.md documentation
    main_claude = project_dir / "CLAUDE.md"
    dags_claude = project_dir / "dags" / "CLAUDE.md"
    checks["claude_docs_exist"] = main_claude.exists() and dags_claude.exists()
    
    return checks


def mock_devcontainer_startup(project_dir: Path) -> Dict[str, Any]:
    """Mock DevContainer startup for testing without actual Docker overhead."""
    return {
        "startup_time": 0.1,  # Simulated fast startup
        "services_healthy": True,
        "ports_accessible": {"airflow": 8080, "postgres": 5432},
        "environment_loaded": True,
    }


def fast_test_project_factory(template_dir: str, temp_dir: Path, config: Dict[str, Any]) -> Path:
    """Factory for creating test projects quickly."""
    return quick_cookiecutter_generation(template_dir, temp_dir, config)


def fast_devcontainer_up(project_dir: Path, timeout: int = 30) -> Dict[str, Any]:
    """Fast mock implementation of devcontainer startup."""
    # For fast tests, just validate compose file and return mock results
    compose_file = project_dir / ".devcontainer" / "compose.yaml"
    
    if not compose_file.exists():
        return {"success": False, "error": "compose.yaml not found"}
    
    # Validate compose file syntax
    try:
        result = subprocess.run([
            'docker', 'compose', '-f', str(compose_file), 'config'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            return {"success": False, "error": f"Invalid compose file: {result.stderr}"}
        
        # Mock successful startup
        return {
            "success": True,
            "startup_time": 0.5,
            "services": ["postgres", "airflow-webserver", "airflow-scheduler"],
            "ports": {"8080": "airflow", "5432": "postgres"}
        }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Docker validation timeout"}


def fast_devcontainer_down(project_dir: Path) -> Dict[str, Any]:
    """Fast mock implementation of devcontainer shutdown."""
    # For fast tests, just return success
    return {"success": True, "cleanup_time": 0.1}


def fast_test_base_image() -> str:
    """Return base image for fast testing."""
    # For fast tests, use a minimal base image
    return "python:3.12-slim"