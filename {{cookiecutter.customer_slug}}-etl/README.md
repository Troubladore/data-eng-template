# {{cookiecutter.project_name}}

An **Astronomer-based** data engineering project with Kubernetes Executor, multi-environment configuration, and enterprise-grade development workflow.

**Generated from**: [Data Engineering Template](https://github.com/Troubladore/data-eng-template)  
**Author**: {{cookiecutter.author_name}}

## 🚀 Quick Start

Follow the Astronomer development workflow:

```bash
# Copy environment configuration
cp .env.example .env

# Initialize and start services
make init

# Check running services and URLs
./tools/where.sh
```

**Access Points**:
- **Airflow UI**: Accessible via hostname-based routing (see `./tools/where.sh`)
- **Database**: PostgreSQL with environment-specific configuration

**Key Features**:
- **{{cookiecutter.executor}}**: Production-ready executor
- **{{cookiecutter.secrets_strategy}}**: Enterprise secret management
- **Multi-Environment**: Consistent dev/staging/prod deployment

## 📚 Documentation

- **🏠 Start here**: [`docs/index.md`](docs/index.md) - Complete documentation homepage
- **🚀 Getting started**: [`docs/getting-started.md`](docs/getting-started.md) - Setup and first steps
- **📁 Project structure**: [`docs/directory_structure.md`](docs/directory_structure.md) - What's where
- **⚙️ Configuration**: [`docs/configuration/README.md`](docs/configuration/README.md) - Hydra config system
- **🔧 Pipelines**: [`docs/pipelines/README.md`](docs/pipelines/README.md) - Data processing architecture  
- **🚀 Operations**: [`docs/operations/README.md`](docs/operations/README.md) - Running and deploying
- **❓ FAQ**: [`docs/faq.md`](docs/faq.md) - Common questions and solutions

## ⚡ Key Features

### 🏗️ Modern Architecture
- **Medallion data layers** (Bronze → Silver → Gold)
- **Hydra configuration** with type-safe Pydantic models
- **DevContainer development** with one-command setup
- **Apache Airflow** orchestration with best practices

### 🛠️ Developer Experience  
- **Type-safe configuration** - Full IDE support with validation
- **Distributed AI guidance** - `CLAUDE.md` files provide contextual help
- **Test-driven development** - Comprehensive test suite included
- **Zero-config startup** - Open in DevContainer and start coding

### 🔧 Configuration System

Uses **Hydra** for unified configuration management:

```bash
# Development (default)
python scripts/run_pipeline.py

# Production with overrides  
python scripts/run_pipeline.py environment=prod database.host=prod-db.com

# Debug mode
python scripts/run_pipeline.py runtime.debug_mode=true runtime.dry_run=true
```

## 📊 Data Pipeline

```mermaid
flowchart LR
    sources[(Data Sources)] -->|ingest| bronze[(Bronze Layer)]
    bronze -->|clean & validate| silver[(Silver Layer)]
    silver -->|business logic| gold[(Gold Layer)]
    gold -->|serve| endpoints[APIs / BI / ML]
    
    subgraph "Orchestration"
        airflow[Airflow] --> tasks[Pipeline Tasks]
    end
    
    subgraph "Configuration"  
        hydra[Hydra] --> configs[Environment Configs]
    end
    
    configs --> airflow
    tasks --> bronze
    tasks --> silver  
    tasks --> gold
```

## 🏃‍♂️ Common Tasks

```bash
# Run pipeline with dry-run
python scripts/run_pipeline.py runtime.dry_run=true

# dbt development
cd dbt && dbt run --target dev && dbt test

# Database access
./scripts/psql.sh

# Run tests
make test

# Generate documentation
cd dbt && dbt docs generate && dbt docs serve

# Reset development environment
./scripts/setup-development.sh
```

## 🗑️ Complete Environment Reset

For testing or when you need to completely reset the development environment:

```bash
# Stop all services
astro dev stop
# OR
docker compose down -v

# Clean up containers and volumes
docker system prune -v

# Fresh setup
./scripts/setup-development.sh
```

This process ensures a completely clean environment for reliable testing and development.

## 🗂️ Project Structure

```
├── conf/                    # Hydra configuration system
├── dags/                    # Airflow DAG definitions  
├── dbt/                     # Data transformations (medallion architecture)
├── scripts/                 # Operational utilities
├── transforms/              # SQLModel/Pydantic data models
├── tests/                   # Test suite
├── docs/                    # This documentation
└── .devcontainer/           # VS Code DevContainer setup
```

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## 📜 License

See [LICENSE](LICENSE) for licensing information.

---

**Need help?** Check the [FAQ](docs/faq.md) or [full documentation](docs/index.md).