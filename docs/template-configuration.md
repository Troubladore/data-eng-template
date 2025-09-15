# Template Configuration Guide

## 🎯 **Understanding Configuration Choices and Their Impact**

This guide explains every configuration option in the cookiecutter template, organized by the same topics as `company-template-defaults.yaml`. Wide tables show all choices, meanings, and caching impacts at a glance for easy comparison.

---

## 🚨 **Required Prompts (Cannot Be Defaulted)**

These three settings must be answered for every project generation:

| Setting | Format/Choices | Description | Caching Impact | Isolation Impact |
|---------|----------------|-------------|----------------|------------------|
| **`customer_slug`** | kebab-case<br>Examples: `customer-analytics`, `fraud-detection` | Project identifier used throughout system | **High** - Creates unique image tags, container names, layer paths | Complete separation - each slug gets separate containers, volumes, networks |
| **`description`** | Free text<br>Examples: "Customer analytics pipeline", "Fraud detection system" | Brief project summary for documentation | **None** - Documentation only | None |
| **`deployment_mode`** | `production` \| `testing` | Container naming strategy for environment isolation | **High** - Different modes create separate image caches | **Critical** - See detailed breakdown below |

### **`deployment_mode` Detailed Breakdown**

| Choice | Container Naming | When to Use | Isolation Benefit | Examples |
|--------|------------------|-------------|-------------------|----------|
| **`production`** | Standard names<br>`customer-analytics-postgres` | • Permanent projects<br>• Shared development<br>• Production-bound systems | Clean permanent namespace | Long-running analytics, shared team projects |
| **`testing`** | `-test` suffix<br>`customer-analytics-postgres-test` | • Temporary experiments<br>• CI/CD pipelines<br>• Throwaway development | Complete isolation from production containers | Feature experiments, automated testing, POCs |

---

## ⚡ **Critical Caching Settings**

These settings have **massive impact** on Docker build performance. Misalignment across team members causes complete cache invalidation.

| Setting | Default | Choices | Description | Caching Impact | Why Critical |
|---------|---------|---------|-------------|----------------|--------------|
| **`python_version`** | `3.12` | Any valid version<br>`3.11`, `3.12`, `3.13` | Python runtime for all containers | **CRITICAL** - Base image layer for ALL containers | Different versions = zero layer sharing across team |
| **`airflow_version`** | `3.0.6` | Any Astronomer version<br>`3.0.6`, `3.0.7`, `2.10.2` | Airflow runtime version | **CRITICAL** - Airflow base layers (2GB+ impact) | Version changes invalidate all Airflow-related layers |
| **`postgres_version`** | `16` | Any major version<br>`15`, `16`, `17` | PostgreSQL database version | **Medium** - Database container layers | Database init and extension layers depend on version |
| **`runtime_tag`** | `3.0-10` | Must match airflow_version<br>`3.0-10`, `2.10-1` | Astronomer runtime image tag | **CRITICAL** - Must align or cache misses | Misaligned versions = 5-10 minute cache penalty |

### **Critical Version Alignment Requirements**

| Airflow Version | Required Runtime Tag | Cache Impact if Mismatched |
|-----------------|---------------------|---------------------------|
| `3.0.6` | `3.0-10` | +5-10 minutes per build |
| `2.10.2` | `2.10-1` | +5-10 minutes per build |

---

## 🔐 **Container Registry Configuration**

| Setting | Default | Format | Examples | Caching Impact | Why Important |
|---------|---------|--------|----------|----------------|---------------|
| **`image_repo`** | `registry.example.com/etl/{{ cookiecutter.customer_slug }}` | Registry URL with templating | **Azure**: `yourregistry.azurecr.io/data-eng/{{ cookiecutter.customer_slug }}`<br>**AWS**: `123456789.dkr.ecr.us-east-1.amazonaws.com/etl/{{ cookiecutter.customer_slug }}`<br>**GCP**: `gcr.io/your-project/data-eng/{{ cookiecutter.customer_slug }}`<br>**Docker Hub**: `yourorg/{{ cookiecutter.customer_slug }}-etl` | **High** - Controls push/pull optimization and layer sharing | Registry paths create separate cache namespaces |

---

## 🏢 **Security and Enterprise Settings**

| Setting | Default | Choices & Meanings | Caching Impact | Security/Performance Impact |
|---------|---------|-------------------|----------------|---------------------------|
| **`secrets_strategy`** | `azure-key-vault` | **`azure-key-vault`**: Azure Key Vault + managed identity<br>**`external-secrets-operator`**: Kubernetes External Secrets<br>**`env-vars`**: Environment variables (dev only) | **None** - Runtime config | **High** - Choose based on org security requirements |
| **`executor`** | `KubernetesExecutor` | **`KubernetesExecutor`**: Tasks in separate K8s pods (scale)<br>**`CeleryExecutor`**: Tasks on Celery workers (existing infra)<br>**`LocalExecutor`**: Tasks on scheduler (dev/small workloads) | **None** - Runtime config | **High** - Choose based on workload and infrastructure |
| **`enable_kerberos`** | `no` | **`no`**: Standard authentication (most cases)<br>**`yes`**: Kerberos enterprise authentication | **Low** - May affect dependency layers | **Medium** - Required if org uses Kerberos |
| **`license`** | `Proprietary` | **`Proprietary`**: Internal/company use only<br>**`MIT`**: Open source, minimal restrictions<br>**`Apache-2.0`**: Open source with patent protection | **None** - Documentation only | **High** - Choose based on distribution intent |

---

## 🌐 **Environment and Database Settings**

| Setting | Default | Choices & Meanings | Caching Impact | Default Impact |
|---------|---------|-------------------|----------------|----------------|
| **`env_name`** | `dev` | **`dev`**: Development (debug, verbose logging)<br>**`int`**: Integration (staging-like, external systems)<br>**`qa`**: Quality assurance (testing, validation)<br>**`prod`**: Production (optimized, monitoring) | **None** - Runtime config | **Medium** - Sets default Hydra environment |
| **`db_user`** | `postgres` | Default database username | **None** - Runtime config | Development default only |
| **`db_password`** | `postgres` | Default database password | **None** - Runtime config | Development default - use secrets in prod |

---

## 📝 **Organizational and Documentation Settings**

| Setting | Default | Examples | Caching Impact | Purpose |
|---------|---------|----------|----------------|---------|
| **`author_name`** | `Data Engineering Team` | "Acme Analytics Team", "Data Platform Engineering" | **None** - Documentation only | Team/person credited in docs |
| **`company_domain`** | `myco.com` | "acme.com", "datacompany.io" | **None** - Config only | Company domain in configs/docs |
| **`high_label`** | `high` | "sensitive", "confidential", "internal" | **None** - Config only | Security classification label |

---

## 🔄 **Auto-Generated Values (Usually Don't Change)**

| Setting | Generation Logic | Example | Purpose |
|---------|------------------|---------|---------|
| **`db_name`** | `{{ cookiecutter.customer_slug.replace('-', '_') }}_etl` | `customer-analytics` → `customer_analytics_etl` | Database name from slug |
| **`project_name`** | `{{ cookiecutter.customer_slug \| title }} ETL Project` | `customer-analytics` → `Customer Analytics ETL Project` | Human-readable name |
| **`project_slug`** | `{{ cookiecutter.customer_slug }}-etl` | `customer-analytics` → `customer-analytics-etl` | Full project identifier |
| **`year`** | `2025` | `2025` | License headers |

---

## 🏗️ **Docker Caching Architecture**

### **How Configuration Choices Affect Layer Sharing**

| Layer | Depends On | Shared If Match | Impact of Mismatch |
|-------|------------|-----------------|-------------------|
| **Layer 1**: Base OS + Runtime | `airflow_version` + `runtime_tag` | ✅ Shared across all projects | Complete rebuild (2GB+ download) |
| **Layer 2**: Python Setup | `python_version` | ✅ Shared if same Python version | Python installation rebuild |
| **Layer 3**: System Dependencies | `postgres_version` + system deps | ✅ Shared if same versions | System package reinstall |
| **Layer 4**: Python Dependencies | requirements.txt consistency | ✅ Shared if same deps | pip install rebuild |
| **Layer 5**: Project Code | `customer_slug` + `deployment_mode` | ❌ Always unique per project | Project-specific (fast) |

### **Team Alignment Impact**

| Scenario | Build Time | Layer Sharing |
|----------|------------|---------------|
| **Perfect Alignment**<br>Same `python_version`, `airflow_version`, `runtime_tag`, `postgres_version` | **10-second rebuilds** | 80% layer sharing |
| **Poor Alignment**<br>Different versions across team | **10-minute rebuilds** | 0% layer sharing |

---

## 🎯 **Configuration Recommendations**

### **Organizational Defaults Template**

```yaml
# your-org-defaults.yaml
default_context:
  # CRITICAL: Standardize for caching
  python_version: "3.12"
  airflow_version: "3.0.6"
  postgres_version: "16"
  runtime_tag: "3.0-10"

  # CUSTOMIZE: Match your infrastructure
  image_repo: "your-registry.com/data-eng/{{ cookiecutter.customer_slug }}"
  secrets_strategy: "azure-key-vault"
  executor: "KubernetesExecutor"

  # CUSTOMIZE: Your organization
  author_name: "Your Data Engineering Team"
  company_domain: "yourcompany.com"
  license: "Proprietary"
```

### **Usage Patterns**

| Project Type | Recommended Settings | Rationale |
|--------------|---------------------|-----------|
| **Permanent Production** | `deployment_mode: production` | Standard naming, permanent namespace |
| **Temporary/Experimental** | `deployment_mode: testing` | Isolated with `-test` suffix |
| **Team Standards** | Same caching settings across all projects | Maximize Docker layer sharing |

---

## ⚠️ **Common Pitfalls**

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **Version Drift** | Team members use different `airflow_version` values | Standardize in organizational defaults |
| **Registry Inconsistency** | Different `image_repo` patterns break sharing | Use consistent templated pattern |
| **Runtime Mismatch** | `runtime_tag` doesn't match `airflow_version` | Verify alignment in defaults |
| **Wrong Deployment Mode** | Using `production` for temporary experiments | Use `testing` for temporary/experimental work |

---

## 🎉 **Success Metrics**

| Good Configuration | Poor Configuration |
|-------------------|-------------------|
| ✅ Sub-10-second rebuilds for code changes | ❌ 5-15 minute rebuilds for small changes |
| ✅ <2-minute full rebuilds for dependency changes | ❌ Build time variance between team members |
| ✅ Consistent build times across team members | ❌ Container name conflicts between projects |
| ✅ Clean isolation between production/testing | ❌ Cache invalidation from version mismatches |
| ✅ 80%+ shared layer efficiency between projects | ❌ Developers avoiding DevContainer usage |

**Bottom Line**: Wide tables help you quickly compare choices and understand impacts - essential for making informed organizational configuration decisions.