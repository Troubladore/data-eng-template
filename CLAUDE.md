# Data Engineering Cookiecutter Template - Template Development Guide

This is the **outer layer** guidance for Claude when working on the **cookiecutter template itself**. 

**IMPORTANT**: This repository is a cookiecutter template, not a working data engineering project. Users generate projects from this template using `cookiecutter .`

---

## Template Responsibilities

This outer layer handles:
- **Cookiecutter mechanics**: Template structure, variables, generation process
- **DevContainer configuration**: Docker Compose, environment setup, tool installation
- **Template-level tooling**: Bootstrap scripts, post-generation hooks
- **Cross-cutting architecture**: Tool selection, integration patterns
- **Template maintenance**: Updates, testing, documentation

**NOT handled here**: Domain-specific data engineering patterns (those go in inner layer guidance files)

---

## Unified Configuration System

This template now uses **Hydra** for configuration management, replacing the fragmented `.env`/Docker env/hardcoded approach with a single, hierarchical system.

### Key Benefits

- **Single Source of Truth**: All configuration in `conf/` directory
- **Type Safety**: Pydantic validation with IDE support
- **Environment Awareness**: Automatic dev/staging/prod handling
- **Command-line Flexibility**: Override any setting without editing files
- **Self-Documenting**: Every option includes inline documentation
- **Migration Path**: Backwards compatible with existing `.env` setups

### Implementation Architecture

**Configuration Files** (in generated projects):
```
{{cookiecutter.repo_slug}}/
├── conf/
│   ├── config.yaml                 # Main config with defaults
│   ├── environment/                # Environment-specific overrides
│   │   ├── dev.yaml               # Development (debug, local resources)
│   │   ├── staging.yaml           # Staging (production-like testing) 
│   │   └── prod.yaml              # Production (performance, monitoring)
│   ├── database/                   # Database provider configs
│   │   ├── postgres_local.yaml    # Local PostgreSQL (DevContainer)
│   │   ├── postgres_cloud.yaml    # Cloud PostgreSQL (RDS/Cloud SQL)
│   │   └── snowflake.yaml         # Snowflake data warehouse
│   ├── orchestration/              # Orchestrator configs
│   │   ├── airflow_local.yaml     # Local Airflow (DevContainer)
│   │   ├── airflow_k8s.yaml       # Kubernetes Airflow
│   │   └── prefect.yaml           # Alternative orchestrator
│   ├── transformations/            # dbt/transformation configs  
│   │   ├── dbt_dev.yaml           # Development dbt settings
│   │   └── dbt_prod.yaml          # Production dbt settings
│   └── compute/                    # Compute resource configs
│       ├── local.yaml             # Local development resources
│       └── distributed.yaml       # Distributed compute (Ray/Dask)
```

**Python Integration**:
- `src/config/settings.py` - Pydantic settings classes with full type safety
- `scripts/run_pipeline.py` - Hydra-integrated pipeline runner
- `scripts/migrate_config.py` - Migration tool from old `.env` files

### Usage Examples

```bash
# Default (development) configuration
python scripts/run_pipeline.py

# Production environment
python scripts/run_pipeline.py environment=prod

# Override specific settings
python scripts/run_pipeline.py database.host=prod-db.example.com runtime.parallel_jobs=8

# Combine environment and overrides
python scripts/run_pipeline.py environment=staging orchestration.parallelism=16

# Dry run (preview without execution)
python scripts/run_pipeline.py runtime.dry_run=true

# Environment variable overrides
export DATA_ENG_DATABASE_HOST=localhost
export DATA_ENG_RUNTIME_DEBUG_MODE=true
python scripts/run_pipeline.py
```

### Template Development Guidelines

When adding new configuration options:

1. **Add to appropriate section** in `conf/config.yaml` with documentation
2. **Define Pydantic model** in `src/config/settings.py` with validation
3. **Create environment-specific values** in `conf/environment/` files
4. **Add command-line example** to guidance documentation
5. **Test with different environments** and override scenarios

**Configuration Principles**:
- **Sensible defaults**: Work out-of-the-box for development
- **Environment-appropriate**: Production configs emphasize performance/monitoring
- **Type-safe**: All config options validated by Pydantic
- **Self-documenting**: Every option includes description and examples
- **Override-friendly**: Any setting changeable via command line or env vars

---

## Cookiecutter Template Structure

```
data-eng-template/
├── cookiecutter.json                    # Template variables and defaults
├── hooks/
│   └── post_gen_project.py             # Post-generation setup (Fernet keys, .env)
├── CLAUDE.md                           # THIS FILE - template development guidance
└── {{cookiecutter.repo_slug}}/         # Generated project content
    ├── CLAUDE.md                       # Inner layer - project guidance
    ├── dags/CLAUDE.md                  # Inner layer - Airflow guidance
    ├── dbt/CLAUDE.md                   # Inner layer - dbt guidance
    ├── transforms/CLAUDE.md            # Inner layer - SQLModel guidance
    ├── .devcontainer/                  # Modern DevContainer configuration
    │   ├── compose.yaml               # Modern Docker Compose using custom Airflow image
    │   └── devcontainer.json          # VS Code integration with .venv support
    └── [project files...]
```

---

## Experience Objectives for Generated Projects

1. **Zero-warning startup**: DevContainers start cleanly, no deprecation warnings or missing variables
2. **Developer convenience**: Template "just works" after generation, survives branch switches
3. **Professional defaults**: Postgres 16, Airflow, Python 3.12, modern tooling
4. **Composable services**: Airflow + Postgres as dev services, host connectivity
5. **Transparent operation**: No hidden state, explicit dependencies

---

## Template Development Workflow

### Working on Template Mechanics
When modifying cookiecutter structure, DevContainer config, or generation process:

1. **Test generation frequently**: `cookiecutter . --no-input` to verify template works
2. **Validate DevContainer**: Generated projects must start without errors
3. **Check variable propagation**: Ensure `{{cookiecutter.*}}` variables resolve correctly
4. **Test hook execution**: Verify `post_gen_project.py` creates proper `.env` files

### Cross-Cutting Architectural Changes
When updating tool versions, adding new services, or changing integration patterns:

1. **Update cookiecutter.json**: Add new variables with sensible defaults
2. **Modify DevContainer**: Update `compose.yaml` and `devcontainer.json`
3. **Update inner guidance**: Ensure generated CLAUDE.md files reflect changes
4. **Test end-to-end**: Generate project → start DevContainer → verify functionality

---

## DevContainer Configuration Principles

### Modern Service Management
- **Custom Airflow Image**: Generated projects use `{{cookiecutter.repo_slug}}-airflow-dev` with project dependencies
- **Postgres**: Version 16, dynamic host port, persistent volumes
- **Port Mapping**: Airflow UI on port 8081 to avoid conflicts, Postgres on dynamic port
- **Dependencies**: Services start in correct order with health checks
- **Project Naming**: Docker Compose projects named `{{cookiecutter.repo_slug}}-modern` to avoid conflicts

### Environment Variables
- **Template defaults**: Set in `cookiecutter.json`
- **Generated secrets**: Created by `post_gen_project.py` (Fernet keys, passwords)  
- **Override capability**: All values configurable via `.env` in generated project
- **No hardcoding**: Avoid fixed values in `compose.yaml`

### Tool Integration
- **uv**: Python package management with fallback for missing lockfiles
- **ruff**: Linting and formatting (replaces black/isort)
- **VS Code Integration**: Auto .venv detection with `python.defaultInterpreterPath`
- **DevContainer CLI Support**: Full `devcontainer up --workspace-folder` compatibility
- **Modern defaults**: Latest stable versions with conservative fallbacks

---

## Template Testing Strategy

### Generation Testing
```bash
# Test basic generation
cookiecutter . --no-input

# Test with custom values
cookiecutter . --config-file test-config.yaml

# Verify no template syntax errors
find . -name "*.py" -exec python -m py_compile {} \;
```

### DevContainer Testing  
```bash
# In generated project directory
# Start with DevContainer CLI (builds image automatically)
devcontainer up --workspace-folder .
devcontainer exec --workspace-folder . bash -c "make test"

# Or start manually for testing (builds image automatically)
cd .devcontainer
docker compose up -d
```

### Integration Testing
1. Generate project with various configurations
2. Start DevContainer services (auto-builds custom image via Docker Compose)
3. Verify Airflow UI accessible on port 8081
4. Verify .venv integration in VS Code
5. Test database connectivity
6. Run sample dbt commands

---

## File Editing Considerations

### Auto-formatter Interference
**Issue**: Ruff/other formatters modify files between Read and Edit operations

**Workaround approaches**:
1. Use bash commands: `sed`, `cat >>`, `echo >>`
2. Create new file and `mv` over original for complex changes
3. Clean up `.bak` files after modifications

**Example**:
```bash
# Instead of Edit tool for complex additions
cat >> hooks/post_gen_project.py << 'EOF'
# New functionality here
EOF
```

### Cookiecutter Template Escaping
- **dbt conflicts**: Use `{% raw %}{{ ref('model') }}{% endraw %}` for dbt Jinja
- **Variable conflicts**: Escape nested template syntax carefully
- **Testing**: Validate template renders correctly with test generation

---

## Cookiecutter Best Practices

### Variable Design
```json
{
    "repo_slug": "{{ cookiecutter.project_name.lower().replace(' ', '-').replace('_', '-') }}",
    "postgres_version": "16",
    "python_version": "3.12",
    "airflow_version": "2.8.0"
}
```

### Hook Implementation
- **Idempotent operations**: Hooks can run multiple times safely
- **Error handling**: Graceful failures with helpful messages
- **Secret generation**: Create secure random values (Fernet keys, passwords)
- **Environment setup**: Generate complete `.env` files

### Directory Structure
- **Templated folder names**: Use `{{cookiecutter.repo_slug}}/`
- **Conditional inclusion**: Use `{% if cookiecutter.feature_flag %}` for optional features
- **File permissions**: Ensure executable scripts have correct permissions

---

## ChatGPT Collaboration Workflow

### Template Development Collaboration
When working on template architecture, use ChatGPT for:
- **Tool selection decisions**: Compare alternatives, assess trade-offs
- **Configuration validation**: Review complex Docker Compose setups
- **Integration patterns**: How to best connect Airflow, dbt, Postgres
- **Best practice consultation**: Industry standards for data engineering tooling

### Design Discussion Patterns
1. **Context setting**: Always specify "cookiecutter template for data engineering"
2. **Constraint clarification**: Mention DevContainer, tool version constraints
3. **Scope limitation**: Focus on template mechanics vs domain patterns
4. **Implementation details**: Request concrete configuration examples

### Collaboration Tools Available
- `run_chatgpt(message)` - Basic chat interaction
- `create_persistent_chat(message, title, project_name)` - Named conversations
- `continue_conversation(chat_name, message, project_name)` - Continue existing chats
- Project: "Data Eng Template" - Use for template development discussions

---

## Template Evolution Strategy

### Version Management
- **Semantic versioning**: Major.Minor.Patch for template releases
- **Changelog maintenance**: Document breaking changes, new features
- **Backward compatibility**: Consider impact on existing generated projects
- **Migration guides**: Help users update to new template versions

### Feature Addition Process
1. **Requirements gathering**: What problem does this solve?
2. **Architecture design**: How does it integrate with existing tools?
3. **Implementation planning**: Template changes, hook updates, documentation
4. **Testing strategy**: How to validate the feature works correctly?
5. **Documentation updates**: Both template and generated project guidance

---

## Lessons Learned

### Critical Template Issues Resolved
1. **Cookiecutter structure**: Files must be in `{{cookiecutter.repo_slug}}/` directory
2. **Template conflicts**: Escape dbt Jinja syntax to avoid cookiecutter conflicts
3. **Environment variables**: Generate all required secrets in post-generation hook
4. **Docker Compose syntax**: Use `entrypoint + command` pattern for complex commands
5. **Testing environments**: Always test with actual target tools (devcontainer CLI)

### Development Workflow Insights
- **Iterative testing**: Generate and test frequently during development
- **Environment awareness**: Snap vs traditional packages affect paths
- **Documentation as code**: Keep guidance files synchronized with implementation
- **Template complexity**: Multiple template engines require careful coordination

This outer layer guidance focuses purely on template mechanics and generation concerns. Domain-specific data engineering guidance belongs in the inner layer CLAUDE.md files within the generated project structure.