# Deployment Guide

Comprehensive guide for deploying Airflow with optimized caching mechanisms, inspired by Astronomer's packaged developer deployment model.

## Overview

This template implements a sophisticated deployment system that optimizes for:

- **Fast iterations**: DAG-only deployments in seconds instead of minutes
- **Docker layer caching**: Efficient multi-stage builds with dependency caching
- **Intelligent change detection**: Automatic selection of optimal deployment strategy
- **Performance monitoring**: Built-in timing and optimization metrics

## Deployment Strategies

### 1. DAG-Only Deployment (Fastest)

Perfect for DAG development and iteration:

```bash
# Deploy only DAG files (typically takes 5-15 seconds)
make deploy-dags

# Or using the script directly
python scripts/deploy.py --dags-only
```

**Use when:**
- Only DAG files have changed
- Iterating on DAG logic during development
- Quick fixes to existing workflows

**Performance:** ⚡ 5-15 seconds

### 2. Auto-Detect Deployment (Recommended)

Intelligent deployment that chooses the right strategy:

```bash
# Automatically detect changes and choose optimal strategy
make deploy

# Or using the script directly
python scripts/deploy.py --detect-changes
```

**Detection Logic:**
- **DAG-only** if only `dags/` directory changed
- **Full rebuild** if dependencies changed (`pyproject.toml`, `requirements.txt`, `Dockerfile.airflow`)
- **Image rebuild** if code changed but dependencies stayed the same

**Performance:** ⚡ 5-15 seconds (DAG-only) to 🐢 2-5 minutes (full rebuild)

### 3. Full Deployment (Most Complete)

Complete rebuild including all dependencies:

```bash
# Full deployment with dependency installation
make deploy-full

# Or using the script directly
python scripts/deploy.py --full
```

**Use when:**
- Dependencies have changed
- First-time deployment
- Production deployments
- When you want to ensure everything is fresh

**Performance:** 🐢 2-5 minutes

## Docker Caching Optimization

### Multi-Stage Build Architecture

The deployment uses an optimized `Dockerfile.airflow` with three stages:

```dockerfile
# 1. Dependencies Stage - Cached separately
FROM apache/airflow:{{cookiecutter.airflow_version}} AS dependencies
# Install Python dependencies (cached until requirements change)

# 2. Runtime Stage - Application code
FROM dependencies AS runtime  
# Copy DAGs, plugins, transforms (changes more frequently)

# 3. Development Stage - Debug tools
FROM runtime AS development
# Additional development tools for local work
```

### Caching Benefits

- **Dependency layer caching**: Python packages only reinstall when `requirements.txt` changes
- **Multi-stage optimization**: Only rebuild what changed
- **Volume mount caching**: Faster local development with persistent caches
- **Registry caching**: Pull existing layers from container registry

### Cache Performance

| Change Type | Cache Hit | Build Time | Deployment Time |
|------------|-----------|------------|-----------------|
| DAG only | 100% | 0s | 5-15s |
| Code only | 80% | 30s | 1-2min |
| Dependencies | 20% | 2-3min | 2-5min |
| Full rebuild | 0% | 3-5min | 3-6min |

## Change Detection System

The deployment script uses intelligent change detection:

### File Monitoring

```yaml
# Files that trigger full rebuild
full_rebuild_triggers:
  - pyproject.toml
  - uv.lock  
  - airflow/requirements.txt
  - Dockerfile.airflow

# Files that only need DAG deployment
dag_only_triggers:
  - dags/

# Files that need image rebuild
image_rebuild_triggers:
  - airflow/plugins/
  - transforms/
  - conf/
```

### Cache Management

The system maintains a `.deploy_cache.json` file tracking:
- SHA256 hashes of all monitored files/directories
- Last deployment timestamp
- Previous deployment strategy

```bash
# View deployment status
make deploy-status

# Clean deployment cache (forces full rebuild next time)  
make deploy-clean
```

## Local Development Workflow

### DevContainer Integration

The deployment system integrates seamlessly with VS Code DevContainers:

```bash
# Start development environment
code .  # Open in VS Code DevContainer

# Deploy changes during development
make deploy              # Auto-detect and deploy
make deploy-dags         # DAG-only (fastest)
make deploy-dags-dry     # Preview without deploying
```

### Volume Optimization

Development environment uses optimized volume mounts:

```yaml
# Cached mounts for better performance (especially on macOS/Windows)
volumes:
  - ../dags:/opt/airflow/dags:cached
  - ../airflow/plugins:/opt/airflow/plugins:cached
  - pip_cache:/home/airflow/.cache/pip      # Persistent pip cache
  - uv_cache:/home/airflow/.cache/uv        # Persistent uv cache
```

### Hot Reload Configuration

Airflow is configured for rapid development:

```yaml
# Fast DAG discovery and reloading
dag_dir_list_interval: 10  # Check for changes every 10 seconds
reload_on_plugin_change: true
dag_discovery_safe_mode: false  # Faster but less safe parsing
```

## Performance Monitoring

### Built-in Timing

All deployments include automatic timing:

```bash
# Deploy with timing information
make deploy

# Output includes:
# ⏱️  Docker build: 45.2s
# ⏱️  Service restart: 12.1s  
# 📊 Deployment completed in 57.3s
```

### Performance Testing

Test deployment performance:

```bash
# Run deployment performance benchmarks
make deploy-perf-test

# Test specific strategies
make deploy-dags-dry     # Test DAG-only speed
make deploy-full-dry     # Test full rebuild speed
```

### Optimization Tips

**For Faster DAG Development:**
1. Use `make deploy-dags` for DAG-only changes
2. Enable hot-reload in local development
3. Use volume mounts instead of image rebuilds

**For Faster Dependency Changes:**
1. Use Docker layer caching
2. Order dependencies by change frequency
3. Use `.dockerignore` to minimize build context

**For Production Deployments:**
1. Use registry caching for faster pulls
2. Implement build cache sharing in CI/CD
3. Use multi-stage builds to minimize final image size

## Environment-Specific Deployment

### Local Development (Default)

```bash
# Uses development configuration automatically
make deploy
```

**Characteristics:**
- Fast iteration optimized
- Hot-reload enabled
- Volume mount optimization
- Debug tools included

### Development/Staging Environment

```bash
# Deploy with dev environment configuration
python scripts/deploy.py --config dev --detect-changes
```

**Characteristics:**
- Production-like builds
- Registry caching
- Comprehensive testing
- CI/CD integration

### Production Environment

```bash
# Deploy with production configuration
python scripts/deploy.py --config prod --full
```

**Characteristics:**
- Full rebuilds only (safety)
- Security scanning
- Health check validation
- Rollback capabilities

## Troubleshooting

### Common Issues

**Slow Deployments:**
```bash
# Check cache status
make deploy-status

# Clean cache if corrupted
make deploy-clean

# Test with dry run first
make deploy-auto-dry
```

**Build Failures:**
```bash
# Check Docker daemon
docker info

# Clean Docker cache
docker system prune -f

# Rebuild without cache
docker build --no-cache -f Dockerfile.airflow .
```

**Change Detection Issues:**
```bash
# Force specific strategy
make deploy-full    # Force full rebuild
make deploy-dags    # Force DAG-only

# Check what changed
python scripts/deploy.py --detect-changes --dry-run
```

### Debugging

Enable verbose output:

```bash
# Verbose deployment
python scripts/deploy.py --detect-changes --verbose

# Check deployment logs
docker-compose -f .devcontainer/compose.yaml logs airflow-scheduler
```

## CI/CD Integration

See the [GitHub Actions workflow](.github/workflows/deploy.yml) for example CI/CD integration using:

- Automatic change detection
- Registry caching
- Multi-environment deployment
- Performance monitoring

## Further Reading

- [Astronomer Deployment Best Practices](https://docs.astronomer.io/astro/deploy-dags)
- [Docker Multi-Stage Build Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Airflow Performance Tuning](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)