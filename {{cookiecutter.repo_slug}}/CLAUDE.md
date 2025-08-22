# {{cookiecutter.project_name}} - Data Engineering Project

**Generated from data-eng-template**: This is a modern data engineering project with **Hydra configuration management**, Airflow, dbt, PostgreSQL, and DevContainer using medallion architecture.

## Configuration System

This project uses **Hydra** for unified configuration management, providing:

- **Hierarchical Configuration**: Compose configs from multiple sources
- **Type Safety**: Pydantic validation with IDE support  
- **Environment Management**: Dev/staging/prod with automatic overrides
- **Command-Line Overrides**: Change any setting without editing files
- **Self-Documenting**: All config options include inline documentation

### Quick Start

```bash
# Run with default (development) configuration
python scripts/run_pipeline.py

# Run with production environment
python scripts/run_pipeline.py environment=prod

# Override specific settings
python scripts/run_pipeline.py database.host=prod-db.example.com runtime.parallel_jobs=8

# Dry run mode (preview without execution)
python scripts/run_pipeline.py runtime.dry_run=true
```

### Configuration Structure

- `conf/config.yaml` - Main configuration with sensible defaults
- `conf/environment/` - Environment-specific settings (dev/staging/prod)
- `conf/database/` - Database provider configurations
- `conf/orchestration/` - Airflow and orchestration settings
- `conf/transformations/` - dbt and transformation settings
- `conf/compute/` - Resource allocation and processing framework configs

---

## Project Structure

- **dags/**: Airflow DAG definitions (see `dags/CLAUDE.md` for specific guidance)
- **dbt/**: Data modeling and transformations (see `dbt/CLAUDE.md`)  
- **transforms/**: SQLModel/Pydantic data models (see `transforms/CLAUDE.md`)
- **scripts/**: Helper utilities and operations (see `scripts/CLAUDE.md`)

## Medallion Architecture

- **Bronze Layer**: Raw data ingestion with minimal processing
- **Silver Layer**: Cleaned, validated, and conformed data  
- **Gold Layer**: Business-ready aggregations and metrics

## Development Environment

- **Airflow UI**: http://localhost:8080 (admin/admin)
- **Database**: PostgreSQL on localhost:5432
- **Author**: {{cookiecutter.author_name}}

## Layer-Specific Guidance

Each directory contains detailed CLAUDE.md files with specific guidance for that layer:

- See `dags/CLAUDE.md` for Airflow DAG patterns
- See `dbt/CLAUDE.md` for data modeling guidance
- See `transforms/CLAUDE.md` for SQLModel patterns
- See `scripts/CLAUDE.md` for operational utilities

This distributed guidance approach provides contextual AI assistance exactly where developers need it.