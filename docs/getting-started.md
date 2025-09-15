# Getting Started with Data Engineering Template

This cookiecutter template generates **Astronomer-powered data engineering projects** with **DevContainer environments** for immediate development.

## 🎯 **Quick Start**

### Prerequisites
- **Docker** with Compose V2 (Docker Desktop or Engine)
- **Cookiecutter**: `pipx install cookiecutter`
- **VS Code** (recommended for DevContainer support)

### Generate and Start Project
```bash
# Navigate to your projects directory
cd ~/projects

# Generate from template
cookiecutter https://github.com/Troubladore/data-eng-template

# Navigate to generated project
cd your-project-name-etl/

# Option 1: VS Code DevContainer (recommended)
code .
# Click "Reopen in Container" → Everything starts automatically

# Option 2: Manual Docker Compose
cd .devcontainer
docker compose up -d
```

### Access Services
- **Airflow UI**: http://localhost:8081 (admin/admin)
- **Database**: localhost:5432 (postgres/postgres)

## 🚀 **Template Configuration**

During generation, you'll be prompted for these values. **This table explains each prompt to avoid guessing the author's intent:**

| Prompt | Description | Choices/Format | Choice Definitions | Examples |
|--------|-------------|----------------|-------------------|----------|
| **`customer_slug`** | Project identifier used throughout the codebase | Free text (kebab-case) | Short, descriptive project identifier | `awesome-analytics`, `customer-a`, `fraud-detection` |
| **`project_slug`** | Generated automatically | `{customer_slug}-etl` | Auto-generated from customer_slug | `awesome-analytics-etl` |
| **`project_name`** | Human-readable project title | Generated from slug | Used in documentation and displays | `Awesome Analytics ETL Project` |
| **`author_name`** | Project maintainer/team | Free text | Who to contact for this project | `Data Engineering Team`, `Analytics Squad` |
| **`description`** | Brief project summary | Free text | One-line description for documentation | Default is sensible for most cases |
| **`python_version`** | Python runtime version | `3.12` (default) | Python version for containers and dev | `3.12` recommended for latest features |
| **`airflow_version`** | Airflow version | `3.0.6` (default) | Airflow runtime version | `3.0.6` is current Astronomer stable |
| **`runtime_tag`** | Astronomer runtime tag | `3.0-10` (default) | Astronomer's runtime image tag | Matches Airflow version, use default |
| **`image_repo`** | Container registry path | Format: `registry.domain.com/path/{slug}` | Where to push custom images | `registry.example.com/etl/awesome-analytics` |
| **`postgres_version`** | PostgreSQL version | `16` (default) | Database version for development | `16` is latest stable with JSON features |
| **`deployment_mode`** | Container naming strategy | `production`, `testing` | **production**: Clean names for prod deployment<br/>**testing**: Prefixed names for isolation | Choose `production` for real projects |
| **`env_name`** | Default environment | `dev`, `int`, `qa`, `prod` | **dev**: Development with debug enabled<br/>**int**: Integration testing<br/>**qa**: Quality assurance testing<br/>**prod**: Production deployment | Start with `dev` for development |
| **`company_domain`** | Production domain | Domain format | Your organization's domain for prod | `mycompany.com`, `analytics.corp.com` |
| **`local_domain`** | Development domain | `localhost` (default) | Domain for local development | Keep as `localhost` |
| **`high_label`** | Security classification | Free text | Label for sensitive workloads | `high`, `sensitive`, `restricted` |
| **`executor`** | Airflow executor type | `KubernetesExecutor`, `CeleryExecutor`, `LocalExecutor` | **KubernetesExecutor**: Scalable, isolated task execution<br/>**CeleryExecutor**: Distributed workers<br/>**LocalExecutor**: Single-machine execution | `KubernetesExecutor` for production |
| **`secrets_strategy`** | Secrets management | `azure-key-vault`, `external-secrets-operator`, `env-vars` | **azure-key-vault**: Azure Key Vault integration<br/>**external-secrets-operator**: K8s External Secrets<br/>**env-vars**: Simple environment variables | `azure-key-vault` for enterprise |
| **`enable_kerberos`** | Kerberos authentication | `yes`, `no` | **yes**: Enable Kerberos for secure connections<br/>**no**: Standard authentication only | `yes` if your org uses Kerberos |
| **`db_name`** | Database name | Auto-generated | Generated from customer_slug | `awesome_analytics_etl` |
| **`db_user`** | Database username | `postgres` (default) | Development database user | Keep default for development |
| **`db_password`** | Database password | `postgres` (default) | Development database password | Keep default for development |
| **`license`** | Project license | `Proprietary`, `MIT`, `Apache-2.0` | **Proprietary**: Company/private use only<br/>**MIT**: Open source, permissive<br/>**Apache-2.0**: Open source with patent protection | `Proprietary` for company projects |
| **`year`** | Copyright year | Current year | For license headers | `2025` |

### 💡 **Recommended Choices for Most Projects**
- **`deployment_mode`**: `production` (unless specifically testing template)
- **`executor`**: `KubernetesExecutor` (scalable and modern)
- **`secrets_strategy`**: `azure-key-vault` (enterprise-ready)
- **`enable_kerberos`**: `no` (unless your organization requires it)
- **`license`**: `Proprietary` (for company projects)


## 🔧 **Development Workflow**

### Starting Development
```bash
# DevContainer automatically:
# - Builds custom Airflow image with project dependencies
# - Starts PostgreSQL database
# - Configures environment variables from Hydra configs
# - Sets up VS Code Python environment with .venv

# Access Airflow UI
open http://localhost:8081

# Run example pipeline
python scripts/run_pipeline.py

# Override configuration
python scripts/run_pipeline.py environment=prod database.host=prod-db.example.com
```

### Project Structure

For the complete directory structure of generated projects, see:
**[Generated Project Structure](../{{cookiecutter.customer_slug}}-etl/docs/directory_structure.md)**

## 🪟 **Platform-Specific Notes**

### Windows/WSL2
```bash
# Work in WSL2 filesystem for best performance
cd ~/projects  # NOT /mnt/c/projects

# Ensure Docker Desktop WSL2 integration is enabled
# Settings → Resources → WSL Integration → Enable
```

### macOS/Linux
```bash
# Standard setup works out of the box
# Ensure Docker has sufficient resources allocated
```

## 🐛 **Troubleshooting**

### DevContainer Won't Start
```bash
# Check Docker is running
docker version

# Verify Docker Compose syntax
cd .devcontainer
docker compose config

# Check for port conflicts
docker ps -a
```

### Airflow UI Not Accessible
```bash
# Verify services are running
docker compose ps

# Check Airflow logs
docker compose logs airflow-webserver

# Verify port mapping
# Should see: localhost:8081 → container:8080
```

### Slow Performance
```bash
# Windows: Ensure working in WSL2, not Windows filesystem
pwd  # Should show /home/username/..., not /mnt/c/...

# Check Docker resource allocation
# Docker Desktop → Settings → Resources
# Recommend: 8GB RAM, 60GB disk
```

## 🎉 **Success Validation**

After setup, you should have:
- ✅ **Airflow UI**: Accessible at http://localhost:8081
- ✅ **Database**: PostgreSQL accessible on localhost:5432
- ✅ **Example DAGs**: Visible in Airflow UI
- ✅ **VS Code integration**: Python environment detected

### Quick Test
```bash
# Verify configuration system
python scripts/run_pipeline.py runtime.dry_run=true

# Check database connectivity
python scripts/psql.sh -c "\l"

# Run DAG validation tests
make test
```

## 📚 **Next Steps**

1. **Explore generated documentation**: Start with `docs/index.md` in your project
2. **Review example DAGs**: Check patterns in `dags/` directory
3. **Customize configuration**: Edit `conf/config.yaml` for your needs
4. **Add data sources**: Update database and connection configs
5. **Build your first pipeline**: Use provided templates and patterns

---

**You're ready to build production-ready data engineering projects with Astronomer!** 🚀

For detailed architecture and deployment information, see the [template overview](template-overview.md).