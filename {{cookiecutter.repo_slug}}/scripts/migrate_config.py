#!/usr/bin/env python3
"""Configuration migration utility.

This script helps migrate from the old .env-based configuration
to the new Hydra-based configuration system.

Usage:
    python scripts/migrate_config.py --env-file .env --output-dir conf/local
"""

import argparse
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import os


def parse_env_file(env_file: Path) -> Dict[str, str]:
    """Parse .env file into key-value pairs."""
    env_vars = {}
    
    if not env_file.exists():
        logging.warning(f"Environment file not found: {env_file}")
        return env_vars
    
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
                
            # Parse KEY=VALUE format
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                env_vars[key] = value
    
    return env_vars


def map_env_to_config(env_vars: Dict[str, str]) -> Dict[str, Any]:
    """Map environment variables to Hydra configuration structure."""
    config = {
        'project': {},
        'runtime': {},
        'database': {},
        'orchestration': {},
        'transformations': {},
        'pipeline': {},
        'monitoring': {}
    }
    
    # Mapping from env var names to config paths
    env_mappings = {
        # Database configuration
        'DB_HOST': 'database.host',
        'POSTGRES_HOST': 'database.host',
        'DB_PORT': 'database.port',  
        'POSTGRES_PORT': 'database.port',
        'DB_NAME': 'database.name',
        'POSTGRES_DB': 'database.name',
        'DB_USER': 'database.user',
        'POSTGRES_USER': 'database.user', 
        'DB_PASSWORD': 'database.password',
        'POSTGRES_PASSWORD': 'database.password',
        
        # Airflow configuration
        'AIRFLOW_EXECUTOR': 'orchestration.executor',
        'AIRFLOW__CORE__EXECUTOR': 'orchestration.executor',
        'AIRFLOW__WEBSERVER__WEB_SERVER_PORT': 'orchestration.web_server_port',
        'AIRFLOW__CORE__PARALLELISM': 'orchestration.parallelism',
        'AIRFLOW__CORE__DAG_CONCURRENCY': 'orchestration.dag_concurrency',
        'AIRFLOW__CORE__LOAD_EXAMPLES': 'orchestration.load_examples',
        
        # Runtime configuration
        'LOG_LEVEL': 'runtime.log_level',
        'DEBUG': 'runtime.debug_mode',
        'DRY_RUN': 'runtime.dry_run',
        'PARALLEL_JOBS': 'runtime.parallel_jobs',
        
        # Python/Project configuration
        'PYTHON_VERSION': 'project.python_version',
        'PROJECT_NAME': 'project.name',
        'AUTHOR_NAME': 'project.author',
        
        # dbt configuration
        'DBT_PROFILES_DIR': 'transformations.profiles_dir',
        'DBT_TARGET': 'transformations.target',
        'DBT_THREADS': 'transformations.threads',
    }
    
    # Apply mappings
    for env_key, config_path in env_mappings.items():
        if env_key in env_vars:
            value = env_vars[env_key]
            
            # Type conversion
            if config_path.endswith(('.port', '.parallelism', '.threads', 'parallel_jobs')):
                try:
                    value = int(value)
                except ValueError:
                    logging.warning(f"Could not convert {env_key}={value} to integer")
                    continue
            elif config_path.endswith(('.debug_mode', '.dry_run', '.load_examples')):
                value = value.lower() in ('true', '1', 'yes', 'on')
            
            # Set nested config value
            _set_nested_config(config, config_path, value)
    
    # Handle special cases
    _handle_special_cases(env_vars, config)
    
    return config


def _set_nested_config(config: Dict[str, Any], path: str, value: Any) -> None:
    """Set a nested configuration value using dot notation."""
    parts = path.split('.')
    current = config
    
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]
    
    current[parts[-1]] = value


def _handle_special_cases(env_vars: Dict[str, str], config: Dict[str, Any]) -> None:
    """Handle special configuration cases that don't map directly."""
    
    # Database connection URL construction
    if all(key in env_vars for key in ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_NAME']):
        db_user = env_vars['DB_USER']
        db_password = env_vars['DB_PASSWORD'] 
        db_host = env_vars['DB_HOST']
        db_name = env_vars['DB_NAME']
        db_port = env_vars.get('DB_PORT', '5432')
        
        sql_alchemy_conn = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        config['orchestration']['sql_alchemy_conn'] = sql_alchemy_conn
    
    # Environment detection
    environment = 'dev'
    if env_vars.get('ENVIRONMENT') == 'prod':
        environment = 'prod'
    elif env_vars.get('ENVIRONMENT') == 'staging':
        environment = 'staging'
    
    config['transformations']['target'] = environment
    
    # Enable/disable features based on environment
    if environment == 'prod':
        config['pipeline']['fail_on_quality_error'] = True
        config['runtime']['debug_mode'] = False
        config['monitoring']['enable_metrics'] = True
    else:
        config['pipeline']['fail_on_quality_error'] = False
        config['runtime']['debug_mode'] = True
        config['monitoring']['enable_metrics'] = False


def generate_config_files(config: Dict[str, Any], output_dir: Path) -> None:
    """Generate Hydra configuration files from parsed config."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate main override file
    main_config_file = output_dir / "config.yaml"
    with open(main_config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    logging.info(f"Generated main config override: {main_config_file}")
    
    # Generate component-specific override files
    for component in ['database', 'orchestration', 'transformations']:
        if component in config and config[component]:
            component_file = output_dir / f"{component}.yaml"
            component_config = {component: config[component]}
            
            with open(component_file, 'w') as f:
                f.write(f"# @package _global_\n\n")
                yaml.dump(component_config, f, default_flow_style=False, sort_keys=False)
            
            logging.info(f"Generated {component} config override: {component_file}")


def create_migration_guide(output_dir: Path) -> None:
    """Create a migration guide for users."""
    guide_file = output_dir / "MIGRATION_GUIDE.md"
    
    guide_content = """# Configuration Migration Guide

Your .env configuration has been migrated to Hydra YAML format.

## Generated Files

- `config.yaml` - Main configuration overrides
- `database.yaml` - Database-specific overrides  
- `orchestration.yaml` - Airflow/orchestration overrides
- `transformations.yaml` - dbt transformation overrides

## Usage

### Option 1: Use local overrides directory
Move the generated files to `conf/local/` to automatically apply them:
```bash
mkdir -p conf/local
mv {output_dir}/*.yaml conf/local/
```

### Option 2: Use command-line overrides
Reference specific config files when running:
```bash
python scripts/run_pipeline.py --config-path {output_dir} --config-name config
```

### Option 3: Environment variable overrides
Set environment variables with DATA_ENG_ prefix:
```bash
export DATA_ENG_DATABASE_HOST=localhost
export DATA_ENG_RUNTIME_DEBUG_MODE=true
python scripts/run_pipeline.py
```

## Next Steps

1. Review the generated configuration files
2. Test with your existing setup
3. Gradually adopt the new Hydra features
4. Remove the old .env file once migration is complete

## Need Help?

See the main CLAUDE.md for detailed Hydra configuration documentation.
"""
    
    with open(guide_file, 'w') as f:
        f.write(guide_content.format(output_dir=output_dir))
    
    logging.info(f"Generated migration guide: {guide_file}")


def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(description="Migrate .env configuration to Hydra")
    parser.add_argument(
        "--env-file", 
        type=Path, 
        default=Path(".env"),
        help="Path to .env file to migrate"
    )
    parser.add_argument(
        "--output-dir",
        type=Path, 
        default=Path("conf/local"),
        help="Output directory for generated config files"
    )
    parser.add_argument(
        "--log-level",
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logging.info(f"Starting configuration migration from {args.env_file}")
    
    try:
        # Parse environment file
        env_vars = parse_env_file(args.env_file)
        
        if not env_vars:
            logging.warning("No environment variables found to migrate")
            return
        
        logging.info(f"Found {len(env_vars)} environment variables to migrate")
        
        # Map to Hydra config structure
        config = map_env_to_config(env_vars)
        
        # Generate configuration files
        generate_config_files(config, args.output_dir)
        
        # Create migration guide
        create_migration_guide(args.output_dir)
        
        logging.info("Migration completed successfully!")
        logging.info(f"Review generated files in: {args.output_dir}")
        
    except Exception as e:
        logging.error(f"Migration failed: {e}")
        raise


if __name__ == "__main__":
    main()