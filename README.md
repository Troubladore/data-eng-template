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
- **DevContainer environments** with custom Airflow images for consistent team workflows
- **Type-safe configuration** via Hydra + Pydantic replacing fragmented .env files
- **Modern Python tooling** (`uv`, `ruff`, Python 3.12) aligned with team standards
- **Hot-reload development** with 10-second DAG detection for rapid iteration
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
- **Enterprise security**: Azure Key Vault integration and secrets management patterns
- **Flexibility**: Multi-environment support (dev/staging/prod) with consistent deployment
- **Performance**: Optimized configurations from years of production experience

**👥 Customized for Team Development Alignment**
- **Repeatable project architecture** ensures consistent practices across initiatives
- **Standardized tooling** (`uv`, `ruff`, Hydra) aligns team development workflows
- **DevContainer environments** eliminate "works on my machine" issues
- **Comprehensive testing patterns** maintain code quality standards across projects

## How Do You Use It?

**⚠️ This template requires proper organizational setup for optimal team results.**

### Step 1: Organizational Setup (Required First)

**📚 [Complete the Organizational Setup Guide](docs/organizational-setup-guide.md)**

This mandatory first step:
- **Sets up optimized caching defaults** (10-second rebuilds vs 10-minute rebuilds)
- **Configures port management** to prevent team conflicts
- **Establishes container registry** and security settings
- **Creates team dependency standards** and workflow documentation
- **Ensures persistence** of customizations across template updates

**Why this step is required**: Skipping organizational setup leads to slow builds, port conflicts, configuration drift, and inconsistent team environments that waste hours of development time.

### Step 2: Project Generation

**After completing organizational setup**:

**📚 [Follow the Getting Started Guide](docs/getting-started.md)**

You'll have a streamlined experience:
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

**About This Template**: For template architecture, development, and design decisions → **[`docs/`](docs/)**

**About the Deployed Repo**: Generated projects include their own comprehensive documentation. Explore what a **generated project looks like** → **[`{{cookiecutter.customer_slug}}-etl/README.md`]({{cookiecutter.customer_slug}}-etl/README.md)**

## License

This cookiecutter template is available under the MIT License. Generated projects can choose their own license during generation.