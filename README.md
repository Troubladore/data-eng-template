# Data Engineering Cookiecutter Template

**Astronomer-powered cookiecutter template** that generates production-ready data engineering projects built on **Astronomer's proven foundation** with **team-customized development workflows**, **DevContainer environments**, and **repeatable project architecture**.

## What Is This?

This is a **cookiecutter template** that generates data engineering projects built on **Astronomer's battle-tested foundation**:

### 🚀 **Astronomer Core Benefits** (Built-in)
- **Airflow 3.0.6** with Astronomer runtime for **proven reliability**
- **Operational excellence** with enterprise-grade monitoring and scaling
- **Production-ready configurations** based on Astronomer best practices
- **Performance optimizations** from years of Airflow operational experience

### 🛠️ **Team Development Customizations**
- **DevContainer environments** for consistent team development workflows
- **Type-safe configuration** via Hydra + Pydantic for team-specific needs
- **Modern Python tooling** (`uv`, `ruff`, Python 3.12) aligned with team standards
- **Docker cleanup systems** to prevent development environment drift
- **Comprehensive testing frameworks** ensuring code quality across projects

## Why Was This Created?

### The Challenge: Inconsistent Development Practices
Teams often struggle with:
- **Inconsistent project setups** across data engineering initiatives
- **Reinventing operational patterns** instead of building on proven foundations
- **Development environment drift** between team members and projects
- **Lost time** recreating the same architectural decisions repeatedly

### The Astronomer Foundation + Team Alignment Solution
This template leverages **Astronomer's operational excellence** while adding **team-specific development alignment**:

**🏗️ Built on Astronomer's Proven Foundation**
- **Reliability**: Astronomer's enterprise-grade Airflow distribution
- **Operational ease**: Pre-configured monitoring, scaling, and deployment patterns
- **Flexibility**: Extensible architecture supporting diverse data workflows
- **Performance**: Optimized configurations from years of production experience

**👥 Customized for Team Development Alignment**
- **Repeatable project architecture** ensures consistent practices across initiatives
- **Standardized tooling** (`uv`, `ruff`, Hydra) aligns team development workflows
- **DevContainer environments** eliminate "works on my machine" issues
- **Comprehensive testing patterns** maintain code quality standards across projects

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

### Why Astronomer + Airflow 3.0?
- **Astronomer's operational expertise**: Years of production Airflow experience baked in
- **Enterprise-grade reliability**: Battle-tested configurations and monitoring patterns
- **Proven scalability**: Handles everything from small teams to enterprise-scale deployments
- **Community + commercial support**: Open-source foundation with commercial backing
- **Latest Airflow 3.0 features**: Performance improvements and enhanced security
- **Container-native design**: Perfect alignment with modern DevContainer development

## Team Development Alignment

This template ensures **consistent development practices** across your data engineering projects:

### 🎯 **Standardized Project Structure**
Every generated project follows the same **Astronomer-based architecture**, making it easy for team members to:
- **Navigate any project** with familiar structure and tooling
- **Onboard quickly** to new initiatives using known patterns
- **Share knowledge** and best practices across projects
- **Maintain consistency** in operational and development approaches

### 🔄 **Repeatable Excellence**
- **Start every project** with Astronomer's proven operational foundation
- **Apply team conventions** automatically (testing, tooling, configuration)
- **Avoid architectural debt** by building on established patterns
- **Scale team practices** as you add more data engineering initiatives

### 📈 **Continuous Improvement**
- **Evolve the template** to incorporate new team learnings and Astronomer updates
- **Propagate improvements** to future projects through template updates
- **Maintain alignment** between development and production environments

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