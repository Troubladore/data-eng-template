# Data Engineering Template

Modern cookiecutter template for data engineering projects with:
- **Docker Compose**: Airflow 3.0.6 + Postgres 16 + Custom Images
- **VS Code DevContainer**: One-click development environment
- **Performance Optimization**: 149x faster builds via external caching system
- **Modern Python Stack**: `uv` + `ruff` + Python 3.12
- **Type-Safe Configuration**: Hydra + Pydantic for unified config management  
- **Data Modeling**: `dbt-core` + `sqlmodel` with medallion architecture

## Prerequisites

### Required
- **Docker** or **Podman** with Docker API socket enabled (macOS/Linux/WSL2)
- **DevContainer CLI**: `npm install -g @devcontainers/cli` (or VS Code + Dev Containers extension)
- **Cookiecutter**: `pipx install cookiecutter`

### For Optimal Performance
- **Enhanced Development Tools** (optional but recommended):
  ```bash
  pipx install devcontainer-service-manager[workstation]
  ```
  Provides 149x faster builds, WSL2 optimizations, and cross-repository caching

### Optional
- **pyenv** on host (`.python-version` files are respected)
- **WSL2** for Windows development (see performance optimizations below)

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
   - `airflow_version`: "3.0.6" (default)
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
   - **CLI** (recommended): `devcontainer up --workspace-folder .`
   - **VS Code**: Open project → **Reopen in Container** (services auto-start)

4. **Access services**:
   - **Airflow**: http://localhost:8081 (admin/admin)
   - **Postgres**: localhost:5432 (postgres/postgres)

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

## 🚀 Performance Optimization

### Automatic Performance Benefits
Generated projects include an optimized setup script that provides:

- **149x faster Docker builds**: Fingerprint-based caching across projects and branches  
- **Cross-repository cache sharing**: Reuse builds between different projects
- **WSL2 optimization**: Specialized performance tuning for Windows development
- **Automatic resource cleanup**: Prevents Docker resource accumulation

### Usage in Generated Projects
```bash
# In your generated project directory
./scripts/setup-development.sh
```

This automatically installs and configures [`devcontainer-service-manager`](https://github.com/Troubladore/devcontainer-service-manager) with workstation optimization features.

### Manual Installation
```bash
# Install enhanced development tools (globally available)
pipx install devcontainer-service-manager[workstation]

# One-time workstation optimization
dcm-setup install --profile data-engineering

# Validate setup
dcm-setup validate
```

## 🪟 **Windows/WSL2 Users**

For optimal performance on Windows:

### Setup Steps
```bash
# 1. Ensure you're in WSL2 filesystem (not /mnt/c/)
cd ~  # Or mkdir -p ~/repos && cd ~/repos

# 2. Clone template to WSL2 filesystem  
git clone https://github.com/Troubladore/data-eng-template.git

# 3. Install prerequisites in WSL2
pipx install cookiecutter
pipx install devcontainer-service-manager[workstation]

# 4. One-time workstation optimization
dcm-setup install --profile data-engineering
```

### Performance Tips
- **File Location**: Keep repositories in WSL2 filesystem (`~/repos/`) for 10x faster I/O
- **Docker Desktop**: Enable WSL2 integration in Docker Desktop settings  
- **Resource Allocation**: Allocate 8GB+ memory to Docker Desktop for optimal performance

### Troubleshooting
```bash
# Validate WSL2 setup
dcm-setup validate

# Fix common issues automatically
dcm-setup troubleshoot

# Check if you're in the right filesystem
pwd  # Should show /home/username/... not /mnt/c/...
```

## 📁 Template Structure