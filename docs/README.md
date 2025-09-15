# Template Documentation

Documentation for the **Astronomer-powered Data Engineering Cookiecutter Template**.

## 📚 **Template Architecture & Requirements**

### **[Template Overview](TEMPLATE_OVERVIEW.md)**
High-level architecture, purpose, and production deployment pathway. **Start here** to understand what this template generates and why.

### **[Astronomer Architecture Requirements](ASTRONOMER_ARCHITECTURE_REQUIREMENTS.md)**
Comprehensive checklist of **production-grade features** that must be present in every generated project. This document outlines the migration imperatives driving the Astronomer-based architecture.

## 🛠️ **Template Development**

### **[Getting Started](GETTING_STARTED.md)**
How to use this cookiecutter template to generate new data engineering projects.

### **[Directory Structure](cookiecutter_directory_structure.md)**
Template file organization and cookiecutter variable usage.

## 🔍 **Key Design Imperatives**

This template was created to support **enterprise Astronomer production architecture** with these core requirements:

### **Multi-Cluster Production Support**
- **Standard Airflow clusters** for general workloads
- **High-performance clusters** for resource-intensive processing
- **Environment isolation**: Non-prod → Prod promotion pipeline

### **Enterprise Security & Compliance**
- **Azure Key Vault** integration for centralized secrets management
- **Side-car security implementations** for production compliance
- **Network isolation** with Traefik routing and production networking

### **Execution Model Flexibility**
- **Multiple executors**: KubernetesExecutor and CeleryExecutor support
- **Pre-configured queues**: Standard, high-memory, GPU, compute worker pools
- **KPO vs Queue-based execution**: Choice between container execution models

### **Development → Production Parity**
- **Container-first development**: DevContainer environment matches production runtime
- **CI/CD integration**: Automated container building and multi-environment deployment
- **Image artifact management**: Tagged, versioned deployments to Astronomer clusters

## 📋 **Generated Project Documentation**

Projects generated from this template include comprehensive documentation in their `/docs` directories:

- **Getting started guides**: Project-specific setup and usage
- **Deployment runbooks**: Production deployment procedures
- **Configuration guides**: Environment setup and secrets management
- **Architecture decisions**: Project-specific design choices and rationale

## 🎯 **Success Metrics**

This template succeeds when:
1. **Zero-config DevContainer startup**: `code .` → "Reopen in Container" → Full environment ready
2. **Production deployment ready**: All Astronomer architecture requirements satisfied
3. **Team consistency**: Identical development experience across all team projects
4. **Minimal production configuration**: Deploy to Astronomer clusters with minimal additional setup

---

**For generated project documentation**, refer to the `/docs` directory in your generated project. **This documentation focuses on the template itself** - how it works, what it generates, and why architectural decisions were made.