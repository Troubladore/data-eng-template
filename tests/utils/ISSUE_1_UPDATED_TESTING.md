# Updated Testing Instructions for Issue #1

## Quick Testing with New Cleanup System

### 1. Validation (Pre-test)
```bash
# Run validation script to check current state
python scripts/validate-dcsm-integration.py
```

### 2. Generate Fresh Test Project (NEW - uses test tagging)
```bash
# Generate with test tagging to ensure easy cleanup
cookiecutter . --no-input \
  deployment_mode=testing \
  project_name="DCSM Test" \
  customer_slug="dcsm-integration" \
  --output-dir /tmp

cd /tmp/dcsm-integration-etl
```

**What this creates:**
- Project: `/tmp/dcsm-integration-etl/`
- Docker artifacts tagged with `-test` suffix:
  - Compose projects: `dcsm-integration-etl-modern-test`, `dcsm-integration-etl-test-fast-test`
  - Images: `dcsm-integration-etl-airflow-dev-test`, `dcsm-integration-etl-airflow-fast-test-test`
  - Containers: `dcsm-integration-etl-postgres-test`, etc.
- All containers labeled with `de-template.deployment=testing`

### 3. Build and Test
```bash
# Build the custom Airflow image with DCSM integration
timeout 60 docker build -f Dockerfile.airflow --target development -t dcsm-integration-etl-airflow-dev-test .

# Start services
cd .devcontainer
docker compose up -d

# Verify services are running
docker compose ps

# Check Airflow UI (if needed)
echo "Airflow UI: http://localhost:8081"
```

### 4. Run Integration Tests
```bash
# Run DCSM integration tests
cd ..
.venv/bin/pytest tests/integration/test_dcsm_custom_build_integration.py -v -s

# Run specific test if needed
.venv/bin/pytest tests/integration/test_dcsm_custom_build_integration.py::TestDCSMCustomBuildIntegration::test_dcsm_custom_build_with_existing_dockerfile -v -s
```

### 5. Validation (Post-test)
```bash
# Run validation script to verify integration
python scripts/validate-dcsm-integration.py
```

### 6. Cleanup (NEW - much simpler!)
```bash
# Return to template repository
cd /path/to/data-eng-template

# Option A: Clean up this specific test
# Remove the generated project directory
rm -rf /tmp/dcsm-integration-etl

# Clean up Docker artifacts by label (test artifacts only)
docker ps -a --filter "label=de-template.project=dcsm-integration-etl" -q | xargs docker rm -f 2>/dev/null || true
docker images --filter "reference=dcsm-integration-etl*" -q | xargs docker rmi -f 2>/dev/null || true

# Option B: Use automated cleanup script (recommended)
./cleanup-shallow.sh  # This will find and clean /tmp/dcsm-integration-etl automatically

# Option C: Nuclear cleanup (if you want to start completely fresh)
./cleanup-deep.sh  # Removes ALL data-eng-template test artifacts
```

## Verification Commands

### Check Test Artifact Tagging
```bash
# View all test containers
docker ps -a --filter "label=de-template.deployment=testing"

# View specific project containers
docker ps -a --filter "label=de-template.project=dcsm-integration-etl"

# View test images
docker images | grep "test"
```

### Before/After Comparison
```bash
# Before testing - check what exists
docker ps -a --filter "label=de-template.project" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
docker images | grep -E "(etl|airflow|test)" | wc -l

# After cleanup - verify clean state
docker ps -a --filter "label=de-template.project" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
docker images | grep -E "(etl|airflow|test)" | wc -l
```

## Key Improvements

1. **Test Tagging**: Using `deployment_mode=testing` ensures all Docker artifacts are clearly marked as test resources
2. **Automated Cleanup**: The `cleanup-shallow.sh` script automatically finds and removes test projects and their Docker artifacts
3. **Label-based Identification**: Easy to distinguish test vs production artifacts using Docker labels
4. **Output Directory**: Using `/tmp` keeps test projects separate from your working directory
5. **Verification**: Commands to verify the tagging system is working and cleanup was successful

## Troubleshooting

### If cleanup-shallow.sh doesn't find the project:
```bash
# Manual cleanup for /tmp projects
rm -rf /tmp/dcsm-integration-etl

# Clean Docker artifacts by project label
docker ps -a --filter "label=de-template.project=dcsm-integration-etl" -q | xargs docker rm -f 2>/dev/null || true
docker images --filter "reference=dcsm-integration-etl*" -q | xargs docker rmi -f 2>/dev/null || true
docker volume ls --filter "label=de-template.project=dcsm-integration-etl" -q | xargs docker volume rm 2>/dev/null || true
```

### If you need to run multiple test iterations:
```bash
# Test iteration 1
cookiecutter . --no-input deployment_mode=testing customer_slug=dcsm-test-1 --output-dir /tmp
# ... test ...
rm -rf /tmp/dcsm-test-1-etl && docker ps -a --filter "label=de-template.project=dcsm-test-1-etl" -q | xargs docker rm -f 2>/dev/null || true

# Test iteration 2
cookiecutter . --no-input deployment_mode=testing customer_slug=dcsm-test-2 --output-dir /tmp
# ... test ...
rm -rf /tmp/dcsm-test-2-etl && docker ps -a --filter "label=de-template.project=dcsm-test-2-etl" -q | xargs docker rm -f 2>/dev/null || true

# Final cleanup
./cleanup-deep.sh
```