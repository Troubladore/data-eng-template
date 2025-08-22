# Configuration System

The {{cookiecutter.project_name}} uses **Hydra** for unified, type-safe configuration management.

## Why Hydra?

Traditional `.env` files become unwieldy in data engineering projects with multiple environments, services, and deployment targets. Hydra provides:

- **Hierarchical composition** - Layer configurations logically
- **Type safety** - Pydantic validation with IDE support
- **Environment management** - Clean dev/staging/prod separation
- **Runtime flexibility** - Override any setting via command line
- **Self-documenting** - Inline comments explain all options

## Configuration Structure

```
conf/
├── config.yaml                 # Main config with defaults
├── environment/
│   ├── dev.yaml                # Development overrides
│   ├── staging.yaml            # Staging overrides  
│   └── prod.yaml               # Production overrides
├── database/
│   ├── postgres_local.yaml    # Local development DB
│   └── postgres_cloud.yaml    # Production DB
├── orchestration/
│   ├── airflow_local.yaml     # Local Airflow setup
│   └── airflow_cloud.yaml     # Cloud Airflow setup
├── transformations/
│   ├── dbt_dev.yaml           # dbt development config
│   └── dbt_prod.yaml          # dbt production config
├── compute/
│   ├── local.yaml             # Local compute resources
│   └── cloud.yaml             # Cloud compute resources
└── local/                     # Local overrides (gitignored)
    └── generated.yaml         # Generated secrets & keys
```

## Basic Usage

### Command Line Interface

```bash
# Use default configuration (development)
python scripts/run_pipeline.py

# Override environment
python scripts/run_pipeline.py environment=prod

# Override specific settings
python scripts/run_pipeline.py database.host=prod-db.example.com

# Multiple overrides
python scripts/run_pipeline.py environment=staging runtime.parallel_jobs=8 runtime.debug_mode=true

# Dry run mode
python scripts/run_pipeline.py runtime.dry_run=true
```

### Python API

```python
from {{cookiecutter.repo_slug.replace('-', '_')}}.config import get_settings

# Load default configuration
settings = get_settings()

# Load specific environment
settings = get_settings(environment="prod")

# Load with command-line style overrides
settings = get_settings(overrides=["database.port=5433", "runtime.debug_mode=true"])

# Access configuration with full IDE support
print(settings.database.connection_url)
print(settings.runtime.parallel_jobs)
print(settings.orchestration.fernet_key)
```

## Configuration Layers

Hydra composes configuration in this order (later overrides earlier):

1. **Base configuration** (`config.yaml`)
2. **Environment-specific** (`environment/{env}.yaml`)
3. **Service-specific** (database, orchestration, etc.)
4. **Local overrides** (`local/generated.yaml`)
5. **Command-line overrides** (highest priority)

### Example Composition

With `python scripts/run_pipeline.py environment=prod database.port=5433`:

```yaml
# From config.yaml (base)
project:
  name: "My Data Project"
runtime:
  debug_mode: false
  parallel_jobs: 4

# From environment/prod.yaml (environment)
runtime:
  debug_mode: false  # Ensures production safety
  parallel_jobs: 16  # Higher parallelism

# From database/postgres_cloud.yaml (service)
database:
  host: "prod-cluster.amazonaws.com"
  port: 5432

# From command line (highest priority)
database:
  port: 5433  # Overrides everything else
```

## Type Safety

All configuration is validated using Pydantic models:

```python
# settings.py
class DatabaseSettings(BaseModel):
    host: str = Field(..., description="Database hostname")
    port: int = Field(5432, description="Database port", ge=1, le=65535)
    name: str = Field(..., description="Database name")
    
    @property
    def connection_url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

# Usage with full IDE support
settings = get_settings()
url = settings.database.connection_url  # Type: str, validated
```

## Environment Variables Integration

For compatibility with Docker Compose and legacy tools, configurations can be exported as environment variables:

```bash
# Generate .env file from current configuration
./scripts/export_env.sh > .env

# With specific environment
python scripts/run_pipeline.py environment=prod --config-path=conf --config-name=config hydra.job.chdir=false | grep "export" > .env

# DevContainer automatically runs this during setup
```

## Adding New Configuration

### 1. Create Configuration File

```yaml
# conf/monitoring/datadog.yaml
# @package monitoring.datadog

api_key: "${DATADOG_API_KEY}"
app_key: "${DATADOG_APP_KEY}"

metrics:
  enabled: true
  namespace: "{{cookiecutter.repo_slug}}"
  tags:
    - "env:${environment}"
    - "service:data-pipeline"

logs:
  enabled: true
  source: "python"
  service: "{{cookiecutter.project_name}}"
```

### 2. Update Pydantic Models

```python
# In settings.py
class DatadogSettings(BaseModel):
    api_key: str = Field(..., description="Datadog API key")
    app_key: str = Field(..., description="Datadog application key")
    
    metrics: dict = Field(default_factory=dict)
    logs: dict = Field(default_factory=dict)

class MonitoringSettings(BaseModel):
    datadog: DatadogSettings

class Settings(BaseModel):
    # ... existing fields ...
    monitoring: MonitoringSettings
```

### 3. Update Main Configuration

```yaml
# In config.yaml
defaults:
  - environment: dev
  - database: postgres_local  
  - orchestration: airflow_local
  - transformations: dbt_dev
  - compute: local
  - monitoring: datadog  # Add this
  - _self_
```

## Best Practices

### Configuration Organization

- **Group related settings** in dedicated files (database, orchestration, etc.)
- **Use descriptive names** for configuration files and fields
- **Add inline documentation** for complex settings
- **Provide sensible defaults** that work out of the box
- **Use environment variables** for secrets (via `${VAR}` syntax)

### Environment Management

- **dev.yaml**: Optimized for development (debug on, smaller resources)
- **staging.yaml**: Production-like but with staging endpoints
- **prod.yaml**: Production-ready (debug off, monitoring on, high resources)

### Security

- **Never commit secrets** - Use environment variable interpolation
- **Use local/ directory** for machine-specific overrides (gitignored)
- **Rotate generated keys** regularly (they're in `local/generated.yaml`)

### Testing Configuration

```python
def test_config_validation():
    """Test that configuration validates correctly."""
    settings = get_settings()
    
    # Pydantic ensures these are valid
    assert settings.database.port > 0
    assert settings.runtime.parallel_jobs >= 1
    assert settings.project.name is not None

def test_environment_overrides():
    """Test environment-specific configurations."""
    dev_settings = get_settings(environment="dev")
    prod_settings = get_settings(environment="prod")
    
    assert dev_settings.runtime.debug_mode is True
    assert prod_settings.runtime.debug_mode is False
```

## Further Reading

- [Operations Guide](../operations/README.md) - Deployment and production configuration
- [Getting Started](../getting-started.md) - Quick setup and first steps  
- [FAQ](../faq.md) - Common configuration questions