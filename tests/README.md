# Testing Strategy for Data Engineering Template

This testing suite ensures the cookiecutter template works reliably for data engineering teams across all scenarios.

## 🎯 Test Philosophy

- **Mission Critical**: Template failure blocks entire data engineering teams
- **Comprehensive Coverage**: From lightweight smoke tests to full infrastructure validation  
- **Remote Testing**: Heavy tests use remote branches, not work-in-progress code
- **Isolation**: Tests clean up completely to avoid interference
- **Fast Feedback**: Quick tests for development, comprehensive tests for CI/CD

## 🏗️ Test Architecture

### **Tier 1: Lightning Fast (< 10 seconds)**
```bash
pytest -m "unit or smoke" --maxfail=1
```

**Purpose**: Immediate feedback during development
- Template syntax validation
- Cookiecutter variable validation
- File structure verification  
- Documentation consistency checks
- No Docker, no network calls

### **Tier 2: Integration (< 2 minutes)**
```bash
pytest -m "integration and not slow"
```

**Purpose**: Verify template generation and basic functionality
- Template generation with all variable combinations
- Generated project structure validation
- DevContainer configuration validation
- Multiple project generation (port conflict detection)
- Service configuration verification

### **Tier 3: End-to-End (< 10 minutes)**
```bash  
pytest -m "e2e"
```

**Purpose**: Full workflow validation with real services
- DevContainer startup and service validation
- Astronomer CLI integration testing
- Database connectivity and schema validation
- Airflow UI accessibility and DAG loading
- Cross-project isolation verification

### **Tier 4: Stress & Recovery (< 30 minutes)**
```bash
pytest -m "stress"
```

**Purpose**: Extreme scenarios and recovery testing
- Clean slate testing (all Docker artifacts removed)
- Resource exhaustion scenarios
- Network partition simulation
- Concurrent project generation
- Full system recovery verification

### **Tier 5: Remote Branch Testing (CI Only)**
```bash
pytest -m "remote" --remote-branch=main
```

**Purpose**: Test against published versions, not work-in-progress
- Uses cookiecutter from GitHub URLs
- Tests actual user experience
- Validates published documentation
- Prevents work-in-progress disruption

## 🚀 Test Execution

### **Development Workflow**
```bash
# Quick validation while working
make test-fast

# Before committing  
make test-integration

# Full local validation (rare)
make test-all
```

### **CI/CD Pipeline**
```bash
# PR validation
pytest -m "unit or integration" 

# Main branch validation
pytest -m "unit or integration or e2e"

# Nightly comprehensive testing
pytest -m "stress or remote"
```

## 📁 Test Organization

```
tests/
├── unit/                    # Tier 1: Lightning fast
│   ├── test_template_syntax.py
│   ├── test_cookiecutter_variables.py
│   └── test_documentation_consistency.py
├── integration/             # Tier 2: Template generation
│   ├── test_template_generation.py
│   ├── test_project_structure.py
│   ├── test_multi_project_isolation.py
│   └── test_devcontainer_config.py
├── e2e/                     # Tier 3: Full workflows
│   ├── test_devcontainer_startup.py
│   ├── test_astronomer_integration.py
│   ├── test_airflow_workflows.py
│   └── test_database_integration.py
├── stress/                  # Tier 4: Extreme scenarios
│   ├── test_clean_slate_generation.py
│   ├── test_concurrent_projects.py
│   └── test_resource_exhaustion.py
└── remote/                  # Tier 5: Remote testing
    ├── test_published_template.py
    └── test_user_experience.py
```

## 🛠️ Test Infrastructure

### **Docker Management**
- Each test uses isolated Docker contexts
- Automatic cleanup with pytest fixtures
- Network namespace isolation for multi-project tests
- Resource monitoring and cleanup validation

### **Temporary Directory Strategy**  
- Each test gets isolated temp directory
- Automatic cleanup with proper error handling
- Shared fixtures for common scenarios
- Artifact preservation for debugging

### **Remote Testing Strategy**
```python
@pytest.fixture  
def remote_template_url():
    """Use GitHub URL for remote testing, local path for development."""
    if os.getenv('PYTEST_REMOTE_BRANCH'):
        branch = os.getenv('PYTEST_REMOTE_BRANCH', 'main')
        return f"https://github.com/Troubladore/data-eng-template.git@{branch}"
    return str(Path(__file__).parent.parent)
```

## 📊 Test Metrics & Monitoring

- **Success Rate**: Track test success over time
- **Performance**: Monitor test execution time trends  
- **Coverage**: Ensure all template features tested
- **Resource Usage**: Track Docker resource consumption
- **Cleanup Verification**: Ensure no test pollution

## 🏃 Quick Commands

```bash
# Development
make test-fast              # < 10 seconds
make test-dev               # < 2 minutes  
make test-local            # < 10 minutes (full local)

# CI/CD  
make test-pr               # PR validation
make test-main            # Main branch validation
make test-nightly         # Comprehensive nightly testing

# Debugging
make test-debug           # Verbose output, artifact preservation
make test-clean           # Clean all Docker artifacts first
make test-remote          # Test against published template
```

This strategy ensures **mission-critical reliability** while providing **fast developer feedback** and preventing work-in-progress disruption through smart remote testing.