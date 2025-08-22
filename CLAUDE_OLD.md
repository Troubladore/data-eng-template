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
---

## ChatGPT Collaboration Workflow

Claude now has access to a ChatGPT Browser MCP that provides comprehensive tools for collaborating with ChatGPT during development. This establishes a new workflow for complex tasks:

### Available ChatGPT Tools

The following MCP tools are available for ChatGPT interaction:

1. **Core Messaging Tools**
   - `run_chatgpt(message)` - Send a new message to ChatGPT 
   - `send_new_message(message)` - Equivalent to run_chatgpt for new conversations

2. **Conversation Management**
   - `find_conversation(chat_name, project_name?)` - Find existing conversation by name
   - `continue_conversation(chat_name, message, project_name?)` - Add message to existing chat
   - `list_conversations(project_name?)` - List available conversations
   - `get_conversation_content(chat_name, project_name?, limit?)` - Retrieve chat content

3. **Project Organization**
   - `list_projects(include_temporary?)` - List ChatGPT project folders
   - `create_project_folder(project_name, temporary?)` - Create new project folder
   - `navigate_to_project(project_name)` - Switch to project context
   - `list_project_contents(project_name)` - List conversations in project

4. **Chat Creation and Modes**
   - `create_temporary_chat(message, title?)` - Create non-persistent chat
   - `create_persistent_chat(message, title?, project_name?)` - Create saved chat
   - `detect_current_chat_mode()` - Check if in temporary/persistent mode

5. **Design Discussion Support**
   - `get_design_discussion_summary(chat_name, project_name?)` - Get institutional knowledge
   - `list_design_discussions(project_name?)` - Find design/technical discussions

6. **Development Utilities**
   - `cleanup_test_artifacts(identifier_prefix?)` - Clean up test conversations
   - Navigation and context management for complex workflows

### New Development Workflow

For complex development tasks, Claude should follow this enhanced workflow:

#### 1. Initial Design Phase
When tasked with implementing a feature or solving a complex problem:

```
1. Create a design discussion with ChatGPT to gather requirements and ideas
2. Use ChatGPT's knowledge for architectural decisions and best practices
3. Collaborate on technical approach and potential gotchas
4. Get feedback on implementation strategy
```

**Example Usage:**
```bash
# Create design discussion for new feature
create_persistent_chat("I'm implementing a new data pipeline validation system for Airflow. What are the key architectural considerations and best practices I should follow?", "Data Pipeline Validation Design", "data-eng-template")
```

#### 2. Technical Specification Phase
After initial design collaboration:

```
1. Develop detailed technical specifications based on ChatGPT insights
2. Review the tech spec with ChatGPT for completeness and feasibility
3. Identify implementation phases for agile development
4. Plan testing and validation strategies
```

#### 3. Implementation Phase
During actual coding:

```
1. Begin step-by-step implementation using the approved tech spec
2. Consult ChatGPT when encountering complex problems or design decisions
3. Seek code review feedback from ChatGPT for critical components
4. Use ChatGPT for troubleshooting difficult bugs or integration issues
```

#### 4. Code Quality Assurance
Before completing work:

```
1. Have ChatGPT review code for style, security, and best practices
2. Get suggestions for additional test cases or edge case handling
3. Review documentation and comments for clarity
4. Validate that implementation meets original design goals
```

### Integration Guidelines

#### When to Consult ChatGPT
- **Complex architectural decisions**: Database schema design, API structure
- **Technology selection**: Choosing between competing approaches or tools
- **Problem-solving**: Stuck on implementation details or debugging
- **Best practices**: Security, performance, maintainability considerations
- **Code review**: Getting fresh perspective on critical code paths

#### ChatGPT Project Organization
- Create project-specific folders for major features or architectural decisions
- Use descriptive conversation names that include context
- Maintain design discussions as institutional knowledge for the project
- Keep temporary chats for quick questions that don't need persistence

#### Collaboration Best Practices
- **Be specific**: Provide context about the data engineering domain and tools in use
- **Share code**: Include relevant code snippets and configurations in discussions
- **Ask focused questions**: Break complex problems into specific, answerable parts
- **Document decisions**: Capture important architectural decisions in persistent chats
- **Review iteratively**: Use ChatGPT throughout development, not just at the end

### Commit Message Standards

Following the ChatGPT MCP repository's lead, use **Conventional Commits** specification:

```bash
# Format: <type>[optional scope]: <description>
# Types: feat, fix, docs, style, refactor, perf, test, chore

# Examples:
feat: add data pipeline validation with Pydantic models
fix: resolve timing issues in Airflow DAG execution
docs: update DevContainer setup instructions
refactor: modularize dbt model structure
test: add comprehensive pipeline validation tests
chore: update Python dependencies and cleanup
```

**Required commit prefixes:**
- `feat:` - New features or functionality
- `fix:` - Bug fixes  
- `docs:` - Documentation changes
- `refactor:` - Code refactoring without functionality changes
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks, dependency updates
- `perf:` - Performance improvements
- `style:` - Code formatting, linting fixes

### Example: Implementing New Feature with ChatGPT Collaboration

```bash
# Step 1: Create design discussion
create_persistent_chat("I need to implement data quality validation for our dbt models. The validation should check for null values, schema compliance, and data freshness. What's the best architecture for this in a modern data stack?", "Data Quality Validation Design", "data-eng-template")

# Step 2: Continue design conversation with specifics
continue_conversation("Data Quality Validation Design", "Our stack uses dbt Core, Postgres, and Airflow. We need validation that can run as part of our dbt runs and also as separate Airflow tasks. How should we structure this?", "data-eng-template")

# Step 3: Get implementation guidance
continue_conversation("Data Quality Validation Design", "Based on our discussion, I'm thinking of using dbt tests + Great Expectations. Can you help me create a detailed technical specification for implementing this?", "data-eng-template")

# Step 4: Review tech spec before implementation
create_temporary_chat("I've created this technical specification for data quality validation [paste spec]. Can you review it for completeness and suggest any improvements?")

# Step 5: Get help during implementation when stuck
create_temporary_chat("I'm implementing the Great Expectations integration but having trouble with the checkpoint configuration in our Docker environment. Here's my current setup: [paste code]")
```

This collaborative approach ensures:
- **Better design decisions** through ChatGPT's broad knowledge
- **Reduced implementation time** by catching issues early in design phase  
- **Higher code quality** through iterative review and feedback
- **Institutional knowledge capture** via persistent design discussions
- **Professional development practices** with conventional commits and documentation

---
