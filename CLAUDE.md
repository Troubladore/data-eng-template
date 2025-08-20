# claude.md — Guidance for Working in This Repo

This repository is a **cookiecutter-based template** for reproducible, modern **data engineering projects**.  
It integrates Airflow, Postgres, dbt, and a VS Code DevContainer with opinionated defaults.

**IMPORTANT**: This repository contains template files with `{{cookiecutter.*}}` placeholders and should **not** be used directly. Users must first generate a project from this template using `cookiecutter .` before using the DevContainer.

Claude should follow these guidelines when answering questions, writing code, or suggesting changes:

---

## Experience Objectives

1. **Zero-warning startup**  
   - DevContainers must start cleanly with no Compose deprecation warnings, missing env variables, or brittle defaults.  
   - Ports should not collide on host; use environment variables or dynamic host ports when necessary.

2. **Developer convenience without hidden magic**  
   - The template should “just work” on first open, and keep working after branch switches.  
   - Routine tasks like `uv sync` (for Python deps) run automatically on container start, but **installation of tools (e.g. uv)** is not handled ad-hoc. Those are managed declaratively by Ansible.

3. **Professional defaults, easy overrides**  
   - Sensible defaults for Postgres (v16), Airflow, Python (3.12).  
   - All overridable via `.env`, with `cookiecutter.json` defining initial defaults.  
   - Avoid hard-coding values in `compose.yaml` that can live in `.env`.

4. **Modern Python tooling**  
   - Use `uv` as the resolver/installer.  
   - Use `ruff` for linting + formatting.  
   - Prefer `psycopg` v3 for app code, but retain `psycopg2` in Airflow’s provider chain until upstream moves.  
   - No black/isort; ruff replaces both.

5. **Transparency over hidden state**  
   - Scripts should warn/exit if required tools are missing, not auto-install.  
   - Ansible governs base state; DevContainer scripts just check and sync.

6. **Composable services**  
   - Airflow + Postgres run as services for dev only.  
   - Developers can connect from host to Postgres, so conflicts are avoided by dynamic host port binding.  
   - Airflow installs lightweight extras via `_PIP_ADDITIONAL_REQUIREMENTS` only for dev convenience.

---

## Repo Layout

- **.devcontainer/** → container config (`compose.yaml`, `devcontainer.json`, env files, bootstrap/post-start scripts)  
- **dags/** → Airflow DAGs  
- **dbt/** → dbt project with bronze/silver/gold modeling convention  
- **transforms/** → app-level SQLModel/Pydantic models  
- **scripts/** → helper scripts (`airflow-cli.sh`, `psql.sh`)  
- **hooks/** → cookiecutter hook (`post_gen_project.py`) that writes `.env` with Fernet key etc.  
- **pyproject.toml** → Python deps, uv + ruff config  
- **Makefile** → dev shortcuts (psql, tests, etc.)  

---

## DevContainer Behavior

- Defined in `.devcontainer/devcontainer.json`:
  - Services: `postgres`, `airflow-webserver`, `airflow-scheduler`
  - User: `vscode`
  - Ports: 8080 (Airflow UI), 5432 (Postgres, dynamic override allowed)
  - Lifecycle:
    - `postCreateCommand`: runs `bootstrap-dev.sh` (idempotent setup)  
    - `postStartCommand`: runs `post-start.sh` (dependency sync via `uv`)  

- **post-start.sh**:  
  - Verifies `uv` is installed.  
  - Runs `uv sync --frozen` only when lockfile changed.  
  - Exits with warning if uv missing (installation managed elsewhere).

---

## How to Interact with Claude

When asking Claude for help:
- Prefer **concrete changes** (diffs to `compose.yaml`, `pyproject.toml`, etc.).  
- Preserve the separation of responsibilities:
  - `cookiecutter.json` defines project defaults.  
  - `post_gen_project.py` seeds `.env` with Fernet key + defaults.  
  - DevContainer scripts sync the venv but don’t mutate system state.  
- Always assume **clean, professional, reproducible** is the target outcome.

Claude should:
- Suggest updates in terms of cookiecutter, `.env`, and scripts—not host hacks.  
- Flag deprecated/brittle constructs (like Compose `version:` keys).  
- Default to the **simplest, maintainable pattern** that minimizes surprises for developers.

---

## File Editing Notes

**Issue**: Auto-formatters (likely Ruff) may modify files between Read and Edit operations, causing Edit tool failures.

**Workaround**: If Edit tool consistently fails with "file has been modified" errors:
1. Use bash commands for file modifications: `sed`, `cat >>`, `echo >>`
2. For complex changes, create new file and `mv` over original
3. Clean up any `.bak` or temp files created during the process

**Example**:
```bash
# Instead of Edit tool:
cat >> hooks/post_gen_project.py << 'EOF'
# new code here


---

## File Editing Notes

**Issue**: Auto-formatters (likely Ruff) may modify files between Read and Edit operations, causing Edit tool failures.

**Workaround**: If Edit tool consistently fails with "file has been modified" errors:
1. Use bash commands for file modifications: `sed`, `cat >>`, `echo >>`
2. For complex changes, create new file and `mv` over original  
3. Clean up any `.bak` or temp files created during the process

**Example**: Use `cat >> file.py << 'EOF'` instead of Edit tool for appending code.


**EOF Issues**: When using heredoc syntax, avoid complex quoting. Use simple echo or printf instead:
- ❌ `cat >> file << 'EOF'` with nested quotes/backticks  
- ✅ `echo "content" >> file` or `printf "content" >> file`


---

## Lessons Learned from Template Development

### Key Issues Encountered and Solutions

1. **Cookiecutter Template Structure**
   - **Problem**:  - cookiecutter couldn't find template directories
   - **Root Cause**: Files were in repo root instead of  directory
   - **Solution**: Move all project files into  directory
   - **Lesson**: Cookiecutter requires specific directory structure with templated folder name

2. **dbt Jinja Template Conflicts**  
   - **Problem**:  - cookiecutter tried to process dbt's  syntax
   - **Root Cause**: Both cookiecutter and dbt use  syntax, causing conflicts
   - **Solution**: Escape dbt syntax with 
   - **Lesson**: Always escape nested template languages when using cookiecutter

3. **Missing Environment Variables**
   - **Problem**:  failed with missing  and 
   - **Root Cause**:  didn't generate required Airflow admin credentials  
   - **Solution**: Add missing variables to the .env generation in post-generation hook
   - **Lesson**: Ensure all environment dependencies are documented and generated

4. **Docker Compose Command Parsing**
   - **Problem**: Complex bash commands in  field being parsed as individual arguments
   - **Root Cause**: YAML multiline syntax and entrypoint/command interaction
   - **Multiple attempts**: , , , 
   - **Working solution**:  + 
   - **Lesson**: Docker Compose YAML syntax is very specific about string vs array parsing

5. **File Modification Detection Issues**
   - **Problem**: Edit tool failing with "file has been modified" errors
   - **Root Cause**: Auto-formatters (likely Ruff) modifying files between Read and Edit operations  
   - **Solution**: Use bash commands (, , ) instead of Edit tool
   - **Lesson**: Document workarounds for auto-formatter interference

6. **Environment-Specific Testing Challenges**
   - **Problem**: Different behavior between Docker Desktop vs Podman, snap confinement issues
   - **Root Cause**: Testing environment didn't match user environment
   - **Solution**: Test with actual tools user will use (devcontainer CLI, not just docker-compose)
   - **Lesson**: Always test in the target environment, not just isolated components

### Development Workflow Insights

- **Test iteratively**: Don't assume fixes work - validate each change end-to-end
- **Document as you go**: File editing workarounds, YAML syntax gotchas, etc.
- **Environment matters**: Snap packages, Podman vs Docker, auto-formatters all affect behavior
- **Template complexity**: Multiple template engines (cookiecutter + dbt) require careful escaping
- **Dependencies cascade**: Missing env vars cause container failures which cause devcontainer failures

---

## Lessons Learned from Template Development

### Key Issues Encountered and Solutions

1. **Cookiecutter Template Structure**
   - **Problem**: `NonTemplatedInputDirException` - cookiecutter couldn't find template directories
   - **Root Cause**: Files were in repo root instead of `{{cookiecutter.repo_slug}}/` directory
   - **Solution**: Move all project files into `{{cookiecutter.repo_slug}}/` directory
   - **Lesson**: Cookiecutter requires specific directory structure with templated folder name

2. **dbt Jinja Template Conflicts**  
   - **Problem**: `'ref' is undefined` - cookiecutter tried to process dbt's `{{ ref() }}` syntax
   - **Root Cause**: Both cookiecutter and dbt use `{{ }}` syntax, causing conflicts
   - **Solution**: Escape dbt syntax with `{% raw %}{{ ref('model') }}{% endraw %}`
   - **Lesson**: Always escape nested template languages when using cookiecutter

3. **Missing Environment Variables**
   - **Problem**: `airflow-init` failed with missing `_AIRFLOW_WWW_USER_USERNAME` and `_AIRFLOW_WWW_USER_PASSWORD`
   - **Root Cause**: `post_gen_project.py` didn't generate required Airflow admin credentials  
   - **Solution**: Add missing variables to the .env generation in post-generation hook
   - **Lesson**: Ensure all environment dependencies are documented and generated

4. **Docker Compose Command Parsing**
   - **Problem**: Complex bash commands in `command:` field being parsed as individual arguments
   - **Root Cause**: YAML multiline syntax and entrypoint/command interaction
   - **Multiple attempts**: `command: >`, `command: |`, `command: "string"`, `command: ["sh", "-c", "..."]`
   - **Working solution**: `entrypoint: ["sh", "-c"]` + `command: "single string"`
   - **Lesson**: Docker Compose YAML syntax is very specific about string vs array parsing

5. **File Modification Detection Issues**
   - **Problem**: Edit tool failing with "file has been modified" errors
   - **Root Cause**: Auto-formatters (likely Ruff) modifying files between Read and Edit operations  
   - **Solution**: Use bash commands (`sed`, `cat >>`, `echo >>`) instead of Edit tool
   - **Lesson**: Document workarounds for auto-formatter interference

6. **Environment-Specific Testing Challenges**
   - **Problem**: Different behavior between Docker Desktop vs Podman, snap confinement issues
   - **Root Cause**: Testing environment didn't match user environment
   - **Solution**: Test with actual tools user will use (devcontainer CLI, not just docker-compose)
   - **Lesson**: Always test in the target environment, not just isolated components

### Development Workflow Insights

- **Test iteratively**: Don't assume fixes work - validate each change end-to-end
- **Document as you go**: File editing workarounds, YAML syntax gotchas, etc.
- **Environment matters**: Snap packages, Podman vs Docker, auto-formatters all affect behavior
- **Template complexity**: Multiple template engines (cookiecutter + dbt) require careful escaping
- **Dependencies cascade**: Missing env vars cause container failures which cause devcontainer failures