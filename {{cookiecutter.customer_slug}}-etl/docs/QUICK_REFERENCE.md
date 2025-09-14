# {{cookiecutter.project_name}} - Quick Reference

## 🚀 **Get Started Fast**

### VS Code DevContainer (Recommended)
```bash
# One-click development environment
code .
# Click "Reopen in Container" → Automatic setup!
```
**Benefits**: Zero configuration, automatic service startup, port forwarding, all tooling ready

### Astronomer CLI (Production-like)
```bash
# Copy environment configuration
cp .env.example .env

# Initialize and start services  
make init

# Check service URLs
./tools/where.sh
```

### Manual Docker Compose
```bash
# Manual setup
uv sync && cd .devcontainer && docker compose up -d
```

## 🌐 **Service Access Points**

- **Airflow UI**: http://localhost:8081 (admin/admin) - DevContainer/Compose
- **Airflow UI**: Hostname routing (see `./tools/where.sh`) - Astronomer CLI  
- **PostgreSQL**: localhost:5432 - DevContainer/Compose

## 📁 **Key Directories**

- `dags/` - Airflow DAG definitions
- `dbt/` - Data modeling and transformations
- `transforms/` - SQLModel data models
- `conf/` - Hydra configuration system
- `docs/` - Project documentation

## ⚡ **Common Commands**

### Astronomer CLI
```bash
# Start services
astro dev start

# Check status
astro dev ps

# View logs
astro dev logs

# Stop services
astro dev stop
```

### Docker Compose (Alternative)
```bash
# Start services
docker compose up -d

# Check status  
docker compose ps

# Stop services
docker compose down
```

### Configuration
```bash
# Run with default config
python scripts/run_pipeline.py

# Run with production config
python scripts/run_pipeline.py environment=prod

# Override specific settings
python scripts/run_pipeline.py database.host=prod-server runtime.debug=true
```

### Environment Management
```bash
# Check service URLs and status
./tools/where.sh

# Export requirements
make export

# Deploy to environment
# See envs/CLAUDE.md for deployment patterns
```

## 🐛 **Quick Troubleshooting**

### Services won't start
```bash
# Clean up resources  
docker compose down -v

# Or with Astro CLI
astro dev stop

# Restart fresh
./scripts/setup-development.sh
```

### Slow performance
```bash
# Check if you're in WSL2 filesystem (Windows)
pwd  # Should show /home/user/... not /mnt/c/

# Check service status
./tools/where.sh
```

### Permission errors
```bash
# Fix Docker permissions
sudo usermod -aG docker $USER
# Logout and login again
```

## 📚 **Documentation**

- **Complete docs**: [`docs/index.md`](index.md)
- **Configuration**: [`docs/configuration/README.md`](configuration/README.md)
- **Getting started**: [`docs/getting-started.md`](getting-started.md)
- **Secrets management**: [`secrets/CLAUDE.md`](../secrets/CLAUDE.md)
- **Environment config**: [`envs/CLAUDE.md`](../envs/CLAUDE.md)

## 🔧 **Enterprise Features**

With Astronomer integration:
- **{{cookiecutter.executor}}** - Production-ready execution
- **{{cookiecutter.secrets_strategy}}** - Secure secret management  
- **Multi-environment** - Consistent dev/staging/prod deployment
- **Enterprise monitoring** - Built-in observability patterns

---

**Author**: {{cookiecutter.author_name}}  
**Generated from**: [Data Engineering Template](https://github.com/Troubladore/data-eng-template)