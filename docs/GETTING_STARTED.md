# Getting Started with Data Engineering Template

## 🎯 **Complete First-Time Setup Guide**

This guide walks you through setting up an optimized data engineering development environment from scratch.

### 📋 **Prerequisites Checklist**

#### ✅ **Required Tools**
- [ ] **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux) 
- [ ] **WSL2** (Windows users) - [Install Guide](https://docs.microsoft.com/en-us/windows/wsl/install)
- [ ] **Python 3.10+** - Check with `python --version`

#### ✅ **Install Development Tools**
```bash
# Install cookiecutter for template generation
pipx install cookiecutter

# Install DevContainer CLI (optional - VS Code also works)
npm install -g @devcontainers/cli
```

## 🚀 **Option 1: Optimized Setup (Recommended)**

### Step 1: Install Enhanced Development Tools
```bash
# Install with workstation optimization features (globally available)
pipx install devcontainer-service-manager[workstation]
```

### Step 2: One-Time Workstation Optimization  
```bash
# Configure your development environment for optimal performance
dcm-setup install --profile data-engineering

# Validate everything is working
dcm-setup validate
```

**What this does:**
- Sets up 149x faster Docker builds via intelligent caching
- Configures WSL2 for optimal performance (Windows users)
- Creates local Docker registry for cross-repository sharing
- Applies Git and shell optimizations

### Step 3: Generate Your First Project
```bash
# Navigate to where you keep projects (IMPORTANT for WSL2 users: use ~/repos/)
mkdir -p ~/repos && cd ~/repos

# Generate project from template
cookiecutter https://github.com/Troubladore/data-eng-template

# Navigate to your new project
cd your-awesome-project-name
```

### Step 4: Start Optimized Development Environment
```bash
# One command to set up everything optimally
./scripts/setup-development.sh
```

**This script automatically:**
- Installs project dependencies  
- Configures project-specific caching
- Starts Airflow and PostgreSQL services
- Validates the environment

### Step 5: Access Your Services
- **Airflow UI**: http://localhost:8081 (admin/admin)
- **PostgreSQL**: localhost:5432 (postgres/postgres)

## 🔧 **Option 2: Manual Setup**

If you prefer manual control or are troubleshooting:

### Step 1: Generate Project
```bash
cd ~/repos  # Or your preferred location
cookiecutter https://github.com/Troubladore/data-eng-template
cd your-project-name
```

### Step 2: Install Dependencies
```bash
# Install Python dependencies
uv sync

# Generate environment file
./scripts/export_env.sh > .env
```

### Step 3: Start Services
```bash
# Start Docker Compose services
cd .devcontainer
docker compose up -d
```

## 🪟 **Windows/WSL2 Specific Instructions**

### Critical Performance Setup
```bash
# 1. ALWAYS work in WSL2 filesystem (not Windows filesystem)
cd ~  # NOT /mnt/c/

# 2. Create repos directory in WSL2
mkdir -p ~/repos && cd ~/repos

# 3. Verify you're in the right place
pwd  # Should show /home/yourusername/repos (NOT /mnt/c/...)
```

### Docker Desktop Configuration
1. **Enable WSL2 Integration**: Docker Desktop → Settings → Resources → WSL Integration
2. **Allocate Resources**: 8GB+ RAM, 60GB+ disk space for optimal caching
3. **Enable BuildKit**: Set `DOCKER_BUILDKIT=1` environment variable

### Performance Validation
```bash
# Check if you're getting optimal performance
dcm-setup validate

# Should show:
# ✅ WSL2 detected
# ✅ File system performance: fast
# ✅ Docker integration working
```

## 🐛 **Troubleshooting Common Issues**

### "Builds are slow"
```bash
# Check file system location
pwd  # Must be in WSL2 filesystem, not /mnt/c/

# Move to WSL2 if needed
mkdir -p ~/repos
cd ~/repos
# Re-clone your repositories here
```

### "Registry won't start"
```bash
# Check what's using port 5000
sudo netstat -tuln | grep 5000

# Use automated troubleshooting
dcm-setup troubleshoot
```

### "Docker permission errors"
```bash
# Add your user to docker group (Linux/WSL2)
sudo usermod -aG docker $USER
# Logout and login again
```

### "Services won't start"
```bash
# Clean up any stuck resources
dcm-setup cleanup

# Verify Docker is running
docker version

# Check service status
dcm-cache status
```

## 🎉 **Success Validation**

After setup, you should have:

- ✅ **Fast builds**: Second builds complete in <1 second
- ✅ **Working services**: Airflow UI loads at http://localhost:8081
- ✅ **Database access**: Can connect to PostgreSQL
- ✅ **Cache sharing**: Builds are fast across all your data engineering projects

### Quick Test
```bash
# Generate a second project to test cache sharing
cd ~/repos
cookiecutter https://github.com/Troubladore/data-eng-template
cd your-second-project
./scripts/setup-development.sh  # Should be very fast (cache hit!)
```

## 📞 **Getting Help**

### Automated Help
```bash
# Comprehensive validation
dcm-setup validate

# Automated issue resolution
dcm-setup troubleshoot

# Check cache and registry status
dcm-cache status
```

### Manual Troubleshooting
1. Check the troubleshooting section in the [main README](../README.md)
2. Review the [service manager documentation](https://github.com/Troubladore/devcontainer-service-manager)
3. Ensure you're following WSL2 best practices (file location, Docker integration)

---

## 🚀 **Next Steps**

Once your environment is working:

1. **Explore the generated project structure** - Start with `docs/index.md`
2. **Review Airflow DAGs** - Check `dags/` directory for examples
3. **Customize configuration** - Edit `conf/config.yaml` for your needs
4. **Add your data sources** - Update connection configurations
5. **Start building pipelines** - Use the provided templates and patterns

**You're ready to build awesome data engineering projects!** 🎉