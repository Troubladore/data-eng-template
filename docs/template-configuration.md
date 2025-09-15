# Template Configuration Guide

## 🎯 **Understanding Configuration Choices and Their Impact**

This guide explains every configuration option in the cookiecutter template, organized by the same topics as `company-template-defaults.yaml`. Each setting includes available choices, their meanings, and caching implications to help you make informed organizational decisions.

## 🚨 **Required Prompts (Cannot Be Defaulted)**

These three settings must be answered for every project generation:

### **`customer_slug`**
**Description**: Project identifier used throughout the system
**Format**: kebab-case (lowercase letters, numbers, hyphens only)
**Examples**: `customer-analytics`, `fraud-detection`, `user-segmentation`
**Caching Impact**: **High** - Creates unique image tags, container names, and layer paths
**Isolation Impact**: Each slug gets completely separate containers, volumes, and networks

### **`description`**
**Description**: Brief project summary for documentation
**Format**: Free text
**Examples**: "Customer analytics data pipeline", "Real-time fraud detection system"
**Caching Impact**: **None** - Only affects generated documentation
**Isolation Impact**: None

### **`deployment_mode`**
**Choices**: `production` | `testing`
**Description**: Controls container naming patterns for environment isolation
**Meanings**:
- **`production`**: Standard container names for long-running, permanent projects
- **`testing`**: Adds `-test` suffix to all container/image names for temporary isolation

**Caching Impact**: **High** - Different modes create separate image caches
**Isolation Impact**: **Critical** - Testing mode containers are completely isolated from production:
```yaml
# production mode
container_name: customer-analytics-postgres

# testing mode
container_name: customer-analytics-postgres-test
```

**When to Use**:
- **`production`**: Permanent projects, shared development, production-bound systems
- **`testing`**: Temporary experiments, CI/CD pipelines, throwaway development

---

## ⚡ **Critical Caching Settings**

These settings have **massive impact** on Docker build performance. Misalignment across team members causes complete cache invalidation.

### **`python_version`**
**Default**: `3.12`
**Choices**: Any valid Python version (e.g., `3.11`, `3.12`, `3.13`)
**Description**: Python runtime version for all containers
**Caching Impact**: **CRITICAL** - Base image layer for ALL containers
**Recommendation**: **Standardize across entire organization**

**Why Critical**: Python version determines the base image layer. Different versions = zero layer sharing
```dockerfile
# This layer is shared if python_version matches across projects
FROM python:${PYTHON_VERSION}-slim
```

### **`airflow_version`**
**Default**: `3.0.6`
**Choices**: Any Astronomer Airflow version (e.g., `3.0.6`, `3.0.7`, `2.10.2`)
**Description**: Airflow runtime version
**Caching Impact**: **CRITICAL** - Airflow base image layers (largest cache impact)
**Recommendation**: **Use stable releases, coordinate updates across team**

**Why Critical**: Airflow base image is 2GB+. Version changes invalidate all Airflow-related layers
```dockerfile
FROM registry.astronomer.io/ap-airflow:${AIRFLOW_VERSION}
```

### **`postgres_version`**
**Default**: `16`
**Choices**: Any PostgreSQL major version (e.g., `15`, `16`, `17`)
**Description**: PostgreSQL database version
**Caching Impact**: **Medium** - Database container layers
**Recommendation**: **Standardize on stable version**

**Why Matters**: Database initialization and extension layers depend on PostgreSQL version

### **`runtime_tag`**
**Default**: `3.0-10`
**Choices**: Must match Astronomer runtime tags for your `airflow_version`
**Description**: Astronomer runtime image tag
**Caching Impact**: **CRITICAL** - Must align with airflow_version or cache misses occur

**Critical Requirement**: `runtime_tag` MUST match your `airflow_version`:
- Airflow `3.0.6` → Runtime `3.0-10`
- Airflow `2.10.2` → Runtime `2.10-1`
- Mismatched versions cause 5-10 minute cache penalty per build

---

## 🔐 **Container Registry Configuration**

### **`image_repo`**
**Default**: `registry.example.com/etl/{{ cookiecutter.customer_slug }}`
**Format**: Container registry URL with optional templating
**Examples**:
- Azure: `yourregistry.azurecr.io/data-eng/{{ cookiecutter.customer_slug }}`
- AWS: `123456789.dkr.ecr.us-east-1.amazonaws.com/etl/{{ cookiecutter.customer_slug }}`
- GCP: `gcr.io/your-project/data-eng/{{ cookiecutter.customer_slug }}`
- Docker Hub: `yourorg/{{ cookiecutter.customer_slug }}-etl`

**Caching Impact**: **High** - Controls push/pull optimization and layer sharing
**Recommendation**: **Use consistent registry pattern across all team projects**

**Why Important**: Registry paths create separate cache namespaces. Different patterns = no layer sharing

---

## 🏢 **Security and Enterprise Settings**

### **`secrets_strategy`**
**Choices**: `azure-key-vault` | `external-secrets-operator` | `env-vars`
**Description**: How secrets are managed in the generated project
**Meanings**:
- **`azure-key-vault`**: Azure Key Vault integration with managed identity
- **`external-secrets-operator`**: Kubernetes External Secrets Operator
- **`env-vars`**: Simple environment variables (development only)

**Caching Impact**: **None** - Runtime configuration only
**Security Impact**: **High** - Choose based on your organization's security requirements

### **`executor`**
**Choices**: `KubernetesExecutor` | `CeleryExecutor` | `LocalExecutor`
**Description**: Airflow task execution strategy
**Meanings**:
- **`KubernetesExecutor`**: Tasks run in separate Kubernetes pods (recommended for scale)
- **`CeleryExecutor`**: Tasks run on Celery worker nodes (recommended for existing Celery infrastructure)
- **`LocalExecutor`**: Tasks run on scheduler machine (development/small workloads only)

**Caching Impact**: **None** - Runtime configuration
**Performance Impact**: **High** - Choose based on expected workload and infrastructure

### **`enable_kerberos`**
**Choices**: `no` | `yes`
**Description**: Enable Kerberos authentication integration
**Meanings**:
- **`no`**: Standard authentication (recommended for most cases)
- **`yes`**: Kerberos integration for enterprise authentication

**Caching Impact**: **Low** - May affect some dependency installation layers
**Security Impact**: **Medium** - Required if your organization uses Kerberos

### **`license`**
**Choices**: `Proprietary` | `MIT` | `Apache-2.0`
**Description**: License for the generated project
**Meanings**:
- **`Proprietary`**: Internal/company use only
- **`MIT`**: Open source with minimal restrictions
- **`Apache-2.0`**: Open source with patent protection

**Caching Impact**: **None** - Documentation only
**Legal Impact**: **High** - Choose based on intended project distribution

---

## 🌐 **Environment and Database Settings**

### **`env_name`**
**Choices**: `dev` | `int` | `qa` | `prod`
**Description**: Default environment name for configuration
**Meanings**:
- **`dev`**: Development environment (debug enabled, verbose logging)
- **`int`**: Integration environment (staging-like, external system integration)
- **`qa`**: Quality assurance environment (testing, validation)
- **`prod`**: Production environment (optimized, monitoring enabled)

**Caching Impact**: **None** - Runtime configuration only
**Default Impact**: **Medium** - Sets default Hydra environment configuration

### **`db_user`** / **`db_password`**
**Defaults**: `postgres` / `postgres`
**Description**: Default database credentials for development
**Caching Impact**: **None** - Runtime configuration
**Security Note**: These are development defaults only - production should use secrets management

---

## 📝 **Organizational and Documentation Settings**

### **`author_name`**
**Default**: `Data Engineering Team`
**Description**: Team/person credited in generated documentation
**Caching Impact**: **None** - Documentation only
**Examples**: "Acme Analytics Team", "Data Platform Engineering"

### **`company_domain`**
**Default**: `myco.com`
**Description**: Company domain used in configurations and documentation
**Caching Impact**: **None** - Configuration only
**Examples**: "acme.com", "datacompany.io"

### **`high_label`**
**Default**: `high`
**Description**: Security classification label for sensitive data
**Caching Impact**: **None** - Configuration only
**Examples**: "sensitive", "confidential", "internal"

---

## 🔄 **Auto-Generated Values (Usually Don't Change)**

### **`db_name`**
**Default**: `{{ cookiecutter.customer_slug.replace('-', '_') }}_etl`
**Description**: Database name derived from project slug
**Example**: `customer-analytics` → `customer_analytics_etl`

### **`project_name`**
**Default**: `{{ cookiecutter.customer_slug | title }} ETL Project`
**Description**: Human-readable project name
**Example**: `customer-analytics` → `Customer Analytics ETL Project`

### **`project_slug`**
**Default**: `{{ cookiecutter.customer_slug }}-etl`
**Description**: Full project identifier with suffix
**Example**: `customer-analytics` → `customer-analytics-etl`

### **`year`**
**Default**: `2025`
**Description**: Current year for license headers
**Caching Impact**: **None** - Documentation only

---

## 🏗️ **Docker Caching Architecture Deep Dive**

### **How Configuration Choices Affect Layer Caching**

```dockerfile
# Layer 1: Base OS + Runtime (shared if airflow_version + runtime_tag match)
FROM registry.astronomer.io/ap-airflow:${AIRFLOW_VERSION}-${RUNTIME_TAG}

# Layer 2: Python setup (shared if python_version matches)
RUN apt-get update && python${PYTHON_VERSION} setup...

# Layer 3: System dependencies (shared if same versions)
RUN apt-get install postgresql-client-${POSTGRES_VERSION}

# Layer 4: Python dependencies (shared if same requirements.txt)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Layer 5: Project code (unique per customer_slug + deployment_mode)
COPY dags/ /opt/airflow/dags/
LABEL de-template.project="${CUSTOMER_SLUG}"
LABEL de-template.deployment="${DEPLOYMENT_MODE}"
```

### **Critical Caching Insights**

1. **Layers 1-3 can be shared** if `airflow_version`, `runtime_tag`, `python_version`, and `postgres_version` match
2. **Layer 4 caching** depends on requirements.txt consistency across projects
3. **Layer 5 is always unique** per project/deployment mode
4. **Different deployment_modes** create separate image caches for isolation

### **Team Alignment = Faster Builds**

**Good alignment** (10-second rebuilds):
```yaml
# All team members use
python_version: "3.12"
airflow_version: "3.0.6"
runtime_tag: "3.0-10"
postgres_version: "16"
```

**Poor alignment** (10-minute rebuilds):
```yaml
# Team member A
python_version: "3.11"
airflow_version: "3.0.6"

# Team member B
python_version: "3.12"
airflow_version: "3.0.7"
```

---

## 🎯 **Configuration Recommendations by Use Case**

### **For Organizations Setting Defaults**

```yaml
# company-template-defaults.yaml
default_context:
  # CRITICAL: Standardize these for caching
  python_version: "3.12"
  airflow_version: "3.0.6"
  postgres_version: "16"
  runtime_tag: "3.0-10"

  # CUSTOMIZE: Match your infrastructure
  image_repo: "your-registry.com/data-eng/{{ cookiecutter.customer_slug }}"
  secrets_strategy: "azure-key-vault"
  executor: "KubernetesExecutor"

  # CUSTOMIZE: Your organization details
  author_name: "Your Data Engineering Team"
  company_domain: "yourcompany.com"
  license: "Proprietary"
```

### **For Permanent Production Projects**

```bash
# Use when generating long-running, shared projects
cookiecutter . --config-file your-org-defaults.yaml

# Answer prompts:
customer_slug: customer-analytics
description: Customer behavior analytics pipeline
deployment_mode: production  # ← Standard naming
```

### **For Temporary Development/Testing**

```bash
# Use for experiments, CI/CD, temporary development
cookiecutter . --config-file your-org-defaults.yaml

# Answer prompts:
customer_slug: experiment-new-feature
description: Testing new ML feature approach
deployment_mode: testing  # ← Isolated naming with -test suffix
```

---

## ⚠️ **Common Configuration Pitfalls**

### **Pitfall 1: Version Drift Across Team**
❌ **Problem**: Team members use different versions
```yaml
# Developer A (older project)
airflow_version: "3.0.6"

# Developer B (newer project)
airflow_version: "3.0.7"
```
✅ **Solution**: Standardize versions in organizational defaults

### **Pitfall 2: Registry Inconsistency**
❌ **Problem**: Different registry patterns break layer sharing
```yaml
# Project A
image_repo: "acr.company.com/etl/project-a"

# Project B
image_repo: "registry.company.com/data/project-b"
```
✅ **Solution**: Use consistent registry pattern with templating

### **Pitfall 3: Misaligned Runtime Tags**
❌ **Problem**: Runtime tag doesn't match Airflow version
```yaml
airflow_version: "3.0.6"
runtime_tag: "2.10-1"  # Wrong runtime for this Airflow version
```
✅ **Solution**: Verify runtime tag matches your Airflow version

### **Pitfall 4: Wrong Deployment Mode for Use Case**
❌ **Problem**: Using production mode for temporary experiments
```bash
# Temporary experiment clutters permanent namespace
deployment_mode: production
```
✅ **Solution**: Use `testing` mode for temporary/experimental projects

---

## 🎉 **Success Metrics**

**Good configuration results in:**
- ✅ **Sub-10-second rebuilds** for code-only changes
- ✅ **<2-minute full rebuilds** when dependencies change
- ✅ **Consistent build times** across all team members
- ✅ **Clean isolation** between production and testing projects
- ✅ **Predictable resource usage** with proper executor choice

**Poor configuration results in:**
- ❌ **5-15 minute rebuilds** for small changes
- ❌ **Build time variance** between team members
- ❌ **Container name conflicts** between projects
- ❌ **Cache invalidation** from version mismatches
- ❌ **Frustrated developers** avoiding DevContainer usage

---

**Bottom Line**: Understanding these configuration choices and their impacts allows you to optimize for your team's caching efficiency, security requirements, and operational needs.