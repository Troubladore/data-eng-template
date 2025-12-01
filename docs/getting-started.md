# Getting Started with Data Engineering Template

This cookiecutter template generates **Astronomer-powered data engineering projects** with **DevContainer environments** for immediate development.

## 🎯 **Quick Start**

### Prerequisites

#### ✅ **Required Tools**
- **Docker** with Compose V2 (Docker Desktop or Engine)
- **Cookiecutter**: `pipx install cookiecutter`
- **VS Code** (recommended for DevContainer support)

#### 🏢 **First-Time Organizational Setup (Critical)**

**⚠️ STOP: Complete this setup BEFORE generating your first project!**

**📚 [Complete the Organizational Setup Guide](organizational-setup-guide.md)** to:
- **Configure caching-optimized defaults** for your team
- **Set up container registry** and security settings
- **Establish persistence strategy** for your customizations
- **Create team dependency standards**
- **Test and validate** your configuration

**Why this matters**: Skipping this setup leads to slow builds (10+ minutes instead of 10 seconds), inconsistent team environments, and configuration drift that wastes hours of development time.

#### ✅ **After Organizational Setup**

### Generate and Start Project

With organizational setup complete, project generation is streamlined:

```bash
# Navigate to your projects directory
cd ~/projects

# Generate using your organization's optimized defaults
cookiecutter https://github.com/your-org/data-eng-template --config-file your-org-defaults.yaml

# You'll only be prompted for 3 values:
# - customer_slug: your-project-identifier
# - description: Brief project description
# - deployment_mode: production (or testing)

# Navigate to generated project
cd your-project-identifier-etl/

# Option 1: VS Code DevContainer (recommended)
code .
# Click "Reopen in Container" → Everything starts automatically with optimized caching

# Option 2: Manual Docker Compose
cd .devcontainer
docker compose up -d
```

### Discover Service Ports

**Dynamic Port Allocation**: This template supports parallel development by using dynamic port allocation. Each project gets unique ports automatically.

```bash
# Discover your project's actual ports
./scripts/get-ports.sh

# Output example:
# 🌐 Airflow UI: http://localhost:32768
# 🗄️ PostgreSQL: localhost:32769
```

**Credentials**:
- **Airflow**: admin/admin
- **Database**: admin/admin

### 🔄 **Parallel Development Support**

**Multiple Projects**: You can run multiple Astronomer projects simultaneously without port conflicts:

```bash
# Terminal 1: Project A
cd project-a-etl/
./scripts/get-ports.sh
# 🌐 Airflow UI: http://localhost:32768

# Terminal 2: Project B
cd project-b-etl/
./scripts/get-ports.sh
# 🌐 Airflow UI: http://localhost:32770

# Both projects run independently with unique ports
```

**Use Cases**:
- Develop in one project while monitoring long-running DAGs in another
- Compare implementations between projects
- Test integration between multiple data pipelines
- Team members working on different projects simultaneously

## 🚀 **Template Configuration**

### ⚡ **Streamlined Experience: Only 3 Required Prompts**

You'll only be prompted for these **3 essential values**:

| Prompt | Description | Examples |
|--------|-------------|----------|
| **`customer_slug`** | Project identifier (kebab-case) | `awesome-analytics`, `fraud-detection`, `customer-a` |
| **`description`** | Brief project summary | `Customer analytics data pipeline`, `Fraud detection system` |
| **`deployment_mode`** | Container naming strategy | **`production`** (clean names) or **`testing`** (prefixed for isolation) |

**All other settings use sensible defaults** and can be customized later if needed.

### ⚡ **Critical: Configuration Choices Impact Caching!**

**Your configuration choices directly affect Docker build performance!** Poor choices can mean 10-minute rebuilds instead of 10-second rebuilds for your entire team.

**📚 [Read the complete Template Configuration Guide](template-configuration.md)** to understand:
- **Cache-impacting settings** that affect build performance across your team
- **Docker layer caching strategy** and how template choices influence it
- **pyproject.toml considerations** for dependency caching
- **Organizational best practices** for consistent, fast builds

### 🏢 **Company Defaults Configuration**

For organizations wanting to customize defaults:

```bash
# Copy and customize the defaults file
cp company-template-defaults.yaml your-company-defaults.yaml

# Edit your-company-defaults.yaml with your organization's settings:
# - Container registry URLs
# - Security settings (executor, secrets strategy)
# - Author names and domains
# - License preferences

# Generate projects with your company defaults
cookiecutter . --config-file your-company-defaults.yaml
```

### 🔧 **Advanced: All Available Options**

If you need to customize any defaults, here are all available options:

<details>
<summary><strong>Click to expand full configuration options</strong></summary>

| Option | Default | Choices | Description |
|--------|---------|---------|-------------|
| `airflow_version` | `3.0.6` | Version string | Airflow version |
| `author_name` | `Data Engineering Team` | Free text | Project maintainer |
| `company_domain` | `myco.com` | Domain | Production domain |
| `enable_kerberos` | `no` | `no`, `yes` | Enable Kerberos auth |
| `env_name` | `dev` | `dev`, `int`, `qa`, `prod` | Default environment |
| `executor` | `KubernetesExecutor` | `KubernetesExecutor`, `CeleryExecutor`, `LocalExecutor` | Airflow executor |
| `high_label` | `high` | Free text | Security classification |
| `image_repo` | `registry.example.com/etl/{slug}` | Registry URL | Container registry |
| `license` | `Proprietary` | `Proprietary`, `MIT`, `Apache-2.0` | Project license |
| `python_version` | `3.12` | Version string | Python version |
| `secrets_strategy` | `azure-key-vault` | `azure-key-vault`, `external-secrets-operator`, `env-vars` | Secrets management |

</details>


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