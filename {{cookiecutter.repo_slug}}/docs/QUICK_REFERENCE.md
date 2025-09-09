# {{cookiecutter.project_name}} - Quick Reference

## 🚀 **Get Started Fast**

### Option 1: Optimized Setup (Recommended)
```bash
./scripts/setup-development.sh
```

### Option 2: Manual Setup
```bash
uv sync
./scripts/export_env.sh > .env
cd .devcontainer && docker compose up -d
```

## 🌐 **Service Access Points**

- **Airflow UI**: http://localhost:8081 (admin/admin)
- **PostgreSQL**: localhost:5432 (postgres/postgres)

## 📁 **Key Directories**

- `dags/` - Airflow DAG definitions
- `dbt/` - Data modeling and transformations
- `transforms/` - SQLModel data models
- `conf/` - Hydra configuration system
- `docs/` - Project documentation

## ⚡ **Common Commands**

### Development
```bash
# Start services
dcm up                          # If using service manager
# OR
cd .devcontainer && docker compose up -d

# Check status
dcm status                      # Service manager
# OR  
docker compose ps               # Docker compose

# Stop services
dcm down                        # Service manager
# OR
docker compose down             # Docker compose
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

### Performance Tools (if installed)
```bash
# Check cache status
dcm-cache status

# Validate workstation setup
dcm-setup validate

# Fix common issues
dcm-setup troubleshoot
```

## 🐛 **Quick Troubleshooting**

### Services won't start
```bash
# Clean up resources
dcm-setup cleanup
# OR
docker compose down -v

# Restart fresh
./scripts/setup-development.sh
```

### Slow builds
```bash
# Check if you're in WSL2 filesystem (Windows)
pwd  # Should show /home/user/... not /mnt/c/

# Check cache status
dcm-cache status
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

## 🔧 **Performance Benefits**

With optimized setup:
- **149x faster builds** via fingerprint caching
- **Cross-repository sharing** - cache benefits all your projects
- **WSL2 optimization** - 10x faster file I/O
- **Automatic cleanup** - no resource accumulation

---

**Author**: {{cookiecutter.author_name}}  
**Generated from**: [Data Engineering Template](https://github.com/Troubladore/data-eng-template)