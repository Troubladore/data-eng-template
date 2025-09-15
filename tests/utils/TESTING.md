# Testing the Data Engineering Template

This guide explains how to test the cookiecutter template while maintaining clean Docker environments.

## Docker Artifact Naming Scheme

The template now uses a consistent naming scheme to distinguish test artifacts from production ones:

### Production Mode (default)
```bash
cookiecutter . --no-input
# or
cookiecutter . --no-input deployment_mode=production
```

**Generates:**
- **Project name**: `customer-a-etl/`
- **Compose projects**: `customer-a-etl-modern`, `customer-a-etl-test-fast`
- **Docker images**: `customer-a-etl-airflow-dev`, `customer-a-etl-airflow-fast-test`
- **Containers**: `customer-a-etl-postgres`, `customer-a-etl-airflow-webserver`, etc.

### Testing Mode
```bash
cookiecutter . --no-input deployment_mode=testing
```

**Generates:**
- **Project name**: `customer-a-etl/`
- **Compose projects**: `customer-a-etl-modern-test`, `customer-a-etl-test-fast-test`
- **Docker images**: `customer-a-etl-airflow-dev-test`, `customer-a-etl-airflow-fast-test-test`
- **Containers**: `customer-a-etl-postgres-test`, `customer-a-etl-airflow-webserver-test`, etc.

### Docker Labels for Easy Identification

All containers are labeled with:
- `de-template.project=<project_slug>`
- `de-template.deployment=<production|testing>`
- `de-template.service=<postgres|airflow-webserver|etc>`

**View labeled containers:**
```bash
# View all data-eng-template containers
docker ps -a --filter "label=de-template.project"

# View only test containers
docker ps -a --filter "label=de-template.deployment=testing"

# View specific project
docker ps -a --filter "label=de-template.project=customer-a-etl"
```

## Testing Workflow

### 1. Generate Test Project
```bash
# Generate a testing-mode project
cookiecutter . --no-input deployment_mode=testing

# Navigate to generated project
cd customer-a-etl/
```

### 2. Test the Generated Project
```bash
# Start DevContainer services
cd .devcontainer
docker compose up -d

# Verify services
docker compose ps

# Access Airflow UI at http://localhost:8081
```

### 3. Clean Up After Testing

#### Shallow Cleanup (recommended)
Removes generated project directories and their associated Docker artifacts:
```bash
cd ../  # Return to template repo
./cleanup-shallow.sh
```

#### Deep Cleanup (nuclear option)
Removes **ALL** data-eng-template related Docker artifacts:
```bash
./cleanup-deep.sh
```

## Multiple Testing Iterations

For repeated testing with clean environments:

```bash
# Test iteration 1
cookiecutter . --no-input deployment_mode=testing
cd customer-a-etl && cd .devcontainer && docker compose up -d
# ... test the setup ...
cd ../../ && ./cleanup-shallow.sh

# Test iteration 2
cookiecutter . --no-input deployment_mode=testing customer_slug=test-project-2
cd test-project-2-etl && cd .devcontainer && docker compose up -d
# ... test different configuration ...
cd ../../ && ./cleanup-shallow.sh

# Final cleanup
./cleanup-deep.sh
```

## Advanced Testing Scenarios

### Testing Different Configurations
```bash
# Test with different customer slug
cookiecutter . --no-input deployment_mode=testing customer_slug=acme-corp

# Test with different database
cookiecutter . --no-input deployment_mode=testing postgres_version=15

# Test with different Python version
cookiecutter . --no-input deployment_mode=testing python_version=3.11
```

### Custom Config File for Testing
Create a `test-config.yaml` file:
```yaml
default_context:
  customer_slug: "test-company"
  deployment_mode: "testing"
  postgres_version: "15"
  python_version: "3.11"
  enable_kerberos: "yes"
```

Use it:
```bash
cookiecutter . --config-file test-config.yaml --no-input
```

## Cleanup Scripts Reference

### cleanup-shallow.sh
- **Purpose**: Remove generated project folders and their Docker artifacts
- **Safety**: High - only removes artifacts from generated projects
- **Use case**: Regular testing cleanup
- **What it removes**:
  - Generated project directories
  - Docker Compose projects associated with those directories
  - Docker images built by those projects
  - Docker containers, networks, and volumes

### cleanup-deep.sh
- **Purpose**: Remove ALL data-eng-template related Docker artifacts
- **Safety**: Low - requires confirmation, removes everything
- **Use case**: Complete environment reset
- **What it removes**:
  - All containers with `de-template` labels
  - All Docker Compose projects matching template patterns
  - All Docker images matching template patterns
  - All untagged images (`<none>` images)
  - All template-related volumes and networks
  - Docker build cache

## Troubleshooting

### "No space left on device" errors
```bash
# Check Docker disk usage
docker system df

# Run deep cleanup
./cleanup-deep.sh

# If still having issues, prune everything
docker system prune -a --volumes
```

### Containers won't stop
```bash
# Force remove all template containers
docker ps -a --filter "label=de-template.project" -q | xargs docker rm -f

# Or manually kill specific containers
docker kill <container_name>
docker rm <container_name>
```

### Finding orphaned resources
```bash
# Find all template-related containers
docker ps -a --filter "label=de-template.project" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"

# Find all template-related images
docker images | grep -E "(etl|airflow|test)"

# Find all template-related volumes
docker volume ls | grep -E "(etl|airflow|postgres)"
```

## Best Practices

1. **Always use testing mode** when generating projects for testing
2. **Run cleanup after each test iteration** to avoid accumulating artifacts
3. **Use shallow cleanup** for regular testing, deep cleanup only when needed
4. **Check Docker disk usage** regularly with `docker system df`
5. **Use specific customer_slug values** to avoid conflicts between different test runs

## Integration with CI/CD

For automated testing in CI/CD pipelines:

```bash
#!/bin/bash
set -e

# Generate test project
cookiecutter . --no-input deployment_mode=testing

# Test the generated project
cd customer-a-etl
cd .devcontainer
docker compose up -d
sleep 30  # Wait for services to start

# Run tests
docker compose exec airflow-webserver airflow dags list
# Add more tests here

# Cleanup
cd ../../
./cleanup-shallow.sh
```