# Organizational Setup Guide

## 🎯 **Before Your First Project: Optimize for Team Success**

**Critical**: Complete this setup **before generating your first project** to ensure optimal caching, consistent team workflows, and long-term maintainability.

## 🏢 **Step 1: Clone and Configure Template for Your Organization**

### **1.1: Fork or Clone the Template**

Choose your persistence strategy:

#### **Option A: Private Fork (Recommended)**
```bash
# Fork https://github.com/Troubladore/data-eng-template to your organization
# Then clone your fork
git clone https://github.com/your-org/data-eng-template.git
cd data-eng-template

# Create your organization's configuration branch
git checkout -b your-org-config
```

**Benefits**:
- ✅ Persists across template updates
- ✅ Version controlled organizational standards
- ✅ Can merge upstream updates while keeping customizations

#### **Option B: Local Clone with Git Ignore**
```bash
git clone https://github.com/Troubladore/data-eng-template.git
cd data-eng-template

# Your customizations will be git-ignored (see .gitignore section below)
```

**Benefits**:
- ✅ Simpler workflow
- ❌ Customizations not version controlled
- ❌ Manual backup required

### **1.2: Create Your Organization's Configuration**

```bash
# Copy the template defaults
cp company-template-defaults.yaml your-org-defaults.yaml
```

## 🔧 **Step 2: Guided Configuration Optimization**

Edit `your-org-defaults.yaml` with your organization's standards:

### **2.1: Critical Caching Settings**
```yaml
default_context:
  # STANDARDIZE THESE across ALL team projects for optimal caching
  python_version: "3.12"           # ⚡ Critical: Same version = shared base layers
  airflow_version: "3.0.6"         # ⚡ Critical: Stable version for team consistency
  postgres_version: "16"           # ⚡ Medium: Database container layers
  runtime_tag: "3.0-10"           # ⚡ Critical: Must match airflow_version exactly
```

**Why this matters**: Teams using different versions rebuild all Docker layers from scratch, wasting hours of build time daily.

### **2.2: Container Registry Configuration**
```yaml
default_context:
  # UPDATE with your organization's container registry
  image_repo: "your-registry.company.com/data-eng/{{ cookiecutter.customer_slug }}"

  # Examples:
  # Azure: "yourregistry.azurecr.io/data-eng/{{ cookiecutter.customer_slug }}"
  # AWS: "123456789.dkr.ecr.us-east-1.amazonaws.com/data-eng/{{ cookiecutter.customer_slug }}"
  # GCP: "gcr.io/your-project/data-eng/{{ cookiecutter.customer_slug }}"
  # Docker Hub: "yourorg/{{ cookiecutter.customer_slug }}-etl"
```

**Registry Access Setup**:
```bash
# Ensure all team members can push/pull
# Azure
az acr login --name yourregistry

# AWS
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# GCP
gcloud auth configure-docker
```

### **2.3: Security and Enterprise Settings**
```yaml
default_context:
  # CUSTOMIZE for your organization's security requirements
  secrets_strategy: "azure-key-vault"    # azure-key-vault | external-secrets-operator | env-vars
  executor: "KubernetesExecutor"         # KubernetesExecutor | CeleryExecutor | LocalExecutor
  enable_kerberos: "yes"                 # yes | no (if your org uses Kerberos)

  # UPDATE with your organization details
  author_name: "Your Data Engineering Team"
  company_domain: "yourcompany.com"
  high_label: "sensitive"                # Your organization's security classification
  license: "Proprietary"                 # Proprietary | MIT | Apache-2.0
```

### **2.4: Test Your Configuration**
```bash
# Generate a test project to validate your settings
cookiecutter . --config-file your-org-defaults.yaml

# When prompted, enter:
customer_slug: test-config-validation
description: Configuration validation test project
deployment_mode: testing

# Verify the generated project has your organization's settings
cd test-config-validation-etl
grep "yourcompany.com" .devcontainer/compose.yaml
grep "your-registry.company.com" Dockerfile.airflow

# Clean up test project
cd ..
rm -rf test-config-validation-etl
```

## 📝 **Step 3: Configure Generated Project Standards**

### **3.1: Create Dependency Standards Template**

Create a template for consistent `pyproject.toml` dependencies:

```bash
# Create organizational Python standards
mkdir -p org-standards
cat > org-standards/pyproject-template.toml << 'EOF'
# Your Organization's Python Standards
[project]
dependencies = [
    # Core data stack (pinned for caching)
    "pandas==2.1.4",
    "sqlalchemy==2.0.25",
    "pyarrow==14.0.2",

    # Your organization's internal packages
    "your-company-data-lib==1.2.3",
    "your-company-auth==0.5.1",

    # Development tools (flexible versions)
    "pytest>=7.0,<8.0",
    "ruff>=0.1.0",
]

[project.optional-dependencies]
dev = [
    "jupyter>=1.0.0",
    "ipython>=8.0.0",
]

# Your organization's build settings
[build-system]
requires = ["hatchling>=1.21.0"]
build-backend = "hatchling.build"

[tool.ruff]
# Your organization's linting standards
line-length = 88
select = ["E", "F", "I"]

[tool.pytest.ini_options]
# Your organization's testing standards
testpaths = ["tests"]
python_files = ["test_*.py"]
EOF
```

### **3.2: Document Team Workflow**

Create team-specific instructions:

```bash
cat > org-standards/TEAM-WORKFLOW.md << 'EOF'
# Your Organization's Data Engineering Workflow

## Project Generation
Always use our organization's defaults:
```bash
cookiecutter https://github.com/your-org/data-eng-template --config-file your-org-defaults.yaml
```

## Development Standards
1. **Python Dependencies**: Follow org-standards/pyproject-template.toml
2. **Container Registry**: All images pushed to your-registry.company.com/data-eng/
3. **Security**: Use Azure Key Vault for all secrets
4. **Testing**: Minimum 80% coverage required

## Before Your First Commit
1. Run: `make lint test`
2. Verify: Container builds successfully
3. Push: Images to organization registry
EOF
```

## 🔄 **Step 4: Persistence Strategy**

### **Option A: Private Fork Workflow (Recommended)**

```bash
# Commit your organization's customizations
git add your-org-defaults.yaml org-standards/
git commit -m "Add organization-specific template configuration

- Set company container registry and security settings
- Standardize Python versions for optimal Docker caching
- Add internal dependency standards and workflow documentation
"

git push origin your-org-config

# Update .gitignore to preserve your settings
echo "# Organization-specific settings (keep these)" >> .gitignore
echo "!your-org-defaults.yaml" >> .gitignore
echo "!org-standards/" >> .gitignore
```

**Updating from upstream**:
```bash
# Periodically merge upstream improvements
git checkout your-org-config
git remote add upstream https://github.com/Troubladore/data-eng-template.git
git fetch upstream
git merge upstream/main  # or upstream/astro

# Resolve any conflicts, keeping your customizations
git push origin your-org-config
```

### **Option B: Git Ignore Workflow**

Add to `.gitignore`:
```gitignore
# Allow organization-specific overrides
!your-org-defaults.yaml
!org-standards/
```

**Manual backup required**:
```bash
# Backup your customizations
cp your-org-defaults.yaml ~/backup-org-config/
cp -r org-standards/ ~/backup-org-config/

# After updating template:
git pull origin main
cp ~/backup-org-config/your-org-defaults.yaml .
cp -r ~/backup-org-config/org-standards/ .
```

## ✅ **Step 5: Validation and Team Rollout**

### **5.1: Full Workflow Test**
```bash
# Generate a real project using your configuration
cookiecutter . --config-file your-org-defaults.yaml

# Test complete development workflow
cd your-test-project-etl/
code .  # Open in VS Code DevContainer

# In VS Code DevContainer:
# 1. Discover actual service ports: ./scripts/get-ports.sh
# 2. Verify Airflow UI loads at discovered port
# 3. Run: make test
# 4. Check build time (should be <2 minutes after first build)
# 5. Verify registry push: docker push (to your org registry)
```

### **5.2: Team Onboarding**
```bash
# Create team onboarding documentation
cat > TEAM-ONBOARDING.md << 'EOF'
# Data Engineering Template - Team Setup

## New Team Member Setup
1. Clone: https://github.com/your-org/data-eng-template
2. Check out: your-org-config branch
3. Verify: Docker and VS Code installed
4. Test: Generate sample project with your-org-defaults.yaml

## Daily Usage
```bash
# Generate new project
cookiecutter . --config-file your-org-defaults.yaml

# Answer only 3 prompts:
# - customer_slug: your-project-name
# - description: Brief project description
# - deployment_mode: production

# Everything else uses optimized organization defaults
```

## Troubleshooting
- Slow builds? Check python_version consistency across projects
- Registry errors? Verify docker login to your-registry.company.com
- Missing dependencies? Follow org-standards/pyproject-template.toml
EOF
```

## 🎉 **Success Criteria**

After completing this setup, your team should have:

- ✅ **Sub-10 second rebuilds** for code changes across all projects
- ✅ **Consistent configurations** - no more "works on my machine"
- ✅ **Streamlined project generation** - only 3 prompts per project
- ✅ **Persistent customizations** that survive template updates
- ✅ **Organization compliance** - security, registry, and dependency standards built-in

**Next**: Your team can now follow the standard [Getting Started Guide](getting-started.md) with confidence that every project will be optimized for your organization's success.