# Quick Test Reference - Issue #1

## Updated Generation Command (with test tagging)

**OLD (creates hard-to-clean artifacts):**
```bash
cookiecutter . --no-input --output-dir /tmp
```

**NEW (creates tagged test artifacts):**
```bash
cookiecutter . --no-input \
  deployment_mode=testing \
  project_name="DCSM Test" \
  customer_slug="dcsm-integration" \
  --output-dir /tmp
```

## What the NEW command creates:

### Docker Artifacts (all tagged with `-test`)
- **Compose projects**: `dcsm-integration-etl-modern-test`, `dcsm-integration-etl-test-fast-test`
- **Images**: `dcsm-integration-etl-airflow-dev-test`, `dcsm-integration-etl-airflow-fast-test-test`
- **Containers**: `dcsm-integration-etl-postgres-test`, `dcsm-integration-etl-airflow-webserver-test`, etc.

### Labels (for easy identification)
- `de-template.project=dcsm-integration-etl`
- `de-template.deployment=testing`
- `de-template.service=postgres|airflow-webserver|etc`

## Cleanup (much simpler now!)

**OLD cleanup (manual, error-prone):**
```bash
docker compose down -v
docker rmi $(docker images | grep devcontainer-airflow | awk '{print $3}') test-build-args
cd ../.. && rm -rf dcsm-integration-test
```

**NEW cleanup (automated):**
```bash
# Option 1: Automatic (finds /tmp projects too)
./cleanup-shallow.sh

# Option 2: Manual but reliable
rm -rf /tmp/dcsm-integration-etl
docker ps -a --filter "label=de-template.project=dcsm-integration-etl" -q | xargs docker rm -f 2>/dev/null || true
docker images --filter "reference=dcsm-integration-etl*" -q | xargs docker rmi -f 2>/dev/null || true
```

## Verification Commands

```bash
# Before testing - check clean state
docker ps -a --filter "label=de-template.deployment=testing"

# After testing - verify artifacts exist
docker ps -a --filter "label=de-template.project=dcsm-integration-etl"

# After cleanup - verify clean state
docker ps -a --filter "label=de-template.deployment=testing"
```

## Complete Test Cycle

```bash
# 1. Generate with test tagging
cookiecutter . --no-input deployment_mode=testing customer_slug=dcsm-integration --output-dir /tmp

# 2. Test
cd /tmp/dcsm-integration-etl
# ... run your tests ...

# 3. Return to template repo and cleanup
cd /path/to/data-eng-template
./cleanup-shallow.sh

# 4. Verify clean state
docker ps -a --filter "label=de-template.deployment=testing"  # Should be empty
```

**Key Benefits:**
✅ No more `<none>` images
✅ Clear test vs production separation
✅ Automated cleanup scripts
✅ Works with `/tmp` output directory
✅ Easy verification commands