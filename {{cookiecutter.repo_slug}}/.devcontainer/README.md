# DevContainer Configuration

This project uses **DevContainer Service Manager** for intelligent service orchestration with conflict detection and service reuse.

## Architecture

- **Service Manager**: `dcm` (DevContainer Service Manager) handles all service lifecycle
- **Configuration**: `.devcontainer/services.yaml` declares needed services
- **Isolation**: Project+branch namespacing prevents conflicts
- **Reuse**: Services are shared across DevContainer sessions to eliminate startup churn

## Quick Start

The DevContainer is configured to automatically start services:

1. **Open in DevContainer**: VS Code will run `dcm up` automatically
2. **Services Start**: Postgres and Airflow services start in isolated namespace
3. **Development Ready**: Services are available at predictable URLs

## Service Management

### CLI Commands

```bash
# Check service status
dcm status

# Manually start services  
dcm up --config .devcontainer/services.yaml

# Stop services for current project
dcm down

# Check service health
dcm health

# View all managed services
dcm status --all

# Clean up unused services
dcm clean --unused
```

### Service Configuration

Services are defined in `.devcontainer/services.yaml`:

```yaml
namespace: "{{cookiecutter.repo_slug}}"
services:
  postgres:
    template: "postgres:{{cookiecutter.postgres_version}}"
    persistent: true
    health_check: true
  
  airflow-webserver:
    template: "airflow:{{cookiecutter.airflow_version}}"
    component: "webserver" 
    depends_on: ["airflow-init"]
    ports: ["webserver:8080"]
```

## Service Access

- **Airflow UI**: http://localhost:8080 (admin/admin)
- **Postgres**: localhost:5432 (credentials in cookiecutter config)

## Benefits Over Docker Compose

1. **No Port Conflicts**: Automatic port conflict detection and resolution
2. **Service Reuse**: Share services across branches and projects
3. **Namespace Isolation**: Clean separation between different projects
4. **Health Monitoring**: Continuous service health checks with auto-repair
5. **Smart Startup**: Only start services that aren't already running

## Troubleshooting

### Service Won't Start
```bash
# Check service health
dcm health

# Restart specific service
dcm repair --service postgres

# View service logs (if using Docker)
docker logs {{cookiecutter.repo_slug}}_postgres
```

### Port Conflicts
```bash
# Check what's using ports
dcm status --all

# Clean up unused services
dcm clean --unused
```

### Reset Everything
```bash
# Stop all services for this project
dcm down

# Clean up and restart
dcm clean --namespace {{cookiecutter.repo_slug}}
dcm up
```

## Migration from Docker Compose

The old `compose.yaml` has been backed up as `compose.yaml.backup`. The new service manager provides the same functionality with additional benefits:

- **Conflict Detection**: No more "port already in use" errors
- **Service Persistence**: Services survive DevContainer restarts  
- **Health Monitoring**: Automatic detection and repair of failed services
- **Resource Efficiency**: Shared services reduce memory and CPU usage

## Configuration Reference

See the DevContainer Service Manager documentation for complete configuration options:
- Service templates
- Environment variables
- Port mapping
- Volume mounting
- Health checks
- Dependencies