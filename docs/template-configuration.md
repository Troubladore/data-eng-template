# Template Configuration Guide

## 🎯 **Understanding Configuration Choices and Their Impact**

This guide explains every configuration option in the cookiecutter template, organized by the same topics as `company-template-defaults.yaml`. Use the overview tables to understand settings at a glance, then drill into detailed breakdowns for specific choices.

---

## 🚨 **Required Prompts (Cannot Be Defaulted)**

These three settings must be answered for every project generation:

| Setting | Short Description | Format | Examples/Choices | Suggested Default |
|---------|-------------------|--------|------------------|-------------------|
| **`customer_slug`** | Project identifier used throughout system | kebab-case | `customer-analytics`, `fraud-detection`, `user-segmentation` | Project-specific |
| **`description`** | Brief project summary for documentation | Free text | "Customer analytics pipeline", "Fraud detection system" | Project-specific |
| **`deployment_mode`** | Container naming strategy for environment isolation | Choice list | `production`, `testing` | `production` |

<details>
<summary><strong>customer_slug</strong> - Project Identifier Details <a id="customer_slug"></a></summary>

**Context**: The customer_slug is the fundamental identifier that flows through every aspect of your generated project. It becomes container names, database names, directory paths, and Docker image tags. While seemingly simple, this choice affects project organization, team coordination, and operational clarity.

| Example | Why This Works | Caching Impact | Isolation Impact |
|---------|----------------|----------------|------------------|
| `customer-analytics` | Clear business domain, follows kebab-case convention, descriptive without being verbose | **Final layer only** - Only affects image tags and container names in the final cosmetic layer | **Complete namespace separation** - Each slug gets separate containers, volumes, networks |
| `fraud-detection` | Domain-focused naming, uses standard separators, immediately recognizable purpose | **Final layer only** - Project naming doesn't impact underlying build layers or component caching | **Complete namespace separation** - Prevents any resource conflicts between projects |
| `user-segmentation` | Business-aligned terminology, proper format, indicates data scope clearly | **Final layer only** - Infrastructure and dependency caching unaffected by project naming | **Complete namespace separation** - Operational isolation across all Docker resources |

**Format Requirements**: Lowercase letters, numbers, and hyphens only. No spaces, underscores, or special characters.

</details>

<details>
<summary><strong>description</strong> - Project Description Details <a id="description"></a></summary>

**Context**: The description provides human-readable context for your project, appearing in documentation, README files, and project metadata. This is your opportunity to clearly communicate the project's business purpose and scope to team members and stakeholders.

| Example | Why This Works | Caching Impact | Isolation Impact |
|---------|----------------|----------------|------------------|
| "Customer analytics pipeline" | Concise business purpose, clear data domain, indicates pipeline nature | **None** - Pure documentation, no impact on any build layers | **None** - Documentation only |
| "Real-time fraud detection system" | Specifies real-time requirement, clear security domain, system-level scope | **None** - Documentation metadata only | **None** - No operational impact |
| "User behavior segmentation ML" | Indicates ML workload, specifies data type, clear analytical purpose | **None** - No influence on Docker layers or caching | **None** - Documentation artifact only |

**Format**: Free text, typically 1-2 sentences describing the project's business purpose.

</details>

<details>
<summary><strong>deployment_mode</strong> - Container Naming Strategy Details <a id="deployment_mode"></a></summary>

**Context**: Deployment mode controls the container naming strategy to enable parallel development workflows. This is critical for teams running multiple projects simultaneously, CI/CD pipelines, and isolating experimental work from production-bound projects.

| Choice Value | Why This Works | Caching Impact | Isolation Impact |
|--------------|----------------|----------------|------------------|
| `production`<br><div style="text-align:center">(default)</div> | Standard container names create predictable, clean operational environment for permanent projects | **Separate image namespaces** - Production and testing use different Docker image caches | **Standard namespace** - Clean, permanent container names |
| `testing` | `-test` suffix provides complete isolation for experiments, CI/CD, and temporary development work | **Separate image namespaces** - Testing containers completely isolated from production images | **Complete isolation** - No conflicts with production containers during parallel development |

**Critical**: Testing mode provides complete isolation from production containers, preventing conflicts during parallel development.

</details>

---

## ⚡ **Critical Caching Settings**

These settings have **massive impact** on Docker build performance. Misalignment across team members causes complete cache invalidation.

| Setting | Short Description | Format | Examples/Choices | Suggested Default |
|---------|-------------------|--------|------------------|-------------------|
| **`python_version`** | Python runtime version for all containers | Version number | `3.11`, `3.12`, `3.13` | `3.12` |
| **`airflow_version`** | Airflow runtime version | Astronomer version | `3.0.6`, `3.0.7`, `2.10.2` | `3.0.6` |
| **`postgres_version`** | PostgreSQL database version | Major version | `15`, `16`, `17` | `16` |

<details>
<summary><strong>python_version</strong> - Python Runtime Version Details <a id="python_version"></a></summary>

**Context**: The Python version forms the foundation of every Docker image in your project. This choice affects the base OS layer, system dependencies, package installation layers, and compatibility with your data processing libraries. Team alignment on this setting is absolutely critical for Docker layer sharing efficiency.

| Choice Value | Why This Works | Caching Impact | Isolation Impact |
|--------------|----------------|----------------|------------------|
| `3.11` | Mature stability for legacy compatibility requirements, well-tested ecosystem | **CRITICAL - Base image layer** - Different from team standard breaks ALL layer sharing for every build | **None** - Runtime choice only |
| `3.12`<br><div style="text-align:center">(default)</div> | Current stable release with performance improvements and modern features, optimal for new projects | **CRITICAL - Base image layer** - Foundation for ALL containers, must match across entire team | **None** - No operational isolation impact |
| `3.13` | Latest features and performance optimizations, cutting-edge development capabilities | **CRITICAL - Base image layer** - Different from team standard invalidates ALL cached layers | **None** - Runtime configuration |

**Team Alignment Critical**: All team members MUST use the same Python version or Docker layer sharing fails completely across the entire development workflow.

</details>

<details>
<summary><strong>airflow_version</strong> - Airflow Runtime Version Details <a id="airflow_version"></a></summary>

**Context**: Airflow version determines the orchestration runtime, available features, and compatibility with your DAG patterns. This choice affects the largest Docker layers (2GB+ base image), scheduler behavior, and API compatibility. Version coordination across your team is essential for build performance and feature consistency.

| Choice Value | Why This Works | Caching Impact | Isolation Impact |
|--------------|----------------|----------------|------------------|
| `2.10.2` | Mature Airflow 2.x series with proven stability for existing workflows | **CRITICAL - Largest base layers** - 2GB+ base image, version changes invalidate all Airflow-related layers | **None** - Runtime choice only |
| `3.0.6`<br><div style="text-align:center">(default)</div> | Latest stable Airflow 3.0 release with modern features and performance improvements | **CRITICAL - Largest base layers** - Must align with team for sharing 2GB+ of cached layers | **None** - No isolation impact |
| `3.0.7` | Newest features and fixes, requires coordinated team upgrade for optimal caching | **CRITICAL - Major base layers** - Version changes break ALL Airflow-related layer sharing across team | **None** - Runtime configuration |

**Version Coordination**: Team must coordinate Airflow version changes to maintain Docker layer sharing efficiency across all projects.

</details>

<details>
<summary><strong>postgres_version</strong> - PostgreSQL Database Version Details <a id="postgres_version"></a></summary>

**Context**: PostgreSQL version affects database container initialization, extension compatibility, and SQL feature availability. While having less cache impact than Python or Airflow, version consistency still matters for database schema compatibility and initialization script caching.

| Choice Value | Why This Works | Caching Impact | Isolation Impact |
|--------------|----------------|----------------|------------------|
| `15` | Proven stability for environments requiring PostgreSQL 15 compatibility | **Medium - Database layers** - Database container initialization and extension installation layers | **None** - Database runtime only |
| `16`<br><div style="text-align:center">(default)</div> | Current stable release with good balance of features, performance, and stability | **Medium - Database layers** - Database initialization, extension, and configuration layers | **None** - No operational isolation |
| `17` | Latest features and performance improvements for cutting-edge database capabilities | **Medium - Database layers** - Different version affects database setup and extension layers | **None** - Database configuration |

**Stability Focus**: Version 16 provides good balance of features and stability for most data engineering workloads.

</details>

---

## 🔐 **Container Registry Configuration**

| Setting | Short Description | Format | Examples/Choices | Suggested Default |
|---------|-------------------|--------|------------------|-------------------|
| **`image_repo`** | Container registry URL pattern | Registry URL with templating | Azure, AWS, GCP, Docker Hub patterns | `registry.example.com/etl/{{ cookiecutter.customer_slug }}` |

<details>
<summary><strong>image_repo</strong> - Container Registry Configuration Details <a id="image_repo"></a></summary>

**Context**: The container registry pattern determines where your Docker images are stored, pushed, and pulled from. This choice affects build performance through layer sharing, deployment workflows, and team collaboration. Consistency across all team projects is critical for optimal Docker layer caching and operational efficiency.

| Example | Why This Works | Caching Impact | Isolation Impact |
|---------|----------------|----------------|------------------|
| `registry.example.com/etl/{{ cookiecutter.customer_slug }}`<br><div style="text-align:center">(default)</div> | Template placeholder requiring organization customization, follows standard ETL namespace pattern | **High - Registry namespace layers** - Registry paths create separate cache namespaces affecting layer sharing | **None** - Registry configuration |
| `yourregistry.azurecr.io/data-eng/{{ cookiecutter.customer_slug }}` | Azure-specific pattern with data engineering namespace, enables Azure-integrated workflows | **High - Registry namespace layers** - Consistent pattern enables cross-project layer sharing within Azure ecosystem | **None** - No operational isolation |
| `123456789.dkr.ecr.us-east-1.amazonaws.com/etl/{{ cookiecutter.customer_slug }}` | AWS ECR with specific region and account, integrates with AWS deployment pipelines | **High - Registry namespace layers** - Must be consistent across team for optimal layer caching performance | **None** - Registry location only |
| `gcr.io/your-project/data-eng/{{ cookiecutter.customer_slug }}` | Google Container Registry with project-specific namespace and data engineering focus | **High - Registry namespace layers** - Registry consistency critical for Docker layer sharing efficiency | **None** - No isolation impact |
| `yourorg/{{ cookiecutter.customer_slug }}-etl` | Docker Hub pattern with organization namespace, suitable for open or private repositories | **High - Registry namespace layers** - Different registry patterns break cross-project layer sharing completely | **None** - Registry configuration |

**Consistency Critical**: All team projects must use the same registry pattern for Docker layer sharing to work effectively across your development workflow.

</details>

---

## 🏢 **Security and Enterprise Settings**

| Setting | Short Description | Format | Examples/Choices | Suggested Default |
|---------|-------------------|--------|------------------|-------------------|
| **`secrets_strategy`** | How secrets are managed in generated project | Choice list | `azure-key-vault`, `external-secrets-operator`, `env-vars` | `azure-key-vault` |
| **`executor`** | Airflow task execution strategy | Choice list | `KubernetesExecutor`, `CeleryExecutor`, `LocalExecutor` | `KubernetesExecutor` |
| **`enable_kerberos`** | Enable Kerberos authentication integration | Choice list | `no`, `yes` | `no` |
| **`license`** | License for the generated project | Choice list | `Proprietary`, `MIT`, `Apache-2.0` | `Proprietary` |

<details>
<summary><strong>secrets_strategy</strong> - Secrets Management Strategy Details <a id="secrets_strategy"></a></summary>

**Context**: Secrets management strategy determines how your project handles sensitive data like database credentials, API keys, and service account tokens. This choice affects security posture, operational complexity, and integration with your organization's identity management systems.

| Choice Value | Why This Works | When to Use | Caching Impact | Isolation Impact |
|--------------|----------------|-------------|----------------|------------------|
| `azure-key-vault`<br><div style="text-align:center">(default)</div> | Enterprise-grade secrets management with managed identity integration and audit trails | Azure cloud environments requiring enterprise security compliance and centralized secrets management | **None** - Runtime configuration only, no build layer impact | **None** - Security configuration |
| `external-secrets-operator` | Kubernetes-native secrets management supporting multiple secret backends with automated sync | Kubernetes environments requiring multi-cloud secret management or complex secret workflows | **None** - Runtime configuration with no caching impact | **None** - No operational isolation |
| `env-vars` | Simple environment variable based secrets for development and testing scenarios only | Development environments only, never use in production due to security limitations | **None** - Runtime configuration affecting no build layers | **None** - Configuration choice only |

**Security Note**: env-vars should only be used for development. Production environments should use proper secrets management systems.

</details>

<details>
<summary><strong>executor</strong> - Airflow Task Execution Strategy Details <a id="executor"></a></summary>

**Context**: The Airflow executor determines how tasks are executed, affecting scalability, resource isolation, and operational complexity. This choice impacts your system's ability to handle concurrent workloads, resource allocation strategies, and failure isolation patterns.

| Choice Value | Why This Works | When to Use | Caching Impact | Isolation Impact |
|--------------|----------------|-------------|----------------|------------------|
| `KubernetesExecutor`<br><div style="text-align:center">(default)</div> | Each task runs in separate Kubernetes pods providing maximum isolation and dynamic scaling | Scalable production environments requiring resource isolation, dynamic scaling, and cloud-native operations | **None** - Runtime executor configuration only | **High** - Complete task isolation with separate pods and resource limits |
| `CeleryExecutor` | Distributed task execution using Celery workers for horizontal scaling with shared infrastructure | Existing Celery infrastructure, traditional scaling patterns, or environments requiring persistent workers | **None** - Runtime configuration with no build impact | **Medium** - Tasks share worker nodes with process-level isolation |
| `LocalExecutor` | Tasks execute on the scheduler machine using local processes for simplicity | Development environments, small workloads, or single-machine deployments with limited scaling needs | **None** - Runtime execution choice only | **Low** - Tasks share scheduler resources with process separation |

**Scale Consideration**: KubernetesExecutor recommended for production workloads requiring scale and resource isolation.

</details>

<details>
<summary><strong>enable_kerberos</strong> - Kerberos Authentication Details <a id="enable_kerberos"></a></summary>

**Context**: Kerberos integration enables enterprise authentication workflows, affecting how your project authenticates with external systems, databases, and services. This choice impacts security architecture, dependency requirements, and integration complexity.

| Choice Value | Why This Works | When to Use | Caching Impact | Isolation Impact |
|--------------|----------------|-------------|----------------|------------------|
| `no`<br><div style="text-align:center">(default)</div> | Standard authentication using modern patterns like OAuth, service accounts, and managed identities | Most modern environments with cloud-native authentication systems and standard security practices | **None** - Runtime authentication configuration only | **None** - No operational impact |
| `yes` | Kerberos protocol integration for enterprise environments requiring legacy authentication compatibility | Enterprise environments with existing Kerberos infrastructure and legacy system integration requirements | **Low - Dependency layers** - May affect some authentication library installation layers | **None** - Authentication configuration |

**Enterprise Context**: Only enable if your organization specifically requires Kerberos authentication integration.

</details>

<details>
<summary><strong>license</strong> - Project License Details <a id="license"></a></summary>

**Context**: The project license determines legal usage rights, distribution permissions, and compliance requirements for your generated codebase. This choice affects intellectual property management, open source compliance, and distribution strategies.

| Choice Value | Why This Works | When to Use | Caching Impact | Isolation Impact |
|--------------|----------------|-------------|----------------|------------------|
| `Proprietary`<br><div style="text-align:center">(default)</div> | Internal company use with full control over distribution and intellectual property rights | Internal projects, confidential business logic, or commercially sensitive data processing workflows | **None** - Documentation metadata only | **None** - Legal framework choice |
| `MIT` | Open source with minimal restrictions allowing maximum flexibility for downstream usage | Open source projects prioritizing adoption, maximum permissiveness, and community contributions | **None** - License header generation only | **None** - No operational impact |
| `Apache-2.0` | Open source with patent protection providing legal safety for enterprise environments | Open source projects needing patent protection, enterprise adoption, and legal risk mitigation | **None** - Documentation and header generation only | **None** - Legal choice only |

**Distribution Intent**: Choose based on whether and how you plan to distribute the generated project code.

</details>

---

## 🌐 **Environment and Database Settings**

| Setting | Short Description | Format | Examples/Choices | Suggested Default |
|---------|-------------------|--------|------------------|-------------------|
| **`env_name`** | Default environment name for configuration | Choice list | `dev`, `int`, `qa`, `prod` | `dev` |
| **`local_domain`** | Domain for local development | Domain format | `localhost`, `local.dev`, `dev.company.com` | `localhost` |
| **`db_user`** | Default database username | String | `postgres`, `airflow`, `etl_user` | `postgres` |
| **`db_password`** | Default database password | String | `postgres`, `password123` | `postgres` |

<details>
<summary><strong>env_name</strong> - Default Environment Configuration Details <a id="env_name"></a></summary>

**Context**: The default environment name sets the initial Hydra configuration context, affecting logging levels, debug settings, performance optimizations, and monitoring configurations. This choice establishes the baseline operational behavior for your project.

| Choice Value | Why This Works | When to Use | Caching Impact | Isolation Impact |
|--------------|----------------|-------------|----------------|------------------|
| `dev`<br><div style="text-align:center">(default)</div> | Development-focused settings with verbose logging, debug capabilities, and rapid iteration features | Local development workflows prioritizing debugging capabilities and development productivity | **None** - Runtime environment configuration only | **None** - No operational isolation |
| `int` | Integration environment settings balancing debugging with external system connectivity | Integration testing requiring external system connections while maintaining diagnostic capabilities | **None** - Runtime configuration with no build impact | **None** - Environment configuration |
| `qa` | Quality assurance focused settings optimized for testing, validation, and quality metrics | QA testing workflows requiring production-like behavior with enhanced testing and validation features | **None** - Runtime environment choice only | **None** - No isolation impact |
| `prod` | Production-optimized settings with performance focus, minimal logging, and monitoring integration | Production deployments prioritizing performance, stability, and operational monitoring | **None** - Runtime configuration affecting no caching layers | **None** - Environment choice |

**Default Impact**: Sets the default Hydra environment configuration - can be overridden at runtime.

</details>

<details>
<summary><strong>local_domain</strong> - Local Development Domain Details <a id="local_domain"></a></summary>

**Context**: The local domain configures hostname resolution and service discovery for development environments, affecting how services communicate and how developers access local resources during development and testing workflows.

| Example | Why This Works | When to Use | Caching Impact | Isolation Impact |
|---------|----------------|-------------|----------------|------------------|
| `localhost`<br><div style="text-align:center">(default)</div> | Standard local development using localhost for simple, predictable service access | Standard development workflows without custom domain requirements or DNS configurations | **None** - Development configuration only | **None** - Local networking choice |
| `local.dev` | Custom local domain providing organized namespace for multiple services and projects | Development environments with multiple services requiring organized DNS namespace management | **None** - Runtime networking configuration only | **None** - No operational impact |
| `dev.company.com` | Company-specific domain enabling integration with corporate DNS and certificate management | Corporate development environments requiring integration with company infrastructure and security policies | **None** - Local networking configuration with no caching impact | **None** - Domain configuration |

**Development Focus**: Configures local service discovery and development environment networking.

</details>

<details>
<summary><strong>db_user</strong> and <strong>db_password</strong> - Database Credentials Details <a id="db_credentials"></a></summary>

**Context**: Default database credentials provide initial authentication for development databases, enabling immediate project startup while supporting eventual migration to proper secrets management for production deployments.

| Example | Why This Works | When to Use | Caching Impact | Isolation Impact |
|---------|----------------|-------------|----------------|------------------|
| `postgres` / `postgres`<br><div style="text-align:center">(default)</div> | Standard PostgreSQL defaults providing immediate development environment functionality | Development environments requiring immediate database access without additional configuration complexity | **None** - Runtime database configuration only | **None** - Authentication choice |
| `airflow` / `custom_password` | Airflow-specific database user with appropriate permissions and custom security | Development environments requiring role-based database access and custom permission structures | **None** - Runtime authentication configuration only | **None** - No operational isolation |
| `etl_user` / `secure_password` | ETL-focused user account with specific permissions for data processing workflows | Development environments simulating production-like database access patterns and security models | **None** - Runtime database authentication only | **None** - Authentication configuration |

**Security Warning**: These are development defaults only. Production environments should use proper secrets management systems.

</details>

---

## 📝 **Organizational and Documentation Settings**

| Setting | Short Description | Format | Examples/Choices | Suggested Default |
|---------|-------------------|--------|------------------|-------------------|
| **`author_name`** | Team/person credited in generated documentation | Free text | `Data Engineering Team`, `Acme Analytics Team` | `Data Engineering Team` |
| **`company_domain`** | Company domain used in configurations and documentation | Domain format | `myco.com`, `acme.com`, `datacompany.io` | `myco.com` |
| **`high_label`** | Security classification label for sensitive data | Free text | `high`, `sensitive`, `confidential`, `internal` | `high` |

<details>
<summary><strong>author_name</strong>, <strong>company_domain</strong>, <strong>high_label</strong> - Organizational Settings Details <a id="organizational_settings"></a></summary>

**Context**: Organizational settings establish institutional identity, security classification, and documentation attribution throughout your generated project, affecting compliance, branding, and operational clarity across your data engineering workflows.

| Setting | Example | Why This Works | When to Use | Caching Impact | Isolation Impact |
|---------|---------|----------------|-------------|----------------|------------------|
| **`author_name`** | `Data Engineering Team`<br><div style="text-align:center">(default)</div> | Standard team attribution providing clear ownership and contact information in project documentation | Standard team-based projects requiring clear ownership attribution and organizational accountability | **None** - Documentation metadata only | **None** - Documentation choice |
| `author_name` | `Acme Analytics Team` | Organization-specific team identity reflecting actual team structure and corporate branding | Custom organizational structures requiring specific team identification and institutional branding | **None** - Documentation generation only | **None** - No operational impact |
| **`company_domain`** | `myco.com`<br><div style="text-align:center">(default)</div> | Template placeholder requiring organizational customization for proper corporate identification | Template default requiring replacement with actual organizational domain for proper configuration | **None** - Configuration metadata only | **None** - Domain identification |
| `company_domain` | `acme.com` | Real organizational domain enabling proper corporate integration and service configuration | Production environments requiring actual corporate domain integration for services and documentation | **None** - Configuration and documentation only | **None** - No isolation impact |
| **`high_label`** | `high`<br><div style="text-align:center">(default)</div> | Standard security classification providing baseline data sensitivity labeling | Standard security environments requiring basic data classification and sensitivity marking | **None** - Security labeling metadata only | **None** - Classification choice |
| `high_label` | `sensitive` | Organization-specific security classification reflecting actual corporate data governance policies | Corporate environments with specific data classification requirements and compliance mandates | **None** - Documentation and labeling only | **None** - No operational isolation |

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

**Context**: Auto-generated naming values provide consistent, predictable naming patterns derived from your customer_slug, ensuring organizational consistency and eliminating naming conflicts across your project ecosystem.

| Setting | Example | Why This Works | When to Use | Caching Impact | Isolation Impact |
|---------|---------|----------------|-------------|----------------|------------------|
| **`db_name`** | `customer_analytics_etl`<br><div style="text-align:center">(auto-generated)</div> | Database naming convention using underscores with ETL suffix, following PostgreSQL identifier standards | Always use auto-generation for consistent database naming across all projects and environments | **None** - Runtime database configuration only | **None** - Database naming choice |
| **`project_name`** | `Customer Analytics ETL Project`<br><div style="text-align:center">(auto-generated)</div> | Human-readable title case formatting with ETL identification, suitable for documentation and UI display | Always use auto-generation for consistent project identification and professional documentation | **None** - Documentation metadata only | **None** - No operational impact |
| **`project_slug`** | `customer-analytics-etl`<br><div style="text-align:center">(auto-generated)</div> | Extended slug with ETL suffix maintaining kebab-case format for technical identifier consistency | Always use auto-generation for consistent technical naming and container identification | **None** - Container naming affecting final layers only | **None** - Naming convention choice |

**Recommendation**: Leave these as auto-generated unless you have specific requirements to override the default logic.

</details>

<details>
<summary><strong>runtime_tag</strong> - Auto-Generated Runtime Tag Details <a id="runtime_tag"></a></summary>

**Context**: Runtime tag is automatically derived from your airflow_version choice to ensure perfect alignment between Airflow runtime and Astronomer base image versions. This eliminates the critical configuration trap where mismatched versions cause 5-10 minute cache penalties on every Docker build.

| Airflow Version | Runtime Tag | Why This Works | When to Use | Caching Impact | Isolation Impact |
|-----------------|-------------|----------------|-------------|----------------|------------------|
| `2.10.2` | `2.10-1`<br><div style="text-align:center">(auto-generated)</div> | Automatically matched runtime preventing version misalignment and ensuring optimal Docker layer caching | Always use auto-generation - prevents critical caching performance traps | **CRITICAL** - Auto-alignment prevents 5-10 minute cache penalty per build | **None** - Runtime alignment choice |
| `3.0.6` | `3.0-10`<br><div style="text-align:center">(auto-generated)</div> | Perfect version alignment ensuring maximum Docker layer sharing and build performance optimization | Always use auto-generation - eliminates manual configuration errors | **CRITICAL** - Auto-alignment ensures proper layer caching across team | **None** - No isolation impact |
| `3.0.7` | `3.0-11`<br><div style="text-align:center">(auto-generated)</div> | Precise runtime matching preventing cache misses and ensuring consistent build performance | Always use auto-generation - functional by design prevents misalignment | **CRITICAL** - Auto-alignment prevents complete cache invalidation | **None** - Runtime configuration |

**Functional by Design**: runtime_tag is automatically derived from airflow_version to eliminate configuration traps and ensure proper cache alignment.

</details>

<details>
<summary><strong>year</strong> - Auto-Generated Year Details <a id="year"></a></summary>

**Context**: The current year is automatically generated for license headers and copyright notices, ensuring accurate legal documentation without manual maintenance or configuration drift.

| Example | Why This Works | When to Use | Caching Impact | Isolation Impact |
|---------|----------------|-------------|----------------|------------------|
| `2025`<br><div style="text-align:center">(auto-generated)</div> | Always reflects current year for accurate legal documentation and license header generation | Always use auto-generation for accuracy and automatic maintenance of legal documentation | **None** - Documentation metadata only | **None** - Legal documentation choice |

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

  # Container registry configuration
  image_repo: "your-registry.com/data-eng/{{ cookiecutter.customer_slug }}"

  # Security and enterprise settings
  secrets_strategy: "azure-key-vault"
  executor: "KubernetesExecutor"
  enable_kerberos: "no"
  license: "Proprietary"

  # Environment and database settings
  env_name: "dev"
  local_domain: "localhost"
  db_user: "postgres"
  db_password: "postgres"

  # Organizational and documentation settings
  author_name: "Your Data Engineering Team"
  company_domain: "yourcompany.com"
  high_label: "high"
```

**Next Step**: Use this understanding to customize your organizational defaults and streamline project generation for your team.