# Template Configuration Guide

## 🎯 **Understanding Configuration Impact on Caching**

Template configuration choices have **massive impact on Docker build caching efficiency**. Poor choices can mean the difference between **1-second rebuilds** and **10-minute rebuilds** for your entire team.

## 📊 **Three Classes of Configuration**

### 🚨 **Class 1: Required Settings**
*These must be answered and are unique per project*

| Setting | Description | Caching Impact |
|---------|-------------|----------------|
| `customer_slug` | Project identifier | **High**: Creates unique image tags and layer paths |
| `description` | Project summary | **None**: Only affects documentation |
| `deployment_mode` | Container naming strategy | **High**: Controls image naming patterns for isolation |

### ⚡ **Class 2: Cache-Impacting Settings**
*These directly affect Docker layer reuse across projects and team members*

| Setting | Default | Caching Impact | Recommendation |
|---------|---------|----------------|----------------|
| `python_version` | `3.12` | **Critical**: Base image layer for all containers | **Standardize across org** - switching versions breaks all cached layers |
| `airflow_version` | `3.0.6` | **Critical**: Airflow runtime base layers | **Use stable releases** - frequent updates break team caches |
| `postgres_version` | `16` | **Medium**: Database container layers | **Standardize** - version changes affect database setup layers |
| `runtime_tag` | `3.0-10` | **Critical**: Astronomer base image | **Must match airflow_version** - mismatches cause cache misses |
| `image_repo` | `registry.example.com/etl/{slug}` | **High**: Controls push/pull optimization | **Use consistent registry** across all team projects |

### 🔧 **Class 3: Other Settings**
*These have minimal or no caching impact*

| Setting | Default | Caching Impact | Notes |
|---------|---------|----------------|-------|
| `author_name` | `Data Engineering Team` | **None** | Only affects documentation |
| `company_domain` | `myco.com` | **None** | Configuration only |
| `env_name` | `dev` | **None** | Runtime configuration |
| `executor` | `KubernetesExecutor` | **None** | Runtime configuration |
| `secrets_strategy` | `azure-key-vault` | **None** | Runtime configuration |
| `enable_kerberos` | `no` | **Low** | May affect some dependency installation |
| `high_label` | `high` | **None** | Configuration only |
| `license` | `Proprietary` | **None** | Documentation only |

## 🏗️ **Caching Architecture Deep Dive**

### **Docker Layer Caching Strategy**

```dockerfile
# Layer 1: Base OS (shared across ALL projects)
FROM registry.astronomer.io/ap-airflow:${AIRFLOW_VERSION}

# Layer 2: Python version setup (shared if python_version matches)
RUN apt-get update && apt-get install python${PYTHON_VERSION}

# Layer 3: Common dependencies (shared if versions align)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Layer 4: Project-specific code (unique per customer_slug)
COPY dags/ /opt/airflow/dags/
```

### **Critical Caching Insights**

1. **Team Standardization = Faster Builds**
   - Teams using identical `python_version` + `airflow_version` share 80% of layers
   - Different versions = everyone rebuilds from scratch

2. **Registry Strategy Matters**
   - Consistent `image_repo` patterns enable cross-project layer sharing
   - Each unique registry path creates separate cache namespaces

3. **Version Alignment is Critical**
   - `runtime_tag` must align with `airflow_version` or cache misses occur
   - Misaligned versions can add 5-10 minutes to every build

## 📝 **pyproject.toml Caching Considerations**

### **Hidden Caching Impact**

**Critical**: Your generated `pyproject.toml` dependencies directly affect Docker caching:

```toml
[project]
dependencies = [
    "pandas==2.1.4",      # Pinned versions = better caching
    "sqlalchemy>=2.0",    # Loose versions = cache invalidation
    "requests",           # No version = unpredictable caching
]
```

### **Caching Best Practices**

1. **Pin Major Dependencies**: Use exact versions for large packages (`pandas==2.1.4`)
2. **Group by Update Frequency**: Fast-changing deps separate from stable ones
3. **Team Consistency**: Same dependency versions across all team projects

### **Hydra Pre-Configuration**

Yes! You can pre-configure dependency standards via Hydra. Here's how:

**In generated projects**: `conf/development/python-dependencies.yaml`
```yaml
python:
  dependencies:
    # Pinned for caching efficiency
    core_data:
      pandas: "==2.1.4"
      sqlalchemy: "==2.0.25"
      pyarrow: "==14.0.2"

    # Flexible for development
    dev_tools:
      pytest: ">=7.0"
      ruff: ">=0.1"

    # Org standards
    company_stack:
      custom_lib: "==1.2.3"  # Your company's internal packages

# Usage in pyproject.toml generation:
# {{ hydra.compose(config_name="python-dependencies") }}
```

## 🚀 **Recommended Configuration Strategies**

### **For Organizations**

```yaml
# company-template-defaults.yaml
default_context:
  # STANDARDIZE THESE for maximum caching efficiency
  python_version: "3.12"           # Same across all projects
  airflow_version: "3.0.6"         # Stable, proven version
  postgres_version: "16"           # Latest stable
  runtime_tag: "3.0-10"           # Matches airflow_version

  # CUSTOMIZE THESE per organization
  image_repo: "acr.company.com/data-eng/{{ cookiecutter.customer_slug }}"
  author_name: "Company Data Team"
  company_domain: "company.com"
  secrets_strategy: "azure-key-vault"
```

### **For Individual Developers**

1. **Follow team standards** for cache-impacting settings
2. **Use `deployment_mode: testing`** for experimental projects
3. **Coordinate version updates** with your team
4. **Monitor build times** - sudden increases indicate cache invalidation

## ⚠️ **Common Caching Pitfalls**

### **Pitfall 1: Version Drift**
```bash
# Team Member A generates project
customer_slug: "analytics-a"
python_version: "3.12"
airflow_version: "3.0.6"

# Team Member B generates project (weeks later)
customer_slug: "analytics-b"
python_version: "3.12"
airflow_version: "3.0.7"  # ❌ Newer version breaks Member A's cache
```

### **Pitfall 2: Registry Inconsistency**
```bash
# Project A
image_repo: "registry.company.com/etl/project-a"

# Project B
image_repo: "acr.company.com/data/project-b"  # ❌ Different registry = no sharing
```

### **Pitfall 3: Loose Dependencies**
```toml
# ❌ Cache-breaking dependencies
[project]
dependencies = [
    "pandas",          # No version = random updates
    "sqlalchemy>=2.0", # Range = frequent cache misses
]

# ✅ Cache-friendly dependencies
[project]
dependencies = [
    "pandas==2.1.4",      # Pinned = consistent caching
    "sqlalchemy==2.0.25", # Specific = predictable builds
]
```

## 🎉 **Success Metrics**

**Good caching configuration results in:**
- ✅ **Sub-10-second rebuilds** for code-only changes
- ✅ **<2-minute full rebuilds** when dependencies change
- ✅ **Consistent build times** across all team members
- ✅ **Shared layer efficiency** >70% between team projects

**Poor caching results in:**
- ❌ **5-15 minute rebuilds** for small changes
- ❌ **Build time variance** between team members
- ❌ **Frequent "downloading" steps** in Docker builds
- ❌ **Frustrated developers** avoiding DevContainer usage

---

**Bottom Line**: Spending 10 minutes on configuration strategy can save your team **hours per week** in build times.