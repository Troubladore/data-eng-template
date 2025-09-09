# Migration Plan: Repository Separation

## 🎯 **Immediate Recommendation**

**Extract workstation optimization tools** into a dedicated repository, leveraging your existing `devcontainer-service-manager` as the foundation for development tooling.

## 📊 **Repository Responsibilities (Final State)**

| Repository | Purpose | Key Components | User Audience |
|------------|---------|---------------|---------------|
| **`data-eng-template`** | Pure cookiecutter template | Template files, generation logic, basic tests | Data engineers creating new projects |
| **`devcontainer-service-manager`** | Development service orchestration + workstation optimization | Service management, Docker caching, WSL2 setup | Developers optimizing their workstation |

## 🚀 **Phase 1: Quick Win (This Week)**

### **Step 1: Enhance `devcontainer-service-manager`**
```bash
cd ~/repos/devcontainer-service-manager

# Add workstation optimization features:
mkdir -p src/devcontainer_services/{caching,workstation,optimization}

# Move from data-eng-template:
cp ~/repos/data-eng-template/tests/docker/fingerprint.py src/devcontainer_services/caching/
cp ~/repos/data-eng-template/tests/helpers/cleanup.py src/devcontainer_services/caching/
cp ~/repos/data-eng-template/scripts/verify-test-cleanup.sh src/devcontainer_services/workstation/
```

### **Step 2: Update `devcontainer-service-manager` Scope**
```python
# pyproject.toml - expand description
description = "Development environment optimization: service orchestration, Docker caching, and workstation setup for data engineering"

# Add new CLI commands:
[project.scripts]
dcm = "devcontainer_services.cli:main"
dcm-cache = "devcontainer_services.caching.cli:main"       # New
dcm-setup = "devcontainer_services.workstation.cli:main"  # New
```

### **Step 3: Clean Up Template Repo**
```bash
cd ~/repos/data-eng-template

# Remove workstation concerns (after copying to service-manager):
git rm tests/docker/fingerprint.py
git rm tests/helpers/cleanup.py  
git rm scripts/verify-test-cleanup.sh
git rm docs/WORKSTATION_SETUP.md

# Update generated projects to reference external tooling:
# Update {{cookiecutter.repo_slug}}/scripts/smart-build.sh to call dcm-cache
# Update template documentation to reference dcm setup
```

## 🔄 **Phase 2: Integration (Next Sprint)**

### **Update Generated Projects**
Template generates projects that integrate with enhanced service manager:

```yaml
# {{cookiecutter.repo_slug}}/.devcontainer/services.yaml
namespace: "{{cookiecutter.repo_slug}}"
cache_strategy: "fingerprint"  # New feature in service manager

services:
  postgres:
    template: "postgres:{{cookiecutter.postgres_version}}"
    persistent: true
    cache_enabled: true  # New feature
    
  airflow:
    template: "airflow:{{cookiecutter.airflow_version}}"  
    depends_on: ["postgres"]
    cache_enabled: true  # New feature
    build_optimization: "fingerprint"  # New feature
```

### **Workstation Setup Integration**  
```bash
# Generated in {{cookiecutter.repo_slug}}/scripts/setup-development.sh
#!/bin/bash
# Development environment setup

# Install/update service manager with workstation tools
pip install devcontainer-service-manager[workstation]

# Setup optimized workstation
dcm-setup install --profile data-engineering

# Configure caching for this project  
dcm-cache configure --project {{cookiecutter.repo_slug}}

# Start optimized services
dcm up --config .devcontainer/services.yaml
```

## 💡 **Why This Approach?**

### **Benefits of Enhancing Existing Repo**:
1. **Leverage existing foundation** - `devcontainer-service-manager` already has service orchestration
2. **Natural evolution** - Extends service management to include workstation optimization  
3. **Single tool** - Developers install one tool (`dcm`) for all dev environment needs
4. **Proven architecture** - Your existing service manager has good structure

### **Clean Separation Achieved**:
- **Template repo**: Pure cookiecutter concerns
- **Service manager repo**: All development environment optimization
- **Generated projects**: Reference external tooling, stay focused

## 🛠️ **Implementation Details**

### **Enhanced `devcontainer-service-manager` Structure**:
```
devcontainer-service-manager/
├── src/devcontainer_services/
│   ├── core/              # Original service orchestration
│   │   ├── service.py
│   │   └── templates.py
│   ├── caching/           # NEW: Docker build optimization
│   │   ├── fingerprint.py # Moved from template repo
│   │   ├── registry.py    # Local registry management
│   │   └── cli.py         # dcm-cache command
│   ├── workstation/       # NEW: Workstation setup
│   │   ├── setup.py       # WSL2, Docker optimization
│   │   ├── health.py      # Performance validation
│   │   └── cli.py         # dcm-setup command
│   └── templates/         # Enhanced with caching
│       ├── airflow.yaml   # Now supports build caching
│       └── postgres.yaml
```

### **New CLI Commands**:
```bash
# Original service management
dcm up --config services.yaml
dcm status
dcm down

# NEW: Workstation optimization
dcm-setup install                    # One-time workstation setup
dcm-setup validate                   # Check performance setup
dcm-setup troubleshoot              # Fix common issues

# NEW: Build caching
dcm-cache status                     # Show cache statistics
dcm-cache clean --older-than 7d     # Cleanup old cached images
dcm-cache optimize                   # Pre-build common images
```

## 📋 **Action Items**

### **Immediate (This Week)**:
- [ ] Enhance `devcontainer-service-manager` with caching and workstation features
- [ ] Move workstation code from template repo to service manager
- [ ] Update template to reference external tooling
- [ ] Test integration between repos

### **Next Sprint**:  
- [ ] Add WSL2 optimization features to service manager
- [ ] Create integration tests between template and service manager
- [ ] Update documentation to reflect new architecture
- [ ] Add CI/CD for service manager enhancements

### **Future**:
- [ ] Consider creating installer/meta-package for easy setup
- [ ] Add telemetry to understand which optimizations help most
- [ ] Create performance benchmarking suite

## 🎉 **Expected Outcome**

**Developer Experience**:
```bash
# New developer (one-time setup):
pip install devcontainer-service-manager
dcm-setup install --profile data-engineering

# Create new project:
cookiecutter gh:your-org/data-eng-template

# Generated project works optimally:
cd my-new-project
dcm up  # Fast cached builds + optimized services
```

**Result**: 
- ✅ **Clean template focus** - cookiecutter does cookiecutter things
- ✅ **Comprehensive dev tooling** - service manager handles all optimization  
- ✅ **Optimal performance** - 149x faster builds + smart service management
- ✅ **Easy maintenance** - clear ownership and responsibilities

This approach leverages your existing investment in `devcontainer-service-manager` while achieving clean separation of concerns! 🚀