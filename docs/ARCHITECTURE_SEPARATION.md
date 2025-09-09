# Architecture: Separation of Concerns

## 🎯 **Problem Statement**
Our data engineering ecosystem has grown to encompass multiple concerns that should be cleanly separated:

1. **Template Generation** (cookiecutter)
2. **Workstation Optimization** (Docker caching, WSL2 setup)
3. **Service Orchestration** (dev services management)
4. **Template Testing** (validation, CI/CD)

## 🏗️ **Recommended Repository Structure**

### **1. `data-eng-template` (THIS REPO)**
**Purpose**: Pure cookiecutter template for data engineering projects
**Responsibilities**:
- ✅ Cookiecutter template structure and variables
- ✅ Generated project scaffolding (DAGs, configs, docs)
- ✅ Template-specific tests (generation, file structure)
- ✅ Template documentation and usage examples

**Should NOT contain**:
- ❌ Workstation setup scripts
- ❌ Docker caching systems  
- ❌ Development environment orchestration
- ❌ Cross-repo performance optimization

**Clean Up Required**:
```bash
# Move these to appropriate repos:
tests/docker/fingerprint.py        → data-eng-workstation-tools
tests/helpers/cleanup.py           → data-eng-workstation-tools  
docs/WORKSTATION_SETUP.md          → data-eng-workstation-tools
scripts/verify-test-cleanup.sh     → data-eng-workstation-tools
```

### **2. `devcontainer-service-manager` (EXISTING REPO)**
**Purpose**: Development service orchestration and management
**Responsibilities**:
- ✅ Service lifecycle management (start/stop/health)
- ✅ Port conflict resolution and allocation
- ✅ Cross-project service reuse
- ✅ DevContainer integration hooks
- 🔄 **Evolution**: Modernize for Docker (currently podman-focused)

**Modern Enhancement Needed**:
```yaml
# Evolution from podman → Docker + modern caching
services:
  airflow:
    image: "project-airflow:cached"  # Uses fingerprinted caching
    cache_strategy: "fingerprint"    # New feature
    depends_on: ["postgres"]
```

### **3. `data-eng-workstation-tools` (NEW REPO)**
**Purpose**: Developer workstation optimization and tooling
**Responsibilities**:
- ✅ Docker build caching and optimization
- ✅ WSL2 setup and configuration
- ✅ Cross-repo performance tooling
- ✅ Developer onboarding automation
- ✅ Workstation health monitoring

**Key Components**:
```
data-eng-workstation-tools/
├── setup/
│   ├── install-workstation.sh     # One-time setup
│   ├── wsl2-optimization.sh       # WSL2-specific config
│   └── docker-optimization.sh     # Docker performance tuning
├── caching/
│   ├── fingerprint.py             # Moved from template repo
│   ├── registry-manager.py        # Local registry management
│   └── cache-cleanup.py           # Cache maintenance
├── health/
│   ├── verify-setup.sh            # Performance validation
│   └── troubleshoot.py            # Common issue resolution
└── integration/
    ├── template-integration/       # Hooks for templates
    └── service-integration/        # Hooks for service manager
```

### **4. `data-eng-template-tests` (NEW REPO - Optional)**
**Purpose**: Comprehensive testing of generated projects
**Responsibilities**:
- ✅ End-to-end validation of generated projects
- ✅ Performance regression testing
- ✅ Cross-platform compatibility testing (WSL2, macOS, Linux)
- ✅ Template ecosystem integration testing

## 🔄 **Migration Plan**

### **Phase 1: Extract Workstation Tools (Immediate)**
```bash
# Create new repo
git clone --bare data-eng-template data-eng-workstation-tools.git
cd data-eng-workstation-tools.git
git push --mirror https://github.com/your-org/data-eng-workstation-tools.git

# Clean up - keep only workstation-related code
# Remove template-specific code, keep only:
# - Docker caching system
# - Workstation setup scripts
# - Performance optimization tools
```

### **Phase 2: Modernize Service Manager (Next Sprint)**
```bash
cd devcontainer-service-manager

# Add Docker support (currently podman-focused)
# Integrate with fingerprint caching system
# Add modern service templates (Airflow 3.0.6, etc.)
# Update to work with new architecture
```

### **Phase 3: Clean Template Repo (Final)**
```bash
cd data-eng-template

# Remove workstation concerns:
rm -rf tests/docker/fingerprint.py
rm -rf tests/helpers/cleanup.py  
rm -rf docs/WORKSTATION_SETUP.md
rm -rf scripts/verify-test-cleanup.sh

# Keep only template concerns:
# - cookiecutter.json and template structure
# - Template generation tests
# - Generated project structure
# - Template documentation
```

## 🔗 **Integration Points**

### **Template → Workstation Tools**
```bash
# In generated project
./scripts/setup-development.sh
# This script calls: data-eng-workstation-tools setup
```

### **Workstation Tools → Service Manager**  
```bash
# Workstation tools configure service manager
dcm configure --cache-strategy fingerprint
dcm template install --from data-eng-templates
```

### **Service Manager → Generated Projects**
```yaml
# .devcontainer/devcontainer.json (in generated projects)
{
  "name": "My Data Project", 
  "initializeCommand": "dcm up --config .devcontainer/services.yaml",
  "shutdownAction": "dcm suspend"
}
```

## 🎯 **Benefits of Separation**

### **For Template Users**:
- ✅ **Clean template focus**: Just cookiecutter concerns
- ✅ **Optional optimization**: Can use workstation tools if desired  
- ✅ **Modular adoption**: Pick and choose tools needed

### **For Developers**:
- ✅ **Clear ownership**: Each repo has single responsibility
- ✅ **Independent evolution**: Tools can evolve without breaking templates
- ✅ **Easier testing**: Each component tested in isolation

### **For Maintenance**:
- ✅ **Focused PRs**: Changes go to appropriate repo
- ✅ **Clear issues**: Bug reports go to right place
- ✅ **Independent releases**: Tools and templates version separately

## 🚀 **Implementation Priority**

### **High Priority** (This Week):
1. **Extract workstation tools** to separate repo
2. **Clean up template repo** to pure cookiecutter focus
3. **Update generated projects** to reference external tools

### **Medium Priority** (Next Sprint):
1. **Modernize service manager** for Docker + caching
2. **Create integration scripts** between components
3. **Document new architecture** for users

### **Low Priority** (Future):
1. **Consider separate test repo** if testing becomes complex
2. **Add CI/CD integration** between repos
3. **Create meta-installer** for full ecosystem

## 📋 **Decision Criteria**

**Use Separate Repo When**:
- ✅ Different update cadence (templates vs tools)
- ✅ Different user audience (template users vs workstation optimizers)  
- ✅ Independent versioning needed
- ✅ Significantly different dependencies

**Keep in Same Repo When**:
- ✅ Tightly coupled functionality
- ✅ Same maintenance team
- ✅ Always used together
- ✅ Simple, focused scope

## 🎉 **End State Vision**

```bash
# New developer setup:
curl -sSL install.data-eng-tools.com | bash  # Workstation optimization

# Create new project:
cookiecutter gh:your-org/data-eng-template   # Pure template

# Generated project automatically integrates:
dcm up                                        # Service management
./scripts/build.sh --fast                    # Uses caching tools
```

**Result**: Clean separation, optimal performance, easy maintenance! 🚀