# Operations Guide

Operational procedures for running, deploying, and maintaining {{cookiecutter.project_name}}.

## Local Development

### DevContainer Setup (Recommended)

The fastest way to get started is using VS Code DevContainers:

1. **Prerequisites**: Docker, VS Code with DevContainers extension
2. **Open project**: `code .` in project root
3. **Reopen in container**: Command Palette → "Dev Containers: Reopen in Container"
4. **Verify setup**: Container automatically runs health checks

The DevContainer provides:
- Python {{cookiecutter.python_version}} with all dependencies
- PostgreSQL database with sample data
- Airflow webserver and scheduler
- Pre-configured environment variables
- Development tools (linting, testing, debugging)

### Manual Setup

If you prefer not to use DevContainers:

```bash
# Install dependencies
uv sync

# Generate environment configuration
./scripts/export_env.sh > .env

# Start services
docker-compose -f .devcontainer/compose.yaml up -d

# Initialize database
docker-compose -f .devcontainer/compose.yaml exec airflow-webserver \
  airflow db upgrade

# Create admin user
docker-compose -f .devcontainer/compose.yaml exec airflow-webserver \
  airflow users create \
  --username admin \
  --password admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com
```

### Development Workflow

```bash
# Run pipeline in dry-run mode
python scripts/run_pipeline.py runtime.dry_run=true

# Test configuration changes
python scripts/run_pipeline.py database.host=test-db.com runtime.debug_mode=true

# Run dbt transformations
cd dbt
dbt run --target dev
dbt test

# Test Airflow DAGs
python -c "from dags.example_dag import dag; dag.test()"

# Run all tests
make test
```

## Environment Management

### Configuration Environments

The project supports multiple environments through Hydra configuration:

```bash
# Development (default)
python scripts/run_pipeline.py

# Staging
python scripts/run_pipeline.py environment=staging

# Production
python scripts/run_pipeline.py environment=prod

# Custom overrides
python scripts/run_pipeline.py environment=prod database.host=new-db.com
```

### Environment-Specific Settings

- **Development**: Debug enabled, smaller resources, local database
- **Staging**: Production-like setup with staging endpoints
- **Production**: Optimized for performance, monitoring enabled

### Environment Variables

For services that require environment variables:

```bash
# Generate from current Hydra configuration
./scripts/export_env.sh > .env

# Generate for specific environment
python scripts/run_pipeline.py environment=prod \
  hydra.job.chdir=false | grep "export" > .env.prod
```

## Deployment

### Container Deployment

```bash
# Build application container
docker build -t {{cookiecutter.repo_slug}}:latest .

# Run with production configuration
docker run -e ENVIRONMENT=prod {{cookiecutter.repo_slug}}:latest \
  python scripts/run_pipeline.py environment=prod
```

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{cookiecutter.repo_slug}}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {{cookiecutter.repo_slug}}
  template:
    metadata:
      labels:
        app: {{cookiecutter.repo_slug}}
    spec:
      containers:
      - name: pipeline
        image: {{cookiecutter.repo_slug}}:latest
        command: ["python", "scripts/run_pipeline.py"]
        args: ["environment=prod"]
        env:
        - name: DATABASE_HOST
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: host
```

### Cloud Deployment (AWS/GCP/Azure)

The project is designed to work with cloud services:

**AWS**:
- ECS/Fargate for container orchestration
- RDS for PostgreSQL
- MWAA (Managed Airflow) for orchestration

**GCP**:
- Cloud Run for serverless containers
- Cloud SQL for PostgreSQL  
- Composer (Managed Airflow) for orchestration

**Azure**:
- Container Instances for containers
- Database for PostgreSQL
- Data Factory for orchestration

## Monitoring

### Application Monitoring

```python
# Built-in logging configuration
python scripts/run_pipeline.py runtime.log_level=INFO

# Enable debug mode for troubleshooting
python scripts/run_pipeline.py runtime.debug_mode=true

# Monitor with dry-run
python scripts/run_pipeline.py runtime.dry_run=true
```

### Infrastructure Monitoring

- **Database**: Monitor connection counts, query performance
- **Compute**: CPU, memory, disk usage
- **Pipeline**: Execution time, failure rates, data volume

### Airflow Monitoring

Access the Airflow UI at http://localhost:8080 (admin/admin) for:
- DAG run status and history
- Task execution details and logs
- Resource utilization
- Connection and configuration management

### Health Checks

```bash
# Application health check
python -c "from {{cookiecutter.repo_slug.replace('-', '_')}}.config import get_settings; print('OK')"

# Database connectivity
./scripts/psql.sh -c "SELECT 1;"

# Airflow health
curl http://localhost:8080/health

# End-to-end pipeline test
python scripts/run_pipeline.py runtime.dry_run=true
```

## Backup and Recovery

### Database Backup

```bash
# Create database backup
./scripts/psql.sh -c "pg_dump" > backup_$(date +%Y%m%d).sql

# Restore database backup  
./scripts/psql.sh < backup_20250822.sql
```

### Configuration Backup

Configuration is version-controlled in git, but for additional safety:

```bash
# Backup all configuration
tar -czf config_backup_$(date +%Y%m%d).tar.gz conf/

# Include generated local configuration
tar -czf full_backup_$(date +%Y%m%d).tar.gz conf/ .env
```

## Troubleshooting

### Common Issues

**Configuration Errors**:
```bash
# Validate configuration
python -c "from {{cookiecutter.repo_slug.replace('-', '_')}}.config import get_settings; get_settings()"

# Check specific environment
python -c "from {{cookiecutter.repo_slug.replace('-', '_')}}.config import get_settings; get_settings(environment='prod')"
```

**Database Connection Issues**:
```bash
# Test database connectivity
./scripts/psql.sh -c "SELECT current_database(), current_user, now();"

# Check database configuration
python -c "from {{cookiecutter.repo_slug.replace('-', '_')}}.config import get_settings; s=get_settings(); print(s.database.connection_url)"
```

**Airflow Issues**:
```bash
# Reset Airflow database
docker-compose -f .devcontainer/compose.yaml exec airflow-webserver airflow db reset

# Restart Airflow services
docker-compose -f .devcontainer/compose.yaml restart airflow-webserver airflow-scheduler
```

**Pipeline Issues**:
```bash
# Run in debug mode
python scripts/run_pipeline.py runtime.debug_mode=true

# Dry run to check configuration
python scripts/run_pipeline.py runtime.dry_run=true

# Check logs
tail -f logs/pipeline.log
```

### Log Analysis

```bash
# Application logs
tail -f outputs/pipeline.log

# Airflow logs
docker-compose -f .devcontainer/compose.yaml logs -f airflow-webserver

# Database logs
docker-compose -f .devcontainer/compose.yaml logs -f postgres
```

### Performance Issues

```bash
# Profile pipeline performance
python scripts/run_pipeline.py runtime.debug_mode=true runtime.parallel_jobs=1

# Database performance
./scripts/psql.sh -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"

# Resource usage
docker stats
```

## Maintenance

### Regular Maintenance Tasks

```bash
# Update dependencies
uv sync --upgrade

# Clean up old logs
find logs/ -name "*.log" -mtime +30 -delete

# Database maintenance
./scripts/psql.sh -c "VACUUM ANALYZE;"

# Clean up Docker resources
docker system prune -f
```

### Security Updates

```bash
# Update base images
docker-compose -f .devcontainer/compose.yaml pull

# Rebuild with security patches
docker-compose -f .devcontainer/compose.yaml build --no-cache

# Rotate generated keys
rm conf/local/generated.yaml
# Regenerate by running post-generation hook or restarting DevContainer
```

### Configuration Updates

```bash
# Test configuration changes
python scripts/run_pipeline.py runtime.dry_run=true

# Validate against schema
python -c "from {{cookiecutter.repo_slug.replace('-', '_')}}.config import get_settings; get_settings()"

# Update documentation
# Edit relevant files in docs/ directory
```

## Further Reading

- [Getting Started Guide](../getting-started.md) - Setup and first steps
- [Pipeline Documentation](../pipelines/README.md) - Data processing architecture
- [FAQ](../faq.md) - Common operational issues and solutions
- [Configuration Guide](../configuration/README.md) - Configuration management