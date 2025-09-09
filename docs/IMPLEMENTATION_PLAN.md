# Repository Migration Implementation Plan

**Date**: 2025-01-09  
**Objective**: Migrate workstation optimization tools to `devcontainer-service-manager` while maintaining clean separation of concerns

## 🎯 **Migration Overview**

This migration separates:
- **Template concerns** → `data-eng-template` (cookiecutter focus)
- **Development environment optimization** → `devcontainer-service-manager` (enhanced)

## 📊 **Current State Analysis**

### Files Being Migrated FROM data-eng-template:
```
tests/docker/fingerprint.py           → devcontainer-service-manager/src/devcontainer_services/caching/
tests/helpers/cleanup.py              → devcontainer-service-manager/src/devcontainer_services/caching/
scripts/verify-test-cleanup.sh        → devcontainer-service-manager/src/devcontainer_services/workstation/
docs/WORKSTATION_SETUP.md             → devcontainer-service-manager/docs/
```

### Key Performance Achievement to Preserve:
- **149x faster Docker builds** via fingerprint-based caching
- **Cross-repository cache sharing** via local Docker registry
- **Robust test cleanup** preventing resource leaks

## 🚀 **Phase 1: Enhance devcontainer-service-manager**

### Step 1.1: Update Repository Structure
```
devcontainer-service-manager/
├── src/devcontainer_services/
│   ├── core/              # Existing service orchestration
│   ├── caching/           # NEW: Docker build optimization
│   │   ├── __init__.py
│   │   ├── fingerprint.py # Moved from data-eng-template
│   │   ├── cleanup.py     # Moved from data-eng-template
│   │   └── cli.py         # NEW: dcm-cache command
│   ├── workstation/       # NEW: Workstation setup
│   │   ├── __init__.py
│   │   ├── setup.py       # WSL2 optimization
│   │   ├── health.py      # Performance validation
│   │   └── cli.py         # NEW: dcm-setup command
│   └── templates/         # Enhanced with caching support
```

### Step 1.2: Add New CLI Commands
```bash
# Enhanced pyproject.toml
[project.scripts]
dcm = "devcontainer_services.cli:main"           # Existing
dcm-cache = "devcontainer_services.caching.cli:main"    # NEW
dcm-setup = "devcontainer_services.workstation.cli:main" # NEW
```

### Step 1.3: Update Description and Scope
```python
# pyproject.toml
description = "Development environment optimization: service orchestration, Docker caching, and workstation setup"
```

## 🔄 **Phase 2: Update data-eng-template**

### Step 2.1: Remove Workstation Files
```bash
git rm tests/docker/fingerprint.py
git rm tests/helpers/cleanup.py  
git rm scripts/verify-test-cleanup.sh
git rm docs/WORKSTATION_SETUP.md
```

### Step 2.2: Update Generated Projects
Update `{{cookiecutter.repo_slug}}/scripts/setup-development.sh`:
```bash
#!/bin/bash
# Development environment setup - calls external tooling

# Install enhanced service manager
pip install devcontainer-service-manager[workstation]

# Setup optimized workstation  
dcm-setup install --profile data-engineering

# Configure project-specific caching
dcm-cache configure --project {{cookiecutter.repo_slug}}

# Start services with optimization
dcm up --config .devcontainer/services.yaml
```

### Step 2.3: Update Template Documentation
Reference external tooling in generated project READMEs.

## 🧪 **Phase 3: Testing Strategy**

### Step 3.1: Service Manager Testing
```bash
cd ~/repos/devcontainer-service-manager
# Test new caching features
dcm-cache status
dcm-setup validate
```

### Step 3.2: Template Integration Testing  
```bash
cd ~/repos/data-eng-template
# Generate test project
cookiecutter . --no-input --output-dir ~/repos/tmp
cd ~/repos/tmp/test-data-project

# Test setup script calls external tooling
./scripts/setup-development.sh
```

### Step 3.3: WSL2 Validation
- Test local Docker registry startup
- Validate file system performance (WSL2 vs /mnt/c/)
- Test DevContainer integration

## 📋 **Success Criteria**

### ✅ Enhanced Service Manager:
- [ ] Caching system preserves 149x performance improvement
- [ ] New CLI commands work: `dcm-cache`, `dcm-setup`  
- [ ] WSL2 compatibility validated
- [ ] Cross-repo cache sharing functional

### ✅ Clean Template Repo:
- [ ] No workstation optimization files remain
- [ ] Generated projects reference external tooling
- [ ] Template generation and tests pass
- [ ] Integration with enhanced service manager works

### ✅ Developer Experience:
- [ ] One command setup: `pip install devcontainer-service-manager`
- [ ] Generated projects start with cached builds
- [ ] Documentation clear for WSL2 users

## 🐛 **Risk Mitigation**

### Backup Strategy:
- All changes committed to branches before merging
- Test migration on copy of repos first
- Keep original migration files until validation complete

### Rollback Plan:
- Service manager enhancements are additive (won't break existing functionality)
- Template changes can be reverted via git
- Performance improvements preserved in both scenarios

## 📚 **Documentation Updates Required**

### In devcontainer-service-manager:
- [ ] Update README.md with new capabilities
- [ ] Add WSL2 setup guide
- [ ] Document new CLI commands
- [ ] Add troubleshooting section

### In data-eng-template:
- [ ] Update main README to reference external tooling
- [ ] Update generated project documentation
- [ ] Remove workstation setup references

## 🎉 **Expected End State**

### Developer Workflow:
```bash
# One-time setup
pip install devcontainer-service-manager
dcm-setup install --profile data-engineering

# Create project
cookiecutter gh:your-org/data-eng-template

# Generated project benefits from optimization
cd my-new-project  
dcm up  # Fast cached builds automatically
```

### Repository Clarity:
- **data-eng-template**: Pure cookiecutter template, focused and maintainable
- **devcontainer-service-manager**: Comprehensive development environment optimization
- **Generated projects**: Reference external tooling, stay focused on domain logic

---

**Next Steps**: Begin Phase 1 implementation with enhanced service manager structure.