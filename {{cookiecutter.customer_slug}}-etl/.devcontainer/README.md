# DevContainer Configuration

This is the **recommended development environment** for {{cookiecutter.project_name}}. The DevContainer provides a fully automated, zero-configuration setup that works consistently across all team members.

## ⚡ **Why DevContainer is Recommended**

- **One-Click Setup**: `code .` → "Reopen in Container" → Development ready!
- **Zero Configuration**: All services, ports, tooling, extensions configured automatically  
- **Consistent Experience**: Same environment for all developers, no "works on my machine"
- **Integrated Debugging**: Native VS Code debugging with breakpoints in DAGs and transforms
- **Port Forwarding**: Direct access to services without complex networking
- **Minimal Dependencies**: Only requires VS Code + Docker (no Astro CLI, no manual setup)

## Architecture

- **Compose Services**: Standard Docker Compose with Airflow and PostgreSQL
- **Configuration**: `.devcontainer/compose.yaml` declares development services
- **Environment Variables**: `.env` file provides configuration
- **Astronomer Compatibility**: Services configured to work with Astro CLI

## Quick Start

The DevContainer is configured to automatically start services:

1. **Open in DevContainer**: VS Code will start compose services automatically
2. **Services Available**: Postgres and Airflow services start with proper networking
3. **Development Ready**: Services available at configured ports

## Service Management

### Docker Compose Commands

```bash
# Check service status
docker compose ps

# Manually start services
docker compose up -d

# Stop services
docker compose down

# View service logs
docker compose logs

# Restart specific service
docker compose restart airflow-webserver
```

### Astronomer CLI Integration

If you have the Astro CLI installed:

```bash
# Initialize Astro project (if not already done)
astro dev init

# Start with Astro CLI
astro dev start

# Check Astro services
astro dev ps

# Stop Astro services
astro dev stop
```

## Services

### Airflow
- **Webserver**: http://localhost:8080 (admin/admin)
- **Scheduler**: Background service for task scheduling
- **Executor**: {{cookiecutter.executor}}

### PostgreSQL
- **Host**: localhost
- **Port**: 5432
- **Database**: {{cookiecutter.db_name}}
- **User**: {{cookiecutter.db_user}}
- **Password**: {{cookiecutter.db_password}}

## Configuration

### Environment Files
- `.env`: Main environment configuration
- `airflow.env`: Airflow-specific environment variables
- `.env.example`: Template for environment configuration

### Service Configuration
- `compose.yaml`: Main service definitions
- `devcontainer.json`: VS Code DevContainer configuration

## Development Workflow

1. **Make changes** to DAGs, configs, or code
2. **Services auto-reload** where supported (Airflow DAGs, configuration)
3. **Manual restart** required for major changes: `docker compose restart`
4. **Check logs** with `docker compose logs [service]`

## Troubleshooting

### Common Issues

**Services won't start**:
```bash
# Check for port conflicts
docker compose down
docker compose up -d
```

**Database connection issues**:
```bash
# Restart postgres service
docker compose restart postgres
```

**Airflow UI not accessible**:
```bash
# Check airflow services
docker compose logs airflow-webserver
docker compose restart airflow-webserver
```

### Reset Environment

To completely reset the development environment:

```bash
# Stop and remove all containers and volumes
docker compose down -v

# Remove built images (optional)
docker compose down -v --rmi all

# Start fresh
docker compose up -d
```

## Astronomer Migration

This project is designed to work with both Docker Compose (for basic development) and Astronomer CLI (for production-like development):

- **Docker Compose**: Basic development workflow
- **Astro CLI**: Production-like development with better Airflow integration
- **Hybrid**: Use both as needed for different development scenarios

To fully migrate to Astro CLI, run:
```bash
astro dev init --no-overwrite
astro dev start
```