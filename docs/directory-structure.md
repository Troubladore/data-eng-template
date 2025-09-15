# Template Directory Structure

## Cookiecutter Template Structure

```
data-eng-template/
├── cookiecutter.json              # Template variables and defaults
├── hooks/
│   └── post_gen_project.py        # Post-generation setup (Fernet keys, .env)
├── docs/                           # Template documentation (this folder)
├── tests/                          # Template testing framework
│   ├── unit/                       # Unit tests for template generation
│   ├── integration/                # Integration tests for DevContainer setup
│   ├── e2e/                        # End-to-end workflow tests
│   └── stress/                     # Concurrent operation stress tests
├── {{cookiecutter.customer_slug}}-etl/     # Generated project template
└── README.md                       # Template overview and usage
```

## Generated Project Structure

When you run `cookiecutter`, this template generates projects with the following structure:

```
your-project-etl/
├── dags/                           # Airflow DAGs
│   ├── example_dag.py             # Example DAG implementations
│   ├── example_modern_airflow.py  # Modern Airflow patterns
│   └── CLAUDE.md                  # Airflow development guidance
├── dbt/                           # dbt transformations
│   ├── models/                    # dbt models organized by layer
│   │   ├── bronze/                # Raw data ingestion layer
│   │   ├── silver/                # Cleaned and standardized data
│   │   └── gold/                  # Business logic and aggregations
│   ├── dbt_project.yml           # dbt project configuration
│   └── CLAUDE.md                 # dbt development guidance
├── .devcontainer/                 # DevContainer configuration
│   ├── compose.yaml              # Docker Compose services setup
│   ├── devcontainer.json         # VS Code DevContainer configuration
│   └── README.md                 # DevContainer setup instructions
├── conf/                          # Hydra configuration system
│   ├── config.yaml               # Main configuration file
│   ├── environment/              # Environment-specific configs (dev/prod)
│   ├── orchestration/            # Airflow configuration templates
│   ├── database/                 # Database connection configs
│   └── deployment/               # Deployment-specific settings
├── docs/                          # Project documentation
│   ├── getting-started.md        # Project setup and usage guide
│   ├── configuration/            # Configuration system documentation
│   └── deployment/               # Deployment procedures and runbooks
├── tests/                         # Comprehensive test suite
│   ├── test_dag_loads.py         # DAG loading and validation tests
│   └── test_config.py            # Configuration validation tests
├── scripts/                       # Utility scripts
│   ├── run_pipeline.py           # Hydra-integrated pipeline runner
│   └── airflow-cli.sh            # Airflow CLI convenience wrapper
├── transforms/                    # SQLModel data transformations
│   ├── models.py                 # Pydantic data models
│   └── CLAUDE.md                 # SQLModel development guidance
├── Dockerfile.airflow            # Custom Airflow image definition
├── pyproject.toml                # Python project configuration (uv/ruff)
├── README.md                     # Generated project overview
└── CLAUDE.md                     # Project-specific development guidance
```

## Key Template Features

- **Cookiecutter Variables**: Defined in `cookiecutter.json` with sensible defaults
- **Post-Generation Hooks**: Automatic setup of secrets, fingerprinting, and .env files
- **DevContainer Ready**: Complete VS Code integration with Docker Compose
- **Comprehensive Testing**: 4-tier test architecture validates template functionality
- **Documentation Hierarchy**: Both template docs and generated project docs included