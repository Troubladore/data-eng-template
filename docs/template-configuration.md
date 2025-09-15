# Template Configuration Guide

## 🎯 **Understanding Configuration Choices and Their Impact**

This guide explains every configuration option in the cookiecutter template, organized by the same topics as `company-template-defaults.yaml`. Use the overview tables to understand settings at a glance, then drill into detailed breakdowns for specific choices.

---

## 🚨 **Required Prompts (Cannot Be Defaulted)**

These three settings must be answered for every project generation:

| Setting | Description | Format | Examples/Choices | Suggested Default |
|---------|-------------|--------|------------------|-------------------|
| **`customer_slug`** | Project identifier used throughout system | kebab-case | `customer-analytics`, `fraud-detection`, `user-segmentation` | Project-specific |
| **`description`** | Brief project summary for documentation | Free text | "Customer analytics pipeline", "Fraud detection system" | Project-specific |
| **`deployment_mode`** | Container naming strategy for environment isolation | Choice list | `production`, `testing` | `production` |

<details>
<summary><strong>customer_slug</strong> - Project Identifier Details <a id="customer_slug"></a></summary>

| Example | Description | When to Use | Caching Impact | Isolation Impact |
|---------|-------------|-------------|----------------|------------------|
| `customer-analytics` | Kebab-case identifier for customer analytics project | Standard project naming | **High** - Creates unique image tags, container names, layer paths | **Complete** - Each slug gets separate containers, volumes, networks |
| `fraud-detection` | Kebab-case identifier for fraud detection project | Standard project naming | **High** - Creates unique image tags, container names, layer paths | **Complete** - Each slug gets separate containers, volumes, networks |
| `user-segmentation` | Kebab-case identifier for user segmentation project | Standard project naming | **High** - Creates unique image tags, container names, layer paths | **Complete** - Each slug gets separate containers, volumes, networks |

**Format Requirements**: Lowercase letters, numbers, and hyphens only. No spaces, underscores, or special characters.

</details>

<details>
<summary><strong>description</strong> - Project Description Details <a id="description"></a></summary>

| Example | Description | When to Use | Caching Impact | Isolation Impact |
|---------|-------------|-------------|----------------|------------------|
| "Customer analytics pipeline" | Brief summary explaining project purpose | Clear, descriptive project documentation | **None** - Documentation only | **None** |
| "Real-time fraud detection system" | Brief summary explaining project purpose | Clear, descriptive project documentation | **None** - Documentation only | **None** |
| "User behavior segmentation ML" | Brief summary explaining project purpose | Clear, descriptive project documentation | **None** - Documentation only | **None** |

**Format**: Free text, typically 1-2 sentences describing the project's business purpose.

</details>

<details>
<summary><strong>deployment_mode</strong> - Container Naming Strategy Details <a id="deployment_mode"></a></summary>

| Choice Value | Description | When to Use | Caching Impact | Isolation Impact |
|--------------|-------------|-------------|----------------|------------------|
| `production`<br>(default) | Standard container names (`customer-analytics-postgres`) | • Permanent projects<br>• Shared development<br>• Production-bound systems<br>• Long-running analytics | **High** - Standard image cache namespace | **Standard** - Clean permanent namespace |
| `testing` | Container names with `-test` suffix (`customer-analytics-postgres-test`) | • Temporary experiments<br>• CI/CD pipelines<br>• Throwaway development<br>• Feature testing<br>• POCs | **High** - Separate `-test` image cache namespace | **Complete** - Isolated from production containers |

**Critical**: Testing mode provides complete isolation from production containers, preventing conflicts during parallel development.

</details>

---

## ⚡ **Critical Caching Settings**

These settings have **massive impact** on Docker build performance. Misalignment across team members causes complete cache invalidation.

| Setting | Description | Format | Examples/Choices | Suggested Default |
|---------|-------------|--------|------------------|-------------------|
| **`python_version`** | Python runtime version for all containers | Version number | `3.11`, `3.12`, `3.13` | `3.12` |
| **`airflow_version`** | Airflow runtime version | Astronomer version | `3.0.6`, `3.0.7`, `2.10.2` | `3.0.6` |
| **`postgres_version`** | PostgreSQL database version | Major version | `15`, `16`, `17` | `16` |

<details>
<summary><strong>python_version</strong> - Python Runtime Version Details <a id="python_version"></a></summary>

| Choice Value | Description | When to Use | Caching Impact | Isolation Impact |
|--------------|-------------|-------------|----------------|------------------|
| `3.11` | Python 3.11 runtime | Legacy projects requiring 3.11 compatibility | **CRITICAL** - Different from team standard breaks all layer sharing | **None** |
| `3.12`<br>(default) | Python 3.12 runtime (recommended) | Standard for new projects, stable and performant | **CRITICAL** - Base image layer for ALL containers, must match team | **None** |
| `3.13` | Python 3.13 runtime (latest) | Bleeding edge features, early adoption | **CRITICAL** - Different from team standard breaks all layer sharing | **None** |

**Team Alignment Critical**: All team members MUST use the same Python version or Docker layer sharing fails completely.

</details>

<details>
<summary><strong>airflow_version</strong> - Airflow Runtime Version Details <a id="airflow_version"></a></summary>

| Choice Value | Description | When to Use | Caching Impact | Isolation Impact |
|--------------|-------------|-------------|----------------|------------------|
| `2.10.2` | Airflow 2.x series (legacy) | Existing projects requiring Airflow 2.x | **CRITICAL** - 2GB+ base image, version changes invalidate all layers | **None** |
| `3.0.6`<br>(default) | Airflow 3.0.6 (recommended) | New projects, stable Airflow 3.0 release | **CRITICAL** - 2GB+ base image, must align with team for sharing | **None** |
| `3.0.7` | Airflow 3.0.7 (newer) | Latest features, coordinate team upgrade | **CRITICAL** - Version changes break all Airflow-related layer sharing | **None** |

**Version Coordination**: Team must coordinate Airflow version changes to maintain Docker layer sharing efficiency.

</details>

<details>
<summary><strong>postgres_version</strong> - PostgreSQL Database Version Details <a id="postgres_version"></a></summary>

| Choice Value | Description | When to Use | Caching Impact | Isolation Impact |
|--------------|-------------|-------------|----------------|------------------|
| `15` | PostgreSQL 15 (older stable) | Legacy compatibility requirements | **Medium** - Database container layers, init scripts depend on version | **None** |
| `16`<br>(default) | PostgreSQL 16 (recommended) | Current stable release, good performance | **Medium** - Database initialization and extension layers | **None** |
| `17` | PostgreSQL 17 (newest) | Latest features, bleeding edge | **Medium** - Different version affects database setup layers | **None** |

**Stability Focus**: Version 16 provides good balance of features and stability for most data engineering workloads.

</details>

---

## 🔐 **Container Registry Configuration**

| Setting | Description | Format | Examples/Choices | Suggested Default |
|---------|-------------|--------|------------------|-------------------|
| **`image_repo`** | Container registry URL pattern | Registry URL with templating | Azure, AWS, GCP, Docker Hub patterns | `registry.example.com/etl/{{ cookiecutter.customer_slug }}` |

<details>
<summary><strong>image_repo</strong> - Container Registry Configuration Details <a id="image_repo"></a></summary>

| Example | Description | When to Use | Caching Impact | Isolation Impact |
|---------|-------------|-------------|----------------|------------------|
| `registry.example.com/etl/{{ cookiecutter.customer_slug }}`<br>(default) | Generic registry pattern | Template default, replace with your registry | **High** - Registry paths create separate cache namespaces | **None** |
| `yourregistry.azurecr.io/data-eng/{{ cookiecutter.customer_slug }}` | Azure Container Registry | Using Azure cloud infrastructure | **High** - Consistent pattern enables layer sharing across projects | **None** |
| `123456789.dkr.ecr.us-east-1.amazonaws.com/etl/{{ cookiecutter.customer_slug }}` | AWS Elastic Container Registry | Using AWS cloud infrastructure | **High** - Must be consistent across team for optimal caching | **None** |
| `gcr.io/your-project/data-eng/{{ cookiecutter.customer_slug }}` | Google Container Registry | Using GCP cloud infrastructure | **High** - Registry consistency critical for layer sharing | **None** |
| `yourorg/{{ cookiecutter.customer_slug }}-etl` | Docker Hub | Public or private Docker Hub usage | **High** - Different patterns break cross-project layer sharing | **None** |

**Consistency Critical**: All team projects must use the same registry pattern for Docker layer sharing to work effectively.

</details>

---

## 🏢 **Security and Enterprise Settings**

| Setting | Description | Format | Examples/Choices | Suggested Default |
|---------|-------------|--------|------------------|-------------------|
| **`secrets_strategy`** | How secrets are managed in generated project | Choice list | `azure-key-vault`, `external-secrets-operator`, `env-vars` | `azure-key-vault` |
| **`executor`** | Airflow task execution strategy | Choice list | `KubernetesExecutor`, `CeleryExecutor`, `LocalExecutor` | `KubernetesExecutor` |
| **`enable_kerberos`** | Enable Kerberos authentication integration | Choice list | `no`, `yes` | `no` |
| **`license`** | License for the generated project | Choice list | `Proprietary`, `MIT`, `Apache-2.0` | `Proprietary` |

<details>
<summary><strong>secrets_strategy</strong> - Secrets Management Strategy Details <a id="secrets_strategy"></a></summary>

| Choice Value | Description | When to Use | Caching Impact | Isolation Impact |
|--------------|-------------|-------------|----------------|------------------|
| `azure-key-vault`<br>(default) | Azure Key Vault integration with managed identity | Azure cloud environments, enterprise security | **None** - Runtime configuration only | **None** |
| `external-secrets-operator` | Kubernetes External Secrets Operator | Kubernetes environments, multi-cloud setups | **None** - Runtime configuration only | **None** |
| `env-vars` | Simple environment variables | Development only, non-production environments | **None** - Runtime configuration only | **None** |

**Security Note**: env-vars should only be used for development. Production environments should use proper secrets management.

</details>

<details>
<summary><strong>executor</strong> - Airflow Task Execution Strategy Details <a id="executor"></a></summary>

| Choice Value | Description | When to Use | Caching Impact | Isolation Impact |
|--------------|-------------|-------------|----------------|------------------|
| `KubernetesExecutor`<br>(default) | Tasks run in separate Kubernetes pods | Scalable environments, resource isolation per task | **None** - Runtime configuration | **High** - Each task in separate pod |
| `CeleryExecutor` | Tasks run on Celery worker nodes | Existing Celery infrastructure, traditional scaling | **None** - Runtime configuration | **Medium** - Tasks share worker nodes |
| `LocalExecutor` | Tasks run on scheduler machine | Development, small workloads, single-machine setups | **None** - Runtime configuration | **Low** - Tasks share scheduler resources |

**Scale Consideration**: KubernetesExecutor recommended for production workloads requiring scale and resource isolation.

</details>

<details>
<summary><strong>enable_kerberos</strong> - Kerberos Authentication Details <a id="enable_kerberos"></a></summary>

| Choice Value | Description | When to Use | Caching Impact | Isolation Impact |
|--------------|-------------|-------------|----------------|------------------|
| `no`<br>(default) | Standard authentication (recommended) | Most environments, modern authentication systems | **None** - Runtime configuration | **None** |
| `yes` | Kerberos enterprise authentication | Enterprise environments requiring Kerberos integration | **Low** - May affect some dependency installation layers | **None** |

**Enterprise Context**: Only enable if your organization specifically requires Kerberos authentication integration.

</details>

<details>
<summary><strong>license</strong> - Project License Details <a id="license"></a></summary>

| Choice Value | Description | When to Use | Caching Impact | Isolation Impact |
|--------------|-------------|-------------|----------------|------------------|
| `Proprietary`<br>(default) | Internal/company use only | Internal projects, confidential code | **None** - Documentation only | **None** |
| `MIT` | Open source with minimal restrictions | Open source projects, maximum permissiveness | **None** - Documentation only | **None** |
| `Apache-2.0` | Open source with patent protection | Open source projects needing patent protection | **None** - Documentation only | **None** |

**Distribution Intent**: Choose based on whether and how you plan to distribute the generated project code.

</details>

---

## 🌐 **Environment and Database Settings**

| Setting | Description | Format | Examples/Choices | Suggested Default |
|---------|-------------|--------|------------------|-------------------|
| **`env_name`** | Default environment name for configuration | Choice list | `dev`, `int`, `qa`, `prod` | `dev` |
| **`db_user`** | Default database username | String | `postgres`, `airflow`, `etl_user` | `postgres` |
| **`db_password`** | Default database password | String | `postgres`, `password123` | `postgres` |

<details>
<summary><strong>env_name</strong> - Default Environment Configuration Details <a id="env_name"></a></summary>

| Choice Value | Description | When to Use | Caching Impact | Isolation Impact |
|--------------|-------------|-------------|----------------|------------------|
| `dev`<br>(default) | Development environment (debug enabled, verbose logging) | Local development, debugging, experimentation | **None** - Runtime configuration | **None** |
| `int` | Integration environment (staging-like, external system integration) | Integration testing, external system connectivity | **None** - Runtime configuration | **None** |
| `qa` | Quality assurance environment (testing, validation) | QA testing, validation workflows | **None** - Runtime configuration | **None** |
| `prod` | Production environment (optimized, monitoring enabled) | Production deployments, performance-focused | **None** - Runtime configuration | **None** |

**Default Impact**: Sets the default Hydra environment configuration - can be overridden at runtime.

</details>

<details>
<summary><strong>db_user</strong> and <strong>db_password</strong> - Database Credentials Details <a id="db_credentials"></a></summary>

| Example | Description | When to Use | Caching Impact | Isolation Impact |
|---------|-------------|-------------|----------------|------------------|
| `postgres` / `postgres`<br>(default) | Standard PostgreSQL defaults | Development environments, local testing | **None** - Runtime configuration | **None** |
| `airflow` / `custom_password` | Custom Airflow user | Specialized database setup, custom permissions | **None** - Runtime configuration | **None** |
| `etl_user` / `secure_password` | ETL-specific user | Role-based database access, production-like setup | **None** - Runtime configuration | **None** |

**Security Warning**: These are development defaults only. Production environments should use proper secrets management systems.

</details>

---

## 📝 **Organizational and Documentation Settings**

| Setting | Description | Format | Examples/Choices | Suggested Default |
|---------|-------------|--------|------------------|-------------------|
| **`author_name`** | Team/person credited in generated documentation | Free text | `Data Engineering Team`, `Acme Analytics Team` | `Data Engineering Team` |
| **`company_domain`** | Company domain used in configurations and documentation | Domain format | `myco.com`, `acme.com`, `datacompany.io` | `myco.com` |
| **`high_label`** | Security classification label for sensitive data | Free text | `high`, `sensitive`, `confidential`, `internal` | `high` |

<details>
<summary><strong>author_name</strong>, <strong>company_domain</strong>, <strong>high_label</strong> - Organizational Settings Details <a id="organizational_settings"></a></summary>

| Setting | Example | Description | When to Use | Caching Impact | Isolation Impact |
|---------|---------|-------------|-------------|----------------|------------------|
| **`author_name`** | `Data Engineering Team`<br>(default) | Default team name in documentation | Standard team attribution | **None** - Documentation only | **None** |
| `author_name` | `Acme Analytics Team` | Custom team name | Organization-specific team name | **None** - Documentation only | **None** |
| **`company_domain`** | `myco.com`<br>(default) | Default company domain | Template default, customize for org | **None** - Configuration only | **None** |
| `company_domain` | `acme.com` | Custom company domain | Real organization domain | **None** - Configuration only | **None** |
| **`high_label`** | `high`<br>(default) | Default security classification | Standard security labeling | **None** - Configuration only | **None** |
| `high_label` | `sensitive` | Custom security classification | Organization-specific classification | **None** - Configuration only | **None** |

**Organizational Customization**: These settings should be customized in your organizational defaults file for consistency.

</details>

---

## 🔄 **Auto-Generated Values (Usually Don't Change)**

| Setting | Naming Pattern | Examples/Choices | Suggested Default |
|---------|----------------|------------------|-------------------|
| **`db_name`** | `{{ cookiecutter.customer_slug.replace('-', '_') }}_etl` | `customer_analytics_etl`, `fraud_detection_etl` | Auto-generated |
| **`project_name`** | `{{ cookiecutter.customer_slug \| title }} ETL Project` | `Customer Analytics ETL Project` | Auto-generated |
| **`project_slug`** | `{{ cookiecutter.customer_slug }}-etl` | `customer-analytics-etl` | Auto-generated |
| **`runtime_tag`** | Auto-derived from `airflow_version` | `3.0-10` (for airflow 3.0.6), `2.10-1` (for airflow 2.10.2) | Auto-generated |
| **`year`** | Current year for license headers | `2025` | Auto-generated |

<details>
<summary><strong>db_name</strong>, <strong>project_name</strong>, <strong>project_slug</strong> - Auto-Generated Names Details <a id="auto_generated_names"></a></summary>

| Setting | Example | Description | When to Use | Caching Impact | Isolation Impact |
|---------|---------|-------------|-------------|----------------|------------------|
| **`db_name`** | `customer_analytics_etl`<br>(auto-generated) | Database name from slug with underscores and _etl suffix | Always use auto-generation for consistency | **None** - Runtime configuration | **None** |
| **`project_name`** | `Customer Analytics ETL Project`<br>(auto-generated) | Human-readable title case project name | Always use auto-generation for consistency | **None** - Documentation only | **None** |
| **`project_slug`** | `customer-analytics-etl`<br>(auto-generated) | Full project identifier with -etl suffix | Always use auto-generation for consistency | **None** - Used in container naming | **None** |

**Recommendation**: Leave these as auto-generated unless you have specific requirements to override the default logic.

</details>

<details>
<summary><strong>runtime_tag</strong> - Auto-Generated Runtime Tag Details <a id="runtime_tag"></a></summary>

| Airflow Version | Runtime Tag | Description | When to Use | Caching Impact | Isolation Impact |
|-----------------|-------------|-------------|-------------|----------------|------------------|
| `2.10.2` | `2.10-1`<br>(auto-generated) | Runtime automatically matched to Airflow 2.10.x | Always use auto-generation to prevent misalignment | **CRITICAL** - Auto-alignment prevents 5-10 min cache penalty | **None** |
| `3.0.6` | `3.0-10`<br>(auto-generated) | Runtime automatically matched to Airflow 3.0.6 | Always use auto-generation to prevent misalignment | **CRITICAL** - Auto-alignment ensures proper caching | **None** |
| `3.0.7` | `3.0-11`<br>(auto-generated) | Runtime automatically matched to Airflow 3.0.7+ | Always use auto-generation to prevent misalignment | **CRITICAL** - Auto-alignment prevents cache misses | **None** |

**Functional by Design**: runtime_tag is automatically derived from airflow_version to eliminate configuration traps and ensure proper cache alignment.

</details>

<details>
<summary><strong>year</strong> - Auto-Generated Year Details <a id="year"></a></summary>

| Example | Description | When to Use | Caching Impact | Isolation Impact |
|---------|-------------|-------------|----------------|------------------|
| `2025`<br>(auto-generated) | Current year for license headers | Always use auto-generation for accuracy | **None** - Documentation only | **None** |

**Recommendation**: Leave as auto-generated to always reflect the current year accurately.

</details>

---

## 🎯 **Quick Configuration Template**

Based on the settings above, here's a template for your organizational defaults:

```yaml
# your-org-defaults.yaml
default_context:
  # Required prompts (still need to be answered)
  customer_slug: "your-project"
  description: "Your project description"
  deployment_mode: "production"

  # Critical caching settings (MUST be consistent across team)
  python_version: "3.12"
  airflow_version: "3.0.6"
  postgres_version: "16"
  # runtime_tag auto-generated from airflow_version

  # Your infrastructure
  image_repo: "your-registry.com/data-eng/{{ cookiecutter.customer_slug }}"
  secrets_strategy: "azure-key-vault"
  executor: "KubernetesExecutor"

  # Your organization
  author_name: "Your Data Engineering Team"
  company_domain: "yourcompany.com"
  license: "Proprietary"
```

**Next Step**: Use this understanding to customize your organizational defaults and streamline project generation for your team.