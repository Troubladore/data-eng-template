"""Configuration management for {{cookiecutter.project_name}}.

This module provides Hydra-based configuration management with type-safe
Pydantic settings classes. It supports hierarchical configuration composition,
environment-specific overrides, and seamless integration with the data pipeline.

Example usage:
    from {{cookiecutter.repo_slug}}.config import get_settings
    
    # Load default configuration
    settings = get_settings()
    
    # Load with environment override
    settings = get_settings(environment="prod")
    
    # Load with command-line overrides
    settings = get_settings(overrides=["database.host=prod-db.example.com"])
"""

from .settings import (
    ProjectSettings,
    DatabaseSettings, 
    OrchestrationSettings,
    TransformationSettings,
    ComputeSettings,
    get_settings,
    initialize_config
)

__all__ = [
    "ProjectSettings",
    "DatabaseSettings", 
    "OrchestrationSettings",
    "TransformationSettings", 
    "ComputeSettings",
    "get_settings",
    "initialize_config"
]