# Data Engineering Template

Reproducible data engineering template with:
- Podman Compose: Airflow + Postgres
- VS Code Dev Container (auto start/stop with `shutdownAction: stopCompose`)
- `uv` for Python package & project management
- `ruff` for linting/formatting (replaces black/isort)
- `sqlmodel` for Bronze tables (Pydantic + SQLAlchemy)
- `dbt-core` for Silver/Gold modeling

## Prereqs
- Podman **with Docker API socket** enabled (or Docker), macOS/Linux/WSL2.
- VS Code + Dev Containers extension.
- Cookiecutter: `pipx install cookiecutter`
- (Optional) `pyenv` on host; `.python-version` is respected.

## First run

**⚠️ This is a cookiecutter template - do not use directly!**

1. **Generate project from template** (run from your projects directory):
   ```bash
   # Navigate to where you want the new project created
   cd ~/projects  # or wherever you keep projects
   
   # Generate from remote template
   cookiecutter https://github.com/Troubladore/data-eng-template
   # Or if you have it locally:
   cookiecutter .
   ```
   
   You'll be prompted to enter:
   - `project_name`: "My Awesome Data Project" 
   - `repo_slug`: "my-awesome-data-project" (auto-generated from project name)
   - `python_version`: "3.12" (default)
   - `airflow_version`: "2.9.3" (default)
   - `airflow_executor`: Choose execution model
     - **LocalExecutor** (default): Runs tasks in parallel using separate processes
     - **SequentialExecutor**: Runs tasks one at a time (for testing/lightweight setups)
   - `license`: Choose project license
     - **Proprietary** (default): All rights reserved, no license granted
     - **MIT**: Permissive open source license
     - **Apache-2.0**: Permissive with patent protection

2. **Navigate to generated project**:
   ```bash
   cd my-awesome-data-project/  # whatever you named it
   ```

3. **Start DevContainer**:
   - **VS Code**: Open project → **Reopen in Container** (services auto-start)
   - **CLI**: `devcontainer up --workspace-folder .`

4. **Access services**:
   - **Airflow**: http://localhost:8080 (admin/admin)
   - **Postgres**: `make psql`

> Airflow image installs lightweight extras on boot via `_PIP_ADDITIONAL_REQUIREMENTS` for dev only.
> For heavier deps, build a custom image later.

## 🚀 Deployment Features

This template includes **Astronomer-inspired deployment optimizations**:

### ⚡ Fast DAG-Only Deployments
- **5-15 second deployments** vs 5+ minute full rebuilds
- Perfect for iterative DAG development
- Automatic change detection with SHA256 hashing

```bash
make deploy-dags    # Deploy only DAG files (fastest)
make deploy         # Auto-detect changes and choose optimal strategy
make deploy-full    # Full rebuild (dependencies + code)
```

### 🐳 Docker Layer Caching
- **Multi-stage builds** with dependency separation
- **60-80% faster rebuilds** with intelligent caching
- Persistent pip/uv caches in development

### 🔍 Intelligent Change Detection
- Automatically detects what changed (DAGs, dependencies, code)
- Chooses optimal deployment strategy
- Performance monitoring with timing metrics

### 📊 Performance Optimizations
- Volume mount caching for local development
- Hot-reload configuration (10-second DAG scanning)
- GitHub Actions CI/CD with registry caching

**See full deployment guide**: [`docs/deployment/README.md`]({{cookiecutter.repo_slug}}/docs/deployment/README.md)

## Layout
See repository tree in this README's template generation.