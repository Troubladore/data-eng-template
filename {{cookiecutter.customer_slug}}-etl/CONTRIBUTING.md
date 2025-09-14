# Contributing to {{cookiecutter.project_name}}

Thank you for your interest in contributing to {{cookiecutter.project_name}}! This document outlines the process for contributing to this data engineering project.

## Getting Started

1. **Fork the repository** and clone your fork locally
2. **Set up the development environment** using the DevContainer:
   ```bash
   code .  # Open in VS Code
   # Click "Reopen in Container" when prompted
   ```
3. **Verify the setup** by running tests:
   ```bash
   make test
   ```

## Development Workflow

### Making Changes

1. **Create a feature branch** from main:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the project conventions:
   - Use the Hydra configuration system for new settings
   - Follow the medallion architecture (Bronze → Silver → Gold)
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**:
   ```bash
   # Run all tests
   make test
   
   # Run specific test suites
   python -m pytest tests/unit/
   python -m pytest tests/integration/
   
   # Test pipeline with your changes
   python scripts/run_pipeline.py runtime.dry_run=true
   ```

4. **Ensure code quality**:
   ```bash
   # Format code with ruff
   ruff format .
   
   # Check for linting issues  
   ruff check .
   ```

### Configuration Changes

When adding new configuration options:

1. **Add to Hydra configs** in the appropriate `conf/` subdirectory
2. **Update Pydantic models** in `src/*/config/settings.py`
3. **Document the new option** with inline comments and type hints
4. **Add validation tests** in `tests/test_config.py`

Example:
```yaml
# conf/my_feature/settings.yaml
my_new_setting:
  enabled: true  # Enable the new feature
  threshold: 100  # Processing threshold (must be > 0)
```

```python
# settings.py
class MyFeatureSettings(BaseModel):
    enabled: bool = Field(True, description="Enable the new feature")
    threshold: int = Field(100, description="Processing threshold", gt=0)
```

### Data Model Changes

When adding new dbt models or transformations:

1. **Follow medallion architecture** - place models in appropriate layer
2. **Add model documentation** in `models/schema.yml`
3. **Include data quality tests** using dbt testing framework
4. **Update pipeline documentation** if the data flow changes

### Documentation

- **Update relevant documentation** for any changes
- **Follow GitHub-native Markdown** conventions
- **Test documentation links** before submitting
- **Add inline code documentation** for complex logic

## Coding Standards

### Python Code

- **Use type hints** for all function parameters and returns
- **Follow PEP 8** style guidelines (enforced by ruff)
- **Write docstrings** for classes and complex functions
- **Use meaningful variable and function names**

### SQL Code (dbt)

- **Use consistent formatting** with 2-space indentation
- **Include model documentation** describing purpose and key fields
- **Add data quality tests** for critical models
- **Use descriptive CTE names** in complex queries

### Configuration

- **Use Hydra configuration** instead of hardcoded values
- **Include inline documentation** for all config options
- **Provide sensible defaults** that work in development
- **Use environment-specific overrides** for production settings

## Testing

### Test Requirements

All contributions must include appropriate tests:

- **Unit tests** for individual functions and classes
- **Integration tests** for end-to-end workflows
- **Configuration tests** to ensure settings work correctly
- **Documentation tests** to verify links and structure

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test types
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v

# Test configuration changes
python scripts/run_pipeline.py runtime.dry_run=true
```

## Pull Request Process

1. **Ensure tests pass** and code follows style guidelines
2. **Update documentation** for any user-facing changes
3. **Write a clear PR description** explaining:
   - What changes were made and why
   - How to test the changes
   - Any breaking changes or migration requirements
4. **Link related issues** if applicable
5. **Request review** from project maintainers

### PR Title Format

Use conventional commit format for PR titles:
- `feat: add new pipeline feature`
- `fix: resolve configuration loading issue`  
- `docs: update getting started guide`
- `test: add integration tests for pipelines`

## Issue Reporting

When reporting bugs or requesting features:

1. **Search existing issues** to avoid duplicates
2. **Use issue templates** provided in the repository
3. **Include environment information**:
   - Operating system and version
   - Python version
   - Docker/DevContainer version
   - Relevant configuration settings
4. **Provide reproduction steps** for bugs
5. **Include logs and error messages** if applicable

## Code Review Guidelines

### For Contributors

- **Respond promptly** to review feedback
- **Ask questions** if feedback is unclear
- **Make requested changes** in separate commits for clarity
- **Test thoroughly** after making review changes

### For Reviewers

- **Be constructive** and helpful in feedback
- **Focus on code quality**, not personal preferences
- **Suggest improvements** with examples where helpful
- **Approve when ready** and tests are passing

## Development Environment

### DevContainer Features

The project includes a comprehensive DevContainer with:
- Python {{cookiecutter.python_version}} with all dependencies
- PostgreSQL database for development
- Airflow webserver and scheduler
- All development tools pre-configured

### Manual Setup (Alternative)

If you prefer not to use DevContainers:
```bash
# Install dependencies
uv sync

# Start services
docker-compose -f .devcontainer/compose.yaml up -d

# Generate environment variables
./scripts/export_env.sh > .env
```

## Questions or Help

- **Check the documentation** in the `docs/` directory first
- **Look at existing issues** and discussions
- **Ask questions** in issue comments or discussions
- **Reach out to maintainers** for major changes or questions

## Recognition

Contributors will be acknowledged in:
- Release notes for significant contributions
- README contributor section
- Project documentation where relevant

Thank you for contributing to {{cookiecutter.project_name}}!