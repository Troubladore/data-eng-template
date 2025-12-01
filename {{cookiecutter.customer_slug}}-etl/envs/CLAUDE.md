# Environment Configuration - {{cookiecutter.project_name}}

This directory contains **environment-specific** configurations for `{{cookiecutter.env_name|join("`, `")}}` environments, providing consistent deployment patterns across the development lifecycle.

## What

Environment-specific overrides for Airflow settings, Kubernetes values, and deployment configurations that adapt the same codebase to different runtime environments.

## Why  

- **Consistency**: Same codebase deployed identically across environments
- **Configuration as Code**: All environment differences captured in version-controlled files
- **Deployment Automation**: Automatic environment detection and configuration loading
- **Scaling Strategy**: Different resource allocations per environment (dev vs prod)

## How

### Configuration Structure

Each environment directory contains:

```
envs/{environment}/
├── .env.example              # Environment variables and connection examples
├── airflow_settings.yaml     # Airflow-specific configuration overrides  
└── k8s-values.patch.yaml     # Kubernetes values patch for Helm deployments
```

### Environment Detection

The deployment system automatically detects target environment via:
- **Branch-based**: `main` → prod, `staging` → qa, `develop` → dev
- **Explicit**: Environment specified in deployment pipeline
- **Local Override**: `.env` file for local development overrides

## Environment-Specific Patterns

### Development (`dev/`)
- **Resource Limits**: Minimal resource allocation for cost efficiency
- **Debug Mode**: Enhanced logging and development tools enabled
- **Local Connectivity**: Database and service endpoints for local development
- **Relaxed Security**: Simplified authentication for development workflow

### QA/Staging (`qa/`)
- **Production-Like**: Mirror production configuration with smaller scale
- **Testing Tools**: Additional testing and monitoring capabilities
- **Stable Versions**: Lock to stable versions for consistent testing
- **Staging Data**: Isolated staging data sources and destinations

### Production (`prod/`)
- **High Availability**: Multi-replica deployments with health checks  
- **Performance Optimization**: Optimized resource allocation and caching
- **Security Hardening**: Full security configuration and monitoring
- **Monitoring & Alerting**: Comprehensive observability and incident response

## Configuration Examples

### Airflow Settings

```yaml
# dev/airflow_settings.yaml
airflow:
  config:
    core:
      parallelism: 4
      max_active_tasks_per_dag: 2
    logging:
      logging_level: DEBUG

# prod/airflow_settings.yaml  
airflow:
  config:
    core:
      parallelism: 32
      max_active_tasks_per_dag: 16
    logging:
      logging_level: INFO
```

### Kubernetes Resource Allocation

```yaml
# dev/k8s-values.patch.yaml
resources:
  limits:
    cpu: "500m"
    memory: "1Gi"
  requests:
    cpu: "200m" 
    memory: "512Mi"

# prod/k8s-values.patch.yaml
resources:
  limits:
    cpu: "2000m"
    memory: "4Gi"
  requests:
    cpu: "1000m"
    memory: "2Gi"
```

### Environment Variables

```bash
# dev/.env.example
DATABASE_HOST=localhost
DATABASE_NAME=dev_{{cookiecutter.customer_slug}}_etl
AIRFLOW_HOST={{cookiecutter.customer_slug}}-etl.{{cookiecutter.local_domain}}

# prod/.env.example  
DATABASE_HOST={{cookiecutter.customer_slug}}-db.{{cookiecutter.company_domain}}
DATABASE_NAME=prod_{{cookiecutter.customer_slug}}_etl
AIRFLOW_HOST={{cookiecutter.customer_slug}}-etl.{{cookiecutter.company_domain}}
```

## Deployment Integration

### CI/CD Pipeline Integration

The deployment pipeline automatically applies environment-specific configuration:

```yaml
# .ado/pipelines/airflow-deploy.yml (excerpt)
- task: HelmDeploy
  inputs:
    command: 'upgrade'
    chartPath: './helm/airflow'
    releaseName: '{{cookiecutter.customer_slug}}-etl-$(environment)'
    valueFile: './envs/$(environment)/k8s-values.patch.yaml'
```

### Local Development Override

```bash
# Copy environment template for local development
cp envs/dev/.env.example .env

# Edit .env with your local development settings
# Start local environment
make init
```

## Best Practices

1. **Environment Parity**: Keep environments as similar as possible, differing only in scale and endpoints
2. **Configuration Validation**: Validate configuration files in CI/CD pipeline
3. **Secret Management**: Store secrets in environment-specific secret stores, never in config files
4. **Resource Planning**: Plan resource allocation based on actual usage patterns
5. **Monitoring**: Deploy same monitoring stack across all environments for consistency

## Adding New Environments

To add a new environment (e.g., `staging`):

1. **Create Directory**: `mkdir envs/staging`
2. **Copy Templates**: Copy from similar environment (usually `qa/`)
3. **Update Configuration**: Adjust settings for new environment requirements
4. **Update Pipeline**: Add environment to deployment pipeline configuration
5. **Test Deployment**: Verify deployment works with new configuration

This approach ensures consistent, predictable deployments while maintaining environment-appropriate configuration differences.