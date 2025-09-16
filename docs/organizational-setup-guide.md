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

She customizes the template's `cookiecutter.json` to set organizational choices and defaults:

```json
{
  "python_version": [
    "3.12.11",  // First = default: company standard with security patches
    "3.11.13",  // Legacy project compatibility, stable patches
    "3.13.2",   // Early adopter stable option
    "3.13.7"    // Latest early adopter option
  ],
  "airflow_version": [
    "3.0.6",   // First = default: current stable
    "3.0.7",   // Bug fixes for specific teams
    "2.10.2"   // Legacy system compatibility
  ],
  "postgres_version": [
    "16",      // First = default: company standard
    "15",      // Legacy system support
    "17"       // Cutting-edge features
  ]
}
```

*Sarah's reasoning: "This gives developers appropriate choices while ensuring cache sharing within each technology stack. The first option becomes the default, so most projects get our standards automatically."*

**Why constrained choices**: → [See Critical Caching Settings details](template-configuration.md#-critical-caching-settings)

### **Decision 2: Organizational Infrastructure Choices**

*Sarah thinks: "For infrastructure and security settings, some things I'll hard-code (like our container registry), others I'll provide as constrained choices with our standard as the default."*

She customizes the organizational infrastructure in `cookiecutter.json`:

```json
{
  // Hard-coded organizational infrastructure
  "image_repo": "acme.azurecr.io/data-eng/{{ cookiecutter.customer_slug }}",
  "company_domain": "acme.com",
  "license": "Proprietary",  // Internal company code

  // Constrained choices (first = default)
  "secrets_strategy": [
    "azure-key-vault",         // First = default: company standard
    "external-secrets-operator", // K8s environments
    "env-vars"                 // Development only
  ],
  "executor": [
    "KubernetesExecutor",      // First = default: we have AKS clusters
    "CeleryExecutor",          // High-throughput scenarios
    "LocalExecutor"            // Development/testing
  ],
  "enable_kerberos": [
    "no",                      // First = default: modern auth
    "yes"                      // Legacy system compatibility
  ]
}
```

*Sarah's reasoning: "I hard-code things that never change (our Azure infrastructure), but provide choices for things where different projects might have different needs while staying within our approved options."*

**Note**: Cookiecutter provides single-select choices only. For scenarios requiring multiple selections (like supporting multiple executors in one project), that would be handled in the generated project's runtime configuration, not in the template generation step.

### **Decision 3: Development Environment Settings**

*Sarah thinks: "For environment workflows, I want to give teams options but start with dev as the sensible default. Database settings can be hard-coded for simplicity."*

She sets up the environment configuration in `cookiecutter.json`:

```json
{
  // Environment workflow choices
  "env_name": [
    "dev",    // First = default: most projects start here
    "prod",   // Production deployments
    "int",    // Integration testing
    "qa"      // QA environments
  ],

  // Hard-coded development defaults
  "local_domain": "localhost",   // Keep it simple
  "db_user": "postgres",         // Standard dev defaults
  "db_password": "postgres"      // Dev environments only
}
```

*Sarah's reasoning: "Environment names should be choices since teams deploy to different stages, but dev database credentials can be hard-coded since they're only for local development."*

---

## 🧪 **Step 3: Sarah Tests Her Configuration**

```bash
# Generate a test project (developers answer ~7 prompts total)
cookiecutter .

# Core prompts:
customer_slug: customer-segmentation
description: Customer behavior analysis pipeline
deployment_mode: 1 (production - default)
airflow_version: 1 (3.0.6 - default)
author_name: Sarah Johnson
# ... other prompts with sensible defaults

# Verify the results
cd customer-segmentation-etl
grep "acme.azurecr.io" .devcontainer/compose.yaml
grep "3.12.11" Dockerfile.airflow
```

*Sarah's reaction: "Perfect! Developers get appropriate choices, most defaults align with our standards, and the repo creation process is straightforward even with a few prompts."*

---

## 💾 **Step 4: Sarah Commits the Configuration**

```bash
git add cookiecutter.json
git commit -m "feat: Customize template for Acme Analytics

- Set organizational technology choices with company standards as defaults
- Configure acme.azurecr.io registry and company domain
- Provide constrained choices for secrets, executor, and environment options
- Optimal Docker caching through consistent version defaults
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

Use our customized template:

```bash
cookiecutter https://github.com/acme/data-eng-template
```

You'll be prompted for ~7 configuration choices:
1. **customer_slug**: Your project identifier (kebab-case)
2. **description**: Brief project summary
3. **deployment_mode**: Choose "production" for permanent projects, "testing" for experiments
4. **airflow_version**: Usually accept default (3.0.6) unless you need specific features
5. **author_name**: Your name or team name
6. **secrets_strategy**: Usually accept default (azure-key-vault) unless using env-vars for dev
7. **executor**: Usually accept default (KubernetesExecutor) unless you need local testing

## Organizational Standards Are Built-In

- ✅ Python 3.12.11 (company standard with patches)
- ✅ Images push to acme.azurecr.io/data-eng/
- ✅ Azure Key Vault for secrets (default choice)
- ✅ Kubernetes executor for scale (default choice)
- ✅ Company domain and registry configured
- ✅ Optimal Docker caching through consistent defaults

## 📊 **Results: Sarah's Success Metrics**

**After 2 weeks with the new setup:**

- ✅ **Build times**: Dropped from 15+ minutes to under 2 minutes (Docker layer sharing working)
- ✅ **Configuration consistency**: Zero "works on my machine" issues
- ✅ **Developer velocity**: 30% faster project onboarding
- ✅ **Standards compliance**: 100% of projects use company security standards
- ✅ **Developer satisfaction**: Team appreciates the guided choices with good defaults

*Sarah's conclusion: "This was the best investment we made in developer productivity this quarter."*

---

## ❓ **Questions?**

See the [Template Configuration Guide](template-configuration.md) for technical details on any setting.

---

## 🎯 ***Your*** **Turn: Customize for Your Organization**

**Step 1**: Fork or clone the template

**Step 2**: Edit `cookiecutter.json` to set your organizational choices and defaults

**Step 3**: Test with a sample project

**Step 4**: Commit and share with your team

### **Simple Customization Process**

Edit your fork's `cookiecutter.json` to reflect your organizational standards:

```json
{
  // Technology choices (first item = default)
  "python_version": [
    "3.12.11",   // Your primary standard (becomes default)
    "3.11.13",   // Legacy compatibility option
    "3.13.7"     // Early adopter option
  ],

  // Hard-coded organizational infrastructure
  "image_repo": "your-registry.com/data-eng/{{ cookiecutter.customer_slug }}",
  "company_domain": "your-company.com",
  "license": "Proprietary",

  // Security choices (first item = default)
  "secrets_strategy": [
    "azure-key-vault",    // Your default
    "env-vars"            // Development option
  ]
}
```

### **Key Principles**

- **First choice = default**: Cookiecutter automatically uses the first item in each array as the default
- **Constrained choices**: Provide 2-4 organizational-approved options instead of unlimited freedom
- **Hard-code fixed values**: Set truly organizational constants (registry, domain) as single values
- **Array for flexibility**: Use arrays when teams might need different options for different projects

### **Benefits of This Approach**
- ✅ **Simpler**: Just one file to edit (cookiecutter.json)
- ✅ **Native**: Uses cookiecutter's built-in choice and default functionality
- ✅ **Cache sharing**: Projects using same versions share Docker layers
- ✅ **Clear guidance**: Developers see exactly what's approved during repo creation
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