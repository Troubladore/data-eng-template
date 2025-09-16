# Organizational Setup Guide

## 📋 **The Philosophy Behind Organizational Setup**

This template contains numerous configurable attributes within both the cookiecutter system and the Hydra configuration framework that supports generated projects. The key insight is that **most of these decisions should be made once at the organizational or departmental level**, rather than forcing individual developers to repeatedly make the same choices.

Rather than having each developer manage configuration conflicts individually, **we declare these settings centrally and apply them globally** at the developer workstation level. This prevents the accumulation of configuration debt and ensures consistent, conflict-free environments across your entire team.

After this setup, individual developers can focus on building data pipelines rather than wrestling with configuration decisions and environment conflicts.

---

## 🏢 **Walkthrough: Setting Up Acme Analytics**

*Let's follow Sarah, the Data Engineering Team Lead at Acme Analytics, as she sets up organizational defaults for her team of 8 data engineers.*

### **Sarah's Infrastructure Assessment**

**Sarah starts by reviewing Acme's existing infrastructure:**

- **Cloud Platform**: Azure (standardized across company)
- **Container Registry**: Azure Container Registry (`acme.azurecr.io`)
- **Security**: Azure Key Vault for secrets management
- **Kubernetes**: AKS clusters for production workloads
- **Team Standards**: Python 3.12, standardized linting rules

**Her Goal**: Configure the template so her team only answers the 3 essential questions (project name, description, deployment mode) while automatically inheriting all of Acme's organizational standards.

---

## 🔧 **Step 1: Clone and Configure Template**

Sarah starts by forking the template for Acme Analytics:

```bash
# Sarah forks the template to her organization
git clone https://github.com/acme/data-eng-template.git
cd data-eng-template
git checkout -b acme-config

# Copy the template to customize
cp company-template-defaults.yaml acme-defaults.yaml
```

---

## 🎯 **Step 2: Sarah's Configuration Decisions**

### **Decision 1: Critical Caching Settings**

*Sarah thinks: "My team wastes 20-30 minutes daily on Docker builds. If everyone uses different Python versions, we can't share any cached layers."*

She opens `acme-defaults.yaml` and sets the foundation:

```yaml
default_context:
  # Critical: Everyone at Acme uses these exact versions
  python_version: "3.12"        # Company-wide Python standard
  airflow_version: "3.0.6"      # Latest stable for new features
  postgres_version: "16"        # Modern database features
```

**Why these choices**: → [See Critical Caching Settings details](template-configuration.md#critical-caching-settings)

### **Decision 2: Acme's Container Registry**

*Sarah thinks: "We're an Azure shop. All our images should go to our ACR, and follow our naming conventions."*

```yaml
default_context:
  image_repo: "acme.azurecr.io/data-eng/{{ cookiecutter.customer_slug }}"
```

**Registry decision factors**: → [See Container Registry Configuration details](template-configuration.md#container-registry-configuration)

### **Decision 3: Security Strategy**

*Sarah thinks: "We're already using Azure Key Vault company-wide. Development can use env vars, but production must use Key Vault."*

```yaml
default_context:
  secrets_strategy: "azure-key-vault"  # Company standard
  executor: "KubernetesExecutor"       # We have AKS clusters
  enable_kerberos: "no"                # We use modern auth
  license: "Proprietary"               # Internal company code
```

**Security choice rationale**: → [See Security and Enterprise Settings details](template-configuration.md#security-and-enterprise-settings)

### **Decision 4: Acme Organizational Identity**

*Sarah thinks: "Every generated project should reflect our team and company standards automatically."*

```yaml
default_context:
  author_name: "Acme Analytics Team"
  company_domain: "acme.com"
  high_label: "confidential"          # Acme's classification level
```

**Organizational settings**: → [See Organizational Settings details](template-configuration.md#organizational-and-documentation-settings)

### **Decision 5: Development Environment**

*Sarah thinks: "Most of our work starts in development mode, with localhost being the simplest for local work."*

```yaml
default_context:
  env_name: "dev"                      # Start in development mode
  local_domain: "localhost"            # Keep it simple
  db_user: "postgres"                  # Standard defaults
  db_password: "postgres"              # Dev environments only
```

**Environment choices**: → [See Environment and Database Settings details](template-configuration.md#environment-and-database-settings)

---

## 🧪 **Step 3: Sarah Tests Her Configuration**

```bash
# Generate a test project
cookiecutter . --config-file acme-defaults.yaml

# Answer only the 3 required prompts:
customer_slug: customer-segmentation
description: Customer behavior analysis pipeline
deployment_mode: production

# Verify the results
cd customer-segmentation-etl
grep "acme.azurecr.io" .devcontainer/compose.yaml
grep "Acme Analytics Team" pyproject.toml
```

*Sarah's reaction: "Perfect! The project has all our standards baked in, and my developers will only see 3 questions."*

---

## 💾 **Step 4: Sarah Commits the Configuration**

```bash
git add acme-defaults.yaml
git commit -m "feat: Add Acme Analytics organizational defaults

- Standardize Python 3.12 and Airflow 3.0.6 for optimal caching
- Configure acme.azurecr.io registry with data-eng namespace
- Set Azure Key Vault as security strategy
- Apply Acme Analytics branding and classification
"

git push origin acme-config
```

---

## 🚀 **Step 5: Team Rollout**

Sarah creates simple instructions for her team:

```bash
cat > ACME-TEAM-SETUP.md << 'EOF'
# Acme Analytics - Data Engineering Projects

## New Project Generation

Always use our organizational defaults:

```bash
cookiecutter https://github.com/acme/data-eng-template --config-file acme-defaults.yaml
```

You'll only be asked 3 questions:
1. **customer_slug**: Your project identifier (kebab-case)
2. **description**: Brief project summary
3. **deployment_mode**: Choose "production" for permanent projects, "testing" for experiments

## Everything Else is Pre-Configured

- ✅ Python 3.12 (matches company standard)
- ✅ Images push to acme.azurecr.io/data-eng/
- ✅ Azure Key Vault for secrets
- ✅ Kubernetes executor for scale
- ✅ Acme Analytics branding
- ✅ Optimal Docker caching across team

## Questions?

See the [Template Configuration Guide](template-configuration.md) for technical details on any setting.
EOF
```

---

## 📊 **Results: Sarah's Success Metrics**

**After 2 weeks with the new setup:**

- ✅ **Build times**: Dropped from 15+ minutes to under 2 minutes (Docker layer sharing working)
- ✅ **Configuration consistency**: Zero "works on my machine" issues
- ✅ **Developer velocity**: 30% faster project onboarding
- ✅ **Standards compliance**: 100% of projects use company security standards
- ✅ **Developer satisfaction**: Team loves the 3-question simplicity

*Sarah's conclusion: "This was the best investment we made in developer productivity this quarter."*

---

## 🎯 **Your Turn: Customize for Your Organization**

**Step 1**: Fork or clone the template
**Step 2**: Copy `company-template-defaults.yaml` to `your-org-defaults.yaml`
**Step 3**: Make your configuration decisions (use the [Template Configuration Guide](template-configuration.md) for detailed explanations)
**Step 4**: Test with a sample project
**Step 5**: Commit and share with your team

### **Key Configuration Areas to Consider**

| Configuration Area | Your Decision | Where to Learn More |
|--------------------|---------------|-------------------|
| **Python/Airflow versions** | What has your org standardized on? | [Critical Caching Settings →](template-configuration.md#critical-caching-settings) |
| **Container registry** | Azure ACR? AWS ECR? GCP? Docker Hub? | [Container Registry Configuration →](template-configuration.md#container-registry-configuration) |
| **Security strategy** | Key Vault? External Secrets? Simple env vars? | [Security Settings →](template-configuration.md#security-and-enterprise-settings) |
| **Kubernetes setup** | Do you have K8s clusters? | [Executor Configuration →](template-configuration.md#security-and-enterprise-settings) |
| **Company branding** | Team name, domain, classification levels? | [Organizational Settings →](template-configuration.md#organizational-and-documentation-settings) |

**For detailed explanations of every setting, caching implications, and technical trade-offs**: → **[Template Configuration Guide](template-configuration.md)**

---

## ✅ **Success Criteria**

After completing your organizational setup, your team should have:

- ✅ **Sub-2 minute rebuilds** for code changes (Docker layer sharing working)
- ✅ **3-question simplicity** for developers (only project-specific questions)
- ✅ **Automatic compliance** with organizational standards (security, registry, branding)
- ✅ **Persistent customizations** that survive template updates
- ✅ **Consistent environments** across all team members

**Next**: Your team can now follow the [Getting Started Guide](getting-started.md) knowing every project will be optimized for your organization.