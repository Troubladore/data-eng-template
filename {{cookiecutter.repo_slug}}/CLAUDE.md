# {{cookiecutter.project_name}} - Data Engineering Project

**Generated from data-eng-template**: This is a modern data engineering project with **Hydra configuration management**, **Custom Airflow Integration**, **Dependency Isolation**, PostgreSQL, and DevContainer using medallion architecture.

## Service Management

This project uses **Docker Compose** with a custom Airflow image for clean, reliable service orchestration:

- **Custom Airflow Image**: Built with your project dependencies at `{{cookiecutter.repo_slug}}-airflow-dev`
- **Modern Unified Stack**: Airflow 3.0.6 with SQLAlchemy 2.0+ throughout (no isolation needed)
- **Modern Port Management**: Airflow UI on port 8081, Postgres on dynamic port
- **Clean Dependencies**: Services start in correct order with health checks
- **Project Isolation**: Named compose project prevents conflicts

### Service Commands

```bash
# Start all services (builds custom Airflow image automatically)
cd .devcontainer
docker compose up -d

# Stop services
docker compose down

# Restart from clean state
docker compose down -v && docker compose up -d

# Check service status
docker compose ps
```

**Key Points:**
- Docker Compose automatically builds the custom Airflow image on first run
- No manual Docker build commands needed
- Services are automatically started by DevContainer via `postCreateCommand`

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

### Development Environment Setup

The DevContainer is fully integrated with the Hydra configuration system:

1. **Open in DevContainer**: Configuration is set up automatically during container creation
2. **No Manual .env Files**: Environment variables are generated from Hydra configs
3. **Dynamic Configuration**: Changes to `conf/` files are reflected after container restart
4. **Local Overrides**: Create `conf/local/custom.yaml` for personal development settings

**Key Points**:
- `.env` files are **generated automatically** - do not edit manually
- All configuration managed through `conf/` directory hierarchy  
- Environment variables sourced from Hydra during container startup
- Services (Airflow, PostgreSQL) configured entirely through Hydra

---

## Dual-Environment Architecture for Modern Data Processing

This project uses **Airflow 3.0.6** with **intelligent dependency isolation** to provide both stability and modern capabilities:

### Architecture Overview

- **Airflow Core**: Uses SQLAlchemy 1.4.x for proven stability and compatibility
- **Data Processing**: Isolated containers with SQLAlchemy 2.0+ and modern stack
- **Smart Caching**: Fingerprint-based Docker image caching across repos/branches
- **Flexible Execution**: Choose between in-process or isolated execution per task

### Execution Patterns

```python
# Option 1: Simple tasks in Airflow context (SQLAlchemy 1.4.x)
simple_task = PythonOperator(
    task_id='simple_processing',
    python_callable=simple_function,
    dag=dag
)

# Option 2: Modern data processing in isolated container (SQLAlchemy 2.0+)
modern_task = DockerOperator(
    task_id='modern_data_processing',
    image='{{cookiecutter.repo_slug}}-data-processing',
    command=['python', 'transforms/modern_processing.py'],
    dag=dag
)
```

### Key Advantages

- **Best of Both Worlds**: Stable Airflow + modern data processing
- **No Version Conflicts**: Complete dependency isolation when needed
- **Performance**: Modern SQLAlchemy 2.0+, Polars, async support in data tasks
- **Cross-Repo Caching**: Smart build system minimizes Docker build times
- **Gradual Migration**: Use modern stack where beneficial, keep stability elsewhere

See `dags/example_isolated_data_processing.py` for complete patterns.

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

- **Airflow UI**: http://localhost:8081 (admin/admin)
- **Database**: PostgreSQL on localhost:5432
- **Author**: {{cookiecutter.author_name}}

## Layer-Specific Guidance

Each directory contains detailed CLAUDE.md files with specific guidance for that layer:

- See `dags/CLAUDE.md` for Airflow DAG patterns
- See `dbt/CLAUDE.md` for data modeling guidance
- See `transforms/CLAUDE.md` for SQLModel patterns
- See `scripts/CLAUDE.md` for operational utilities

This distributed guidance approach provides contextual AI assistance exactly where developers need it.