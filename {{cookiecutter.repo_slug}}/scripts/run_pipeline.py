#!/usr/bin/env python3
"""Data pipeline runner with Hydra configuration management.

This script demonstrates how to use the Hydra-based configuration system
to run data pipelines with different environments and overrides.

Examples:
    # Run with default (dev) configuration
    python scripts/run_pipeline.py
    
    # Run with production configuration
    python scripts/run_pipeline.py environment=prod
    
    # Override specific settings
    python scripts/run_pipeline.py database.host=prod-db.example.com runtime.parallel_jobs=8
    
    # Combine environment and overrides
    python scripts/run_pipeline.py environment=staging orchestration.parallelism=16
    
    # Dry run mode
    python scripts/run_pipeline.py runtime.dry_run=true
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import hydra
from omegaconf import DictConfig, OmegaConf

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from {{cookiecutter.repo_slug}}.config import get_settings, Settings


def setup_logging(settings: Settings) -> None:
    """Configure logging based on settings."""
    logging.basicConfig(
        level=getattr(logging, settings.runtime.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(Path(settings.runtime.output_dir) / "pipeline.log")
        ]
    )


def validate_configuration(settings: Settings) -> None:
    """Validate configuration before pipeline execution."""
    logger = logging.getLogger(__name__)
    
    logger.info("Validating configuration...")
    
    # Check required directories exist
    output_dir = Path(settings.runtime.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    temp_dir = Path(settings.runtime.temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Validate database connection (in production)
    if settings.is_production and not settings.runtime.dry_run:
        logger.info("Production mode: validating database connection...")
        # Here you would add actual database connection validation
        logger.info(f"Database: {settings.database.host}:{settings.database.port}/{settings.database.name}")
    
    # Validate resource limits
    if settings.compute.max_memory_gb > 32:
        logger.warning(f"High memory allocation: {settings.compute.max_memory_gb}GB")
    
    logger.info("Configuration validation complete")


def run_bronze_layer(settings: Settings) -> None:
    """Run bronze layer data ingestion."""
    logger = logging.getLogger(__name__)
    
    logger.info("Starting bronze layer processing...")
    
    if settings.runtime.dry_run:
        logger.info("DRY RUN: Would ingest raw data to bronze layer")
        return
    
    # Bronze layer processing logic would go here
    logger.info("Bronze layer processing complete")


def run_silver_layer(settings: Settings) -> None:
    """Run silver layer data cleaning and normalization."""
    logger = logging.getLogger(__name__)
    
    logger.info("Starting silver layer processing...")
    
    if settings.runtime.dry_run:
        logger.info("DRY RUN: Would clean and normalize data in silver layer")
        return
    
    # Silver layer processing logic would go here
    logger.info("Silver layer processing complete")


def run_gold_layer(settings: Settings) -> None:
    """Run gold layer business logic and aggregations."""
    logger = logging.getLogger(__name__)
    
    logger.info("Starting gold layer processing...")
    
    if settings.runtime.dry_run:
        logger.info("DRY RUN: Would apply business logic in gold layer")
        return
    
    # Gold layer processing logic would go here
    logger.info("Gold layer processing complete")


def run_data_quality_checks(settings: Settings) -> None:
    """Run data quality validation."""
    logger = logging.getLogger(__name__)
    
    if not settings.pipeline.enable_data_quality_checks:
        logger.info("Data quality checks disabled")
        return
    
    logger.info("Running data quality checks...")
    
    if settings.runtime.dry_run:
        logger.info("DRY RUN: Would validate data quality")
        return
    
    # Data quality check logic would go here
    logger.info("Data quality checks complete")


@hydra.main(version_base="1.1", config_path="../conf", config_name="config")
def main(cfg: DictConfig) -> None:
    """Main pipeline execution function with Hydra integration."""
    # Convert Hydra config to our typed settings
    config_dict = OmegaConf.to_container(cfg, resolve=True)
    settings = Settings(**config_dict)
    settings._hydra_cfg = cfg
    
    # Setup logging
    setup_logging(settings)
    logger = logging.getLogger(__name__)
    
    # Log configuration summary
    logger.info("="*50)
    logger.info(f"Starting {{cookiecutter.project_name}} Pipeline")
    logger.info(f"Environment: {settings.transformations.target}")
    logger.info(f"Debug Mode: {settings.runtime.debug_mode}")
    logger.info(f"Dry Run: {settings.runtime.dry_run}")
    logger.info(f"Parallel Jobs: {settings.runtime.parallel_jobs}")
    logger.info("="*50)
    
    try:
        # Validate configuration
        validate_configuration(settings)
        
        # Run pipeline stages
        run_bronze_layer(settings)
        run_silver_layer(settings)
        run_gold_layer(settings)
        
        # Run data quality checks
        run_data_quality_checks(settings)
        
        logger.info("Pipeline execution completed successfully!")
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        if settings.runtime.debug_mode:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()