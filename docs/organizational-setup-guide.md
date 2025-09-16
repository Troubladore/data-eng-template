# Organizational Setup Guide

## 📋 **The Philosophy Behind Organizational Setup**

This template contains numerous configurable attributes within both the cookiecutter system and the Hydra configuration framework that supports generated projects. The key insight is that **most of these decisions should be made once at the organizational or departmental level**, rather than forcing individual developers to repeatedly make the same choices.

Rather than having each developer manage configuration conflicts individually, **we declare these settings centrally and apply them globally** at the developer workstation level. For critical settings that affect Docker layer caching, organizations should provide *constrained choices* rather than unlimited freedom - balancing implementation flexibility vs best practices and operational sustainability. This prevents the accumulation of configuration debt and ensures consistent, conflict-free environments across your entire team.

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

### **Decision 1: Technology Standards and Choice Control**

*Sarah thinks: "My team wastes 20-30 minutes daily on Docker builds. If everyone uses different Python versions, we can't share any cached layers. But I also need to balance standardization with giving my team options for different project needs."*

**Sarah's Technology Assessment:**
- **Python 3.12.11**: Company standard with latest security patches, but some legacy projects need 3.11.13, and early adopters want 3.13 versions for performance testing
- **Airflow 3.0.6**: Current stable, but 3.0.7 has bug fixes some teams need, and 2.10.2 for legacy compatibility
- **PostgreSQL 16**: Our standard, but 15 for legacy systems and 17 for teams wanting cutting-edge features

She modifies the template's `cookiecutter.json` to set organizational choices:

```json
{
  "python_version": [
    "3.12.11",  // Default: company standard with security patches
    "3.11.13",  // Legacy project compatibility, stable patches
    "3.13.2",   // Early adopter stable option
    "3.13.7"    // Latest early adopter option
  ],
  "airflow_version": [
    "3.0.6",   // Default: current stable
    "3.0.7",   // Bug fixes for specific teams
    "2.10.2"   // Legacy system compatibility
  ],
  "postgres_version": [
    "16",      // Default: company standard
    "15",      // Legacy system support
    "17"       // Cutting-edge features
  ]
}
```

Then she creates `acme-defaults.yaml` to set organizational defaults from those choices:

```yaml
default_context:
  # Technology standards (first choice from each array becomes default)
  python_version: "3.12.11"        # Company-wide Python standard
  airflow_version: "3.0.6"         # Latest stable for new features
  postgres_version: "16"           # Modern database features
```

*Sarah's reasoning: "This gives developers appropriate choices while ensuring cache sharing within each technology stack. The first option becomes the default, so most projects get our standards automatically."*

**Why constrained choices**: → [See Critical Caching Settings details](template-configuration.md#-critical-caching-settings)

### **Decision 2: Organizational Infrastructure Choices**

*Sarah thinks: "Now I need to set up choices for our infrastructure and security settings. Some things we hard-code (like our container registry), others we give constrained options."*

**Organizational choices in cookiecutter.json** (already configured):
```json
{
  "secrets_strategy": [
    "azure-key-vault",         // Default: company standard
    "external-secrets-operator", // K8s environments
    "env-vars"                 // Development only
  ],
  "executor": [
    "KubernetesExecutor",      // Default: we have AKS clusters
    "CeleryExecutor",          // High-throughput scenarios
    "LocalExecutor"            // Development/testing
  ],
  "enable_kerberos": [
    "no",                      // Default: modern auth
    "yes"                      // Legacy system compatibility
  ]
}
```

**Organizational defaults in acme-defaults.yaml**:
```yaml
default_context:
  # Hard-coded organizational infrastructure
  image_repo: "acme.azurecr.io/data-eng/{{ cookiecutter.customer_slug }}"
  company_domain: "acme.com"

  # Default choices (teams can override with --no-input=false)
  secrets_strategy: "azure-key-vault"  # Company standard
  executor: "KubernetesExecutor"       # We have AKS clusters
  enable_kerberos: "no"                # We use modern auth
  license: "Proprietary"               # Internal company code
```

*Sarah's reasoning: "I hard-code things that never change (our Azure infrastructure), but provide choices for things where different projects might have different needs while staying within our approved options."*

**Note**: Cookiecutter provides single-select choices only. For scenarios requiring multiple selections (like supporting multiple executors in one project), that would be handled in the generated project's runtime configuration, not in the template generation step.

### **Decision 3: Development Environment Choices**

*Sarah thinks: "For environment workflows, I want to give teams options but start with dev as the sensible default. Database settings can be hard-coded for simplicity."*

**Environment choices in cookiecutter.json** (already configured):
```json
{
  "env_name": [
    "dev",    // Default: most projects start here
    "prod",   // Production deployments
    "int",    // Integration testing
    "qa"      // QA environments
  ]
}
```

**Development defaults in acme-defaults.yaml**:
```yaml
default_context:
  # Environment workflow default
  env_name: "dev"                      # Start in development mode

  # Hard-coded development defaults
  local_domain: "localhost"            # Keep it simple
  db_user: "postgres"                  # Standard defaults
  db_password: "postgres"              # Dev environments only
```

*Sarah's reasoning: "Environment names should be choices since teams deploy to different stages, but dev database credentials can be hard-coded since they're only for local development."*

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

## 📊 **Results: Sarah's Success Metrics**

**After 2 weeks with the new setup:**

- ✅ **Build times**: Dropped from 15+ minutes to under 2 minutes (Docker layer sharing working)
- ✅ **Configuration consistency**: Zero "works on my machine" issues
- ✅ **Developer velocity**: 30% faster project onboarding
- ✅ **Standards compliance**: 100% of projects use company security standards
- ✅ **Developer satisfaction**: Team loves the 3-question simplicity

*Sarah's conclusion: "This was the best investment we made in developer productivity this quarter."*

---

## ❓ **Questions?**

See the [Template Configuration Guide](template-configuration.md) for technical details on any setting.

---

## 🎯 ***Your*** **Turn: Customize for Your Organization**

**Step 1**: Fork or clone the template

**Step 2**: **Set Organizational Technology Choices** - Edit `cookiecutter.json` to define your supported versions:

```json
{
  "python_version": [
    "3.12.11",   // Your primary standard (becomes default)
    "3.11.13",   // Legacy compatibility with patches
    "3.13.7"     // Early adopter latest option
  ],
  "airflow_version": [
    "3.0.6",     // Your primary standard (becomes default)
    "3.0.7"      // Add other versions for specific needs
  ],
  "postgres_version": [
    "16",        // Your primary standard (becomes default)
    "15"         // Add for legacy compatibility if needed
  ]
}
```

**Step 3**: **Set Organizational Defaults** - Copy `company-template-defaults.yaml` to `your-org-defaults.yaml`

**Step 4**: Make your configuration decisions (use the [Template Configuration Guide](template-configuration.md) for detailed explanations)

**Step 5**: Test with a sample project

**Step 6**: Commit and share with your team

### **Customizing Technology Choices**

**Key Principle**: The first item in each choice array becomes the default. Organize your choices by priority:

```json
"python_version": [
  "3.12.11",     // ✅ Default - most projects get this automatically
  "3.11.13",     // Legacy support option with patches
  "3.13.2",      // Stable early adopter option
  "3.13.7"       // Latest early adopter option
]
```

**Benefits of Constrained Choices**:
- ✅ **Cache sharing**: Projects using same versions share Docker layers
- ✅ **Prevents invalid combinations**: No accidental unsupported versions
- ✅ **Easy organizational control**: Just edit the template's cookiecutter.json
- ✅ **Clear options**: Developers see exactly what's supported
- ✅ **Default compliance**: Most projects automatically use organizational standards

### **Key Configuration Areas to Consider**

| Configuration Area | Your Decision | Where to Learn More |
|--------------------|---------------|-------------------|
| **Python/Airflow versions** | What has your org standardized on? | [Critical Caching Settings →](template-configuration.md#-critical-caching-settings) |
| **Container registry** | Azure ACR? AWS ECR? GCP? Docker Hub? | [Container Registry Configuration →](template-configuration.md#-container-registry-configuration) |
| **Security strategy** | Key Vault? External Secrets? Simple env vars? | [Security Settings →](template-configuration.md#-security-and-enterprise-settings) |
| **Kubernetes setup** | Do you have K8s clusters? | [Executor Configuration →](template-configuration.md#-security-and-enterprise-settings) |
| **Company branding** | Team name, domain, classification levels? | [Organizational Settings →](template-configuration.md#-organizational-and-documentation-settings) |

**For detailed explanations of every setting, caching implications, and technical trade-offs**: → **[Template Configuration Guide](template-configuration.md)**

---

## ✅ **Success Criteria**

After completing your organizational setup, your team should have:

- ✅ **Sub-2 minute rebuilds** for code changes (Docker layer sharing working)
- ✅ **3-question simplicity** for developers (only project-specific questions)
- ✅ **Automatic compliance** with organizational standards (security, registry, branding)
- ✅ **Persistent customizations** that survive template updates
- ✅ **Consistent environments** across all team members

Your template is now configured and ready for your team to deploy new repos following the [Getting Started Guide](getting-started.md).