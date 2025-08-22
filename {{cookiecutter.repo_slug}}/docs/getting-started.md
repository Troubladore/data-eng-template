# Getting Started

This guide will get you up and running with the {{cookiecutter.project_name}} data engineering project.

## Prerequisites

- **Docker** and **Docker Compose** installed
- **VS Code** with the DevContainers extension
- **Git** configured with your credentials

## Quick Start (Recommended)

### 1. Open in DevContainer

The fastest way to start is using VS Code DevContainers:

```bash
# Clone the repo
git clone <your-repo-url>
cd {{cookiecutter.repo_slug}}

# Open in VS Code
code .

# When prompted, click "Reopen in Container"
# Or use Command Palette: "Dev Containers: Reopen in Container"
```

The DevContainer will automatically:
- Set up Python {{cookiecutter.python_version}} environment
- Install all dependencies with `uv`
- Start PostgreSQL and Airflow services
- Generate environment variables from Hydra configuration
- Run post-startup health checks

### 2. Verify Setup

Once the container is running, verify everything works:

```bash
# Check configuration system
python scripts/run_pipeline.py runtime.dry_run=true

# Test database connection
make psql

# Check Airflow UI (opens in browser)
make airflow-ui
# Or manually: http://localhost:8080 (admin/admin)

# Run tests
make test
```

## Manual Setup (Alternative)

If you prefer not to use DevContainers:

### 1. Install Dependencies

```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python dependencies
uv sync

# Generate environment variables
./scripts/export_env.sh > .env
```

### 2. Start Services

```bash
# Start PostgreSQL and Airflow
docker-compose -f .devcontainer/compose.yaml up -d

# Initialize Airflow database
docker-compose -f .devcontainer/compose.yaml exec airflow-webserver airflow db upgrade
```

### 3. Verify Setup

```bash
# Activate Python environment
source .venv/bin/activate

# Test configuration
python scripts/run_pipeline.py runtime.dry_run=true

# Check services
curl http://localhost:8080/health  # Airflow
psql postgresql://postgres:postgres@localhost:5432/postgres -c "SELECT 1;"
```

## Configuration Overview

This project uses **Hydra** for configuration management. Key concepts:

### Environment-Based Configuration

```bash
# Development (default)
python scripts/run_pipeline.py

# Production
python scripts/run_pipeline.py environment=prod

# Staging with overrides
python scripts/run_pipeline.py environment=staging database.host=staging-db.com
```

### Configuration Files

- `conf/config.yaml` - Main configuration with defaults
- `conf/environment/` - Environment-specific settings (dev/staging/prod)
- `conf/local/generated.yaml` - Generated secrets and keys (gitignored)

### Type-Safe Settings

All configuration is validated with Pydantic:

```python
from your_project.config import get_settings

settings = get_settings()
print(settings.database.connection_url)  # Full IDE support
```

## Development Workflow

### 1. Pipeline Development

```bash
# Run pipeline with different configurations
python scripts/run_pipeline.py runtime.dry_run=true
python scripts/run_pipeline.py runtime.parallel_jobs=2

# Test specific components
make test-dags
make test-config
```

### 2. Data Model Development

```bash
# dbt development
cd dbt
dbt run --target dev
dbt test
dbt docs generate && dbt docs serve

# Transform model development
python -c "from transforms.models import YourModel; print(YourModel.schema())"
```

### 3. Airflow Development

```bash
# Test DAG parsing
python -c "from dags.your_dag import dag; print(dag.task_dict)"

# Airflow CLI shortcuts
./scripts/airflow-cli.sh dags list
./scripts/airflow-cli.sh tasks test your_dag your_task 2025-01-01
```

## Project Structure

```
├── conf/                    # Hydra configuration
├── dags/                    # Airflow DAGs
├── dbt/                     # Data transformations
├── scripts/                 # Operational utilities
├── transforms/              # Data models
├── tests/                   # Test suite
└── docs/                    # This documentation
```

For detailed structure explanation, see [Directory Structure](directory_structure.md).

## Next Steps

1. **Explore the configuration** - See [`configuration/`](configuration/) docs
2. **Understand data flow** - Read [`pipelines/`](pipelines/) documentation  
3. **Learn operations** - Check [`operations/`](operations/) guides
4. **Review architecture decisions** - Browse [`adr/`](adr/) records

## Troubleshooting

### Common Issues

**DevContainer won't start**: Check Docker is running and you have enough memory (recommend 8GB+)

**Port conflicts**: Modify ports in `.devcontainer/compose.yaml` if 8080 or 5432 are in use

**Permission errors**: On Linux, ensure your user ID matches the container user

**Dependency issues**: Delete `.venv` and run `uv sync` to refresh dependencies

### Getting Help

- Check the [FAQ](faq.md) for common questions
- Review [operations guide](operations/README.md)
- Check [GitHub issues](https://github.com/your-org/{{cookiecutter.repo_slug}}/issues) for known problems

## Configuration Deep Dive

For more details on the Hydra configuration system, see:

- [Configuration Overview](configuration/README.md)
- [Hydra Configuration Guide](configuration/README.md)
- [Environment Configuration](configuration/README.md)