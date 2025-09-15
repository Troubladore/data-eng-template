# Data Engineering Cookiecutter Template

## What Is This?

This template generates data engineering projects built on proven foundations:

- **[Cookiecutter](https://cookiecutter.readthedocs.io/)**: A command-line utility that creates projects from templates, enabling consistent project structure and configuration across teams
- **[Astronomer](https://www.astronomer.io/)**: Enterprise-grade Apache Airflow distributions and operational tooling for production data workflows

## Why Was This Created?

### The Challenge: Inconsistent Development Practices
Teams often struggle with:
- **Inconsistent project setups** across data engineering initiatives
- **Reinventing operational patterns** instead of building on proven foundations
- **Development environment drift** between team members and projects
- **Lost time** recreating the same architectural decisions repeatedly

### The Solution
This template combines Astronomer's operational excellence with team-specific development alignment to eliminate these problems through consistent, production-ready project generation.

## How Do You Use It?

### Step 1: One-Time Organizational Setup

**📚 [Complete the Organizational Setup Guide](docs/organizational-setup-guide.md)**

**Why this step is required:**
- **Sets up optimized caching defaults** (10-second rebuilds vs 10-minute rebuilds)
- **Configures port management** to prevent team conflicts
- **Establishes container registry** and security settings
- **Creates team dependency standards** and workflow documentation
- **Ensures persistence** of customizations across template updates

### Step 2: Per-Project Repository Generation

**📚 [Follow the Per-Project Usage Guide](docs/getting-started.md)**

Having completed the organizational setup, generating each new repository will be streamlined:
- **3 simple prompts**: customer_slug, description, deployment_mode
- **Optimized defaults**: All technical settings pre-configured for your team
- **Fast builds**: Sub-10-second rebuilds with shared Docker layer caching
- **Port coordination**: Automatic conflict-free port assignment
- **Consistent environments**: Same setup across all team members

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

## How to Learn More

**About This Template**: For template architecture, development, and design decisions → **[`docs/`](docs/)**

**About the Deployed Repo**: Generated projects include their own comprehensive documentation. Explore what a **generated project looks like** → **[`{{cookiecutter.customer_slug}}-etl/README.md`]({{cookiecutter.customer_slug}}-etl/README.md)**

## Key Features

### 🚀 **Astronomer Foundation**
- **Airflow 3.0.6** with Astronomer runtime for proven reliability
- **Enterprise security** with Azure Key Vault integration and secrets management patterns
- **Multi-environment support** (dev/staging/prod) with consistent deployment
- **Performance optimizations** from years of production experience

### 🛠️ **Team Development**
- **DevContainer environments** with custom Airflow images for consistent workflows
- **Type-safe configuration** via Hydra + Pydantic replacing fragmented .env files
- **Modern Python tooling** (`uv`, `ruff`, Python 3.12) aligned with team standards
- **Hot-reload development** with 10-second DAG detection for rapid iteration

### 🧹 **Docker Cleanup System**
- **Labeled artifacts** (`de-template.project`, `de-template.deployment`)
- **Shallow cleanup**: Remove test artifacts quickly
- **Deep cleanup**: Complete system cleanup
- **Production/testing isolation** with different naming patterns

### 🧪 **Comprehensive Testing**
- **4-tier test architecture**: Unit → Integration → E2E → Stress
- **Docker cleanup validation**: Ensures no artifact leakage
- **Concurrent operation testing**: Multi-project stress scenarios
- **Airflow 3.0 compatibility**: Zero deprecation warnings

## License

This cookiecutter template is available under the MIT License. Generated projects can choose their own license during generation.