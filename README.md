# Data Engineering Cookiecutter Template

**Modern cookiecutter template** for generating **Astronomer-based** data engineering projects with **DevContainer development environments**, **Docker cleanup systems**, and **comprehensive testing frameworks**.

## What Is This?

This is a **cookiecutter template** - not a working project itself. It generates fully-configured data engineering projects with:

- **Airflow 3.0.6** with Astronomer runtime in DevContainers
- **Docker Compose** development environment with custom images
- **Postgres 16** database with persistent volumes
- **Type-safe configuration** via Hydra + Pydantic
- **Modern Python tooling** (`uv`, `ruff`, Python 3.12)
- **Comprehensive test suites** (unit/integration/e2e/stress tests)
- **Docker cleanup system** with labeled artifact management

## Why Was This Created?

**Problem Solved**: Creating production-ready data engineering projects with proper development environments, testing frameworks, and operational tooling requires significant setup time and architectural decisions.

**Solution**: This template provides a battle-tested architecture that:
- **Eliminates boilerplate setup** for Airflow + DevContainer environments
- **Prevents Docker artifact accumulation** with automated cleanup systems
- **Ensures code quality** with comprehensive testing and modern tooling
- **Supports multiple deployment modes** (production/testing) with proper isolation

## How Do You Use It?

### Prerequisites
- **Docker** with Compose V2 (Docker Desktop or Engine)
- **Cookiecutter**: `pipx install cookiecutter`
- **VS Code** (recommended for DevContainer support)

### Generate a New Project

```bash
# Navigate to your projects directory
cd ~/projects

# Generate from remote template (recommended)
cookiecutter https://github.com/Troubladore/data-eng-template

# Or from local clone
git clone https://github.com/Troubladore/data-eng-template.git
cookiecutter data-eng-template/
```

**You'll be prompted for**:
- `customer_slug`: Project identifier (e.g., "awesome-analytics")
- `deployment_mode`: "production" or "testing" (affects container naming)
- `python_version`: "3.12" (recommended)
- `airflow_version`: "3.0.6" (current stable)
- Additional configuration options with sensible defaults

### Start Development

```bash
# Navigate to generated project
cd your-project-name-etl/

# Option 1: VS Code DevContainer (recommended)
code .
# Click "Reopen in Container" → Everything starts automatically

# Option 2: Manual Docker Compose
cd .devcontainer
docker compose up -d

# Access services
# Airflow UI: http://localhost:8081 (admin/admin)
# Database: localhost:5432 (postgres/postgres)
```

## Project Architecture

Generated projects follow this architecture:

```
your-project-etl/
├── dags/                    # Airflow DAGs
├── dbt/                     # dbt transformations
├── .devcontainer/           # DevContainer + Docker Compose
├── conf/                    # Hydra configuration (replaces .env)
├── docs/                    # Project documentation
├── tests/                   # Comprehensive test suite
└── CLAUDE.md               # Generated project guidance
```

## Key Features

### 🐳 **DevContainer Development**
- **One-click setup** via VS Code DevContainer extension
- **Custom Airflow images** with project dependencies
- **Service orchestration** with Docker Compose
- **Port forwarding** and volume mounts configured

### 🧹 **Docker Cleanup System**
- **Labeled artifacts** (`de-template.project`, `de-template.deployment`)
- **Shallow cleanup**: Remove test artifacts quickly
- **Deep cleanup**: Complete system cleanup
- **Production/testing isolation** with different naming patterns

### 🔧 **Type-Safe Configuration**
- **Hydra framework** replaces fragmented `.env` files
- **Pydantic validation** with IDE support
- **Environment-specific configs** (dev/staging/prod)
- **Command-line overrides** without editing files

### 🧪 **Comprehensive Testing**
- **4-tier test architecture**: Unit → Integration → E2E → Stress
- **Docker cleanup validation**: Ensures no artifact leakage
- **Concurrent operation testing**: Multi-project stress scenarios
- **Airflow 3.0 compatibility**: Zero deprecation warnings

## How to Learn More

After generating your project, refer to the generated documentation:

### Generated Project Documentation
- **`CLAUDE.md`**: Project-specific development guidance
- **`docs/getting-started.md`**: Comprehensive setup and usage guide
- **`docs/configuration/README.md`**: Hydra configuration system details
- **`docs/deployment/README.md`**: Production deployment strategies
- **`dags/CLAUDE.md`**: Airflow DAG development patterns
- **`dbt/CLAUDE.md`**: dbt transformation guidelines

### Template Development
- **`CLAUDE.md`**: This template's development guidance
- **`tests/README.md`**: Test suite architecture and execution
- **Issue Tracker**: https://github.com/Troubladore/data-eng-template/issues

## Template Development & Testing

### Test the Template
```bash
# Clone template repository
git clone https://github.com/Troubladore/data-eng-template.git
cd data-eng-template

# Setup test environment
uv sync
source .venv/bin/activate

# Run comprehensive test suite
make test                    # All tests
pytest -m unit             # Unit tests only
pytest -m integration      # Integration tests
pytest -m e2e              # End-to-end workflow tests
pytest -m stress           # Concurrent operation stress tests
```

### Cleanup Test Artifacts
```bash
# Remove generated test projects and Docker artifacts
bash tests/utils/cleanup-shallow.sh

# Deep cleanup (removes all template-related Docker artifacts)
bash tests/utils/cleanup-deep.sh
```

## Architecture Decisions

### Why DevContainers?
- **Consistent development environments** across team members
- **Zero host dependency conflicts** - everything runs in containers
- **VS Code integration** provides seamless debugging and development
- **Docker Compose orchestration** handles service dependencies

### Why Cookiecutter?
- **Proven template engine** with wide adoption
- **Interactive prompting** for configuration values
- **Jinja2 templating** allows conditional file generation
- **Post-generation hooks** enable dynamic setup (Fernet keys, fingerprinting)

### Why Airflow 3.0?
- **Latest stable release** with performance improvements
- **Simplified configuration** (eliminated deprecation warnings)
- **Enhanced security** and operational features
- **Container-native architecture** aligns with DevContainer approach

## Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes and test**: `make test`
4. **Commit changes**: `git commit -m 'Add amazing feature'`
5. **Push to branch**: `git push origin feature/amazing-feature`
6. **Create Pull Request**

**Testing Requirements**: All changes must pass the 4-tier test suite (unit/integration/e2e/stress) before merge.

## License

This cookiecutter template is available under the MIT License. Generated projects can choose their own license during generation.

---

**Generated projects include their own comprehensive documentation**. This README focuses on the template itself - refer to your generated project's `CLAUDE.md` and `docs/` directory for project-specific guidance.