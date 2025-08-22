"""Type-safe configuration settings with Hydra integration.

This module defines Pydantic settings classes that provide type safety,
validation, and IDE support for all configuration options. The settings
are automatically populated from Hydra configuration files.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote_plus

from hydra import compose, initialize_config_dir
from omegaconf import DictConfig, OmegaConf
from pydantic import BaseModel, Field, validator, root_validator


class ProjectSettings(BaseModel):
    """Project metadata and basic information."""
    
    name: str = Field(..., description="Human-readable project name")
    slug: str = Field(..., description="URL-safe project identifier")
    author: str = Field(..., description="Project author or team")
    description: Optional[str] = Field(None, description="Project description")
    python_version: str = Field("3.12", description="Python version requirement")


class RuntimeSettings(BaseModel):
    """Runtime execution configuration."""
    
    log_level: str = Field("INFO", description="Logging level")
    debug_mode: bool = Field(False, description="Enable debug features")
    dry_run: bool = Field(False, description="Preview mode without execution")
    parallel_jobs: int = Field(4, description="Number of parallel jobs")
    timeout_seconds: int = Field(3600, description="Default operation timeout")
    retry_attempts: int = Field(3, description="Number of retry attempts")
    output_dir: str = Field("./outputs", description="Output directory")
    temp_dir: str = Field("./temp", description="Temporary directory")


class DatabaseSettings(BaseModel):
    """Database connection and configuration."""
    
    host: str = Field(..., description="Database host")
    port: int = Field(5432, description="Database port")
    name: str = Field(..., description="Database name")
    user: str = Field(..., description="Database user")
    password: str = Field(..., description="Database password")
    schema: Optional[str] = Field(None, description="Default schema")
    
    # Connection pool settings
    pool_size: int = Field(5, description="Connection pool size")
    max_overflow: int = Field(10, description="Maximum pool overflow")
    timeout: int = Field(30, description="Connection timeout")
    
    # PostgreSQL specific settings
    sslmode: str = Field("require", description="SSL mode")
    connect_timeout: int = Field(10, description="Connect timeout")
    
    @property
    def connection_url(self) -> str:
        """Generate SQLAlchemy connection URL."""
        password_encoded = quote_plus(self.password)
        return f"postgresql://{self.user}:{password_encoded}@{self.host}:{self.port}/{self.name}"
    
    @property
    def async_connection_url(self) -> str:
        """Generate async SQLAlchemy connection URL."""
        return self.connection_url.replace("postgresql://", "postgresql+asyncpg://")


class OrchestrationSettings(BaseModel):
    """Orchestration system configuration (Airflow, Prefect, etc.)."""
    
    # Core settings
    executor: str = Field("LocalExecutor", description="Task executor type")
    dags_folder: str = Field("./dags", description="DAGs directory")
    parallelism: int = Field(4, description="Max parallel tasks")
    dag_concurrency: int = Field(2, description="Max tasks per DAG")
    
    # Database connection
    sql_alchemy_conn: Optional[str] = Field(None, description="Metadata database connection")
    
    # Webserver settings
    web_server_port: int = Field(8080, description="Webserver port")
    base_url: str = Field("http://localhost:8080", description="Base URL")
    
    # Logging
    base_log_folder: str = Field("./logs", description="Log directory")
    logging_level: str = Field("INFO", description="Logging level")


class TransformationSettings(BaseModel):
    """Data transformation configuration (dbt, etc.)."""
    
    # Project settings
    project_name: str = Field(..., description="Transformation project name")
    profile_name: str = Field(..., description="Profile name")
    target: str = Field("dev", description="Target environment")
    
    # Paths
    model_paths: List[str] = Field(["models"], description="Model directories")
    test_paths: List[str] = Field(["tests"], description="Test directories") 
    seed_paths: List[str] = Field(["seeds"], description="Seed directories")
    
    # Execution settings
    threads: int = Field(2, description="Number of threads")
    full_refresh: bool = Field(False, description="Full refresh mode")
    
    # Development features
    partial_parse: bool = Field(True, description="Enable partial parsing")
    use_colors: bool = Field(True, description="Colored output")
    warn_error: bool = Field(False, description="Treat warnings as errors")


class ComputeSettings(BaseModel):
    """Compute resource configuration."""
    
    # Resource limits
    max_cpu_cores: int = Field(4, description="Maximum CPU cores")
    max_memory_gb: int = Field(8, description="Maximum memory (GB)")
    
    # Processing settings
    max_parallel_jobs: int = Field(2, description="Max parallel jobs")
    default_job_timeout: int = Field(1800, description="Default job timeout")
    
    # Framework settings
    enable_pandas: bool = Field(True, description="Enable pandas processing")
    enable_spark: bool = Field(False, description="Enable Spark processing")
    
    # I/O settings
    read_batch_size: int = Field(50000, description="Read batch size")
    write_batch_size: int = Field(10000, description="Write batch size")


class PipelineSettings(BaseModel):
    """Data pipeline configuration."""
    
    # Data quality
    enable_data_quality_checks: bool = Field(True, description="Enable data quality validation")
    fail_on_quality_error: bool = Field(True, description="Fail on data quality errors")
    quality_sample_size: int = Field(10000, description="Sample size for quality checks")
    
    # Incremental loading
    enable_incremental: bool = Field(True, description="Enable incremental loading")
    lookback_days: int = Field(1, description="Lookback days for incremental")
    
    # Metadata and lineage
    enable_lineage: bool = Field(True, description="Track data lineage")
    enable_profiling: bool = Field(True, description="Enable data profiling")


class MonitoringSettings(BaseModel):
    """Monitoring and observability configuration."""
    
    enable_metrics: bool = Field(True, description="Enable metrics collection")
    metrics_endpoint: Optional[str] = Field(None, description="Metrics endpoint URL")
    enable_alerts: bool = Field(False, description="Enable alerting")
    alert_channels: List[str] = Field([], description="Alert notification channels")


class Settings(BaseModel):
    """Main settings class combining all configuration sections."""
    
    project: ProjectSettings
    runtime: RuntimeSettings
    database: DatabaseSettings
    orchestration: OrchestrationSettings
    transformations: TransformationSettings
    compute: ComputeSettings
    pipeline: PipelineSettings
    monitoring: MonitoringSettings
    
    # Raw Hydra config for advanced usage
    _hydra_cfg: Optional[DictConfig] = Field(None, exclude=True)
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow additional fields from Hydra config
        validate_assignment = True
        
    @root_validator(pre=True)
    def validate_settings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate settings and apply cross-field validation."""
        # Ensure database schema defaults to project slug if not specified
        if "database" in values and values["database"].get("schema") is None:
            if "project" in values:
                values["database"]["schema"] = values["project"]["slug"]
        
        return values
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.runtime.debug_mode or self.transformations.target == "dev"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.transformations.target == "prod" and not self.runtime.debug_mode


def initialize_config(
    config_dir: Optional[Union[str, Path]] = None,
    config_name: str = "config"
) -> DictConfig:
    """Initialize Hydra configuration.
    
    Args:
        config_dir: Configuration directory path. Defaults to ./conf
        config_name: Name of the config file. Defaults to "config"
        
    Returns:
        Hydra configuration object
    """
    if config_dir is None:
        config_dir = Path.cwd() / "conf"
    
    config_dir = Path(config_dir).resolve()
    
    if not config_dir.exists():
        raise FileNotFoundError(f"Configuration directory not found: {config_dir}")
    
    # Initialize Hydra configuration
    with initialize_config_dir(
        config_dir=str(config_dir), 
        version_base="1.1"
    ):
        cfg = compose(config_name=config_name)
    
    return cfg


def get_settings(
    config_dir: Optional[Union[str, Path]] = None,
    config_name: str = "config",
    overrides: Optional[List[str]] = None,
    environment: Optional[str] = None
) -> Settings:
    """Get application settings from Hydra configuration.
    
    Args:
        config_dir: Configuration directory path
        config_name: Name of the config file
        overrides: List of configuration overrides
        environment: Environment to load (dev, staging, prod)
        
    Returns:
        Validated settings object
        
    Examples:
        >>> # Load default configuration
        >>> settings = get_settings()
        
        >>> # Load production environment
        >>> settings = get_settings(environment="prod")
        
        >>> # Override database host
        >>> settings = get_settings(overrides=["database.host=prod-db.example.com"])
    """
    if config_dir is None:
        config_dir = Path.cwd() / "conf"
    
    config_dir = Path(config_dir).resolve()
    
    # Build overrides list
    override_list = overrides or []
    
    # Add environment override if specified
    if environment:
        override_list.append(f"environment={environment}")
    
    # Check for environment variable overrides
    env_overrides = _get_env_overrides()
    override_list.extend(env_overrides)
    
    # Initialize and compose configuration
    with initialize_config_dir(
        config_dir=str(config_dir),
        version_base="1.1"
    ):
        cfg = compose(
            config_name=config_name,
            overrides=override_list
        )
    
    # Convert to container for Pydantic
    config_dict = OmegaConf.to_container(cfg, resolve=True)
    
    # Create settings object
    settings = Settings(**config_dict)
    settings._hydra_cfg = cfg
    
    return settings


def _get_env_overrides() -> List[str]:
    """Extract configuration overrides from environment variables.
    
    Environment variables with prefix DATA_ENG_ are converted to Hydra overrides.
    For example: DATA_ENG_DATABASE_HOST=localhost becomes database.host=localhost
    """
    overrides = []
    prefix = "DATA_ENG_"
    
    for key, value in os.environ.items():
        if key.startswith(prefix):
            # Convert from DATA_ENG_DATABASE_HOST to database.host
            config_key = key[len(prefix):].lower().replace("_", ".")
            overrides.append(f"{config_key}={value}")
    
    return overrides