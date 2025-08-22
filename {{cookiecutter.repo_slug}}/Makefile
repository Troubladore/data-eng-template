COMPOSE = podman compose -f .devcontainer/compose.yaml

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f --tail=200

airflow:
	$(COMPOSE) exec airflow-webserver airflow $(ARGS)

psql:
	$(COMPOSE) exec postgres psql -U airflow -d airflow

# Configuration management targets
config-validate:
	python scripts/run_pipeline.py --help

config-test:
	python scripts/run_pipeline.py runtime.dry_run=true

config-prod-test:
	python scripts/run_pipeline.py environment=prod runtime.dry_run=true

config-migrate:
	python scripts/migrate_config.py --env-file .env --output-dir conf/local

# Pipeline execution targets  
pipeline:
	python scripts/run_pipeline.py

pipeline-prod:
	python scripts/run_pipeline.py environment=prod

# Development shortcuts
test-config:
	python -m pytest tests/test_config.py -v

# =============================================================================
# Deployment Targets - Astronomer-inspired deployment workflows
# =============================================================================

# DAG-only deployment (fastest - for DAG changes only)
deploy-dags:
	@echo "🚀 Deploying DAGs only (fastest deployment)"
	python scripts/deploy.py --dags-only

# Full deployment (dependencies + code - slowest but complete)
deploy-full:
	@echo "🚀 Full deployment (rebuilding everything)"  
	python scripts/deploy.py --full

# Automatic deployment (detects changes and chooses strategy)
deploy-auto:
	@echo "🚀 Automatic deployment (detecting changes)"
	python scripts/deploy.py --detect-changes

# Default deployment target (auto-detect)
deploy: deploy-auto

# Dry run deployments (preview without executing)
deploy-dags-dry:
	@echo "🔍 DRY RUN: DAG-only deployment"
	python scripts/deploy.py --dags-only --dry-run

deploy-full-dry:
	@echo "🔍 DRY RUN: Full deployment"
	python scripts/deploy.py --full --dry-run

deploy-auto-dry:
	@echo "🔍 DRY RUN: Automatic deployment"
	python scripts/deploy.py --detect-changes --dry-run

# Build Docker image with caching optimization
build-image:
	@echo "🐳 Building Airflow Docker image with caching"
	docker build -f Dockerfile.airflow \
		--target runtime \
		--cache-from airflow-{{cookiecutter.repo_slug}}:latest \
		-t airflow-{{cookiecutter.repo_slug}}:latest \
		-t airflow-{{cookiecutter.repo_slug}}:dev \
		.

# Build development image  
build-image-dev:
	@echo "🐳 Building Airflow development image"
	docker build -f Dockerfile.airflow \
		--target development \
		--cache-from airflow-{{cookiecutter.repo_slug}}:dev \
		-t airflow-{{cookiecutter.repo_slug}}:dev \
		.

# Clean deployment cache
deploy-clean:
	@echo "🧹 Cleaning deployment cache"
	rm -f .deploy_cache.json
	docker system prune -f

# Show deployment status and timing
deploy-status:
	@echo "📊 Deployment Status"
	@if [ -f .deploy_cache.json ]; then \
		echo "📄 Cache file exists"; \
		echo "🕐 Last deployment:"; \
		stat -c "%y" .deploy_cache.json; \
	else \
		echo "📄 No deployment cache found"; \
	fi
	@echo "🐳 Docker images:"; \
	docker images | grep airflow-{{cookiecutter.repo_slug}} || echo "No images found"

# Performance testing for deployments
deploy-perf-test:
	@echo "⚡ Running deployment performance test"
	@echo "Testing DAG-only deployment..."
	time make deploy-dags-dry
	@echo "Testing full deployment..."
	time make deploy-full-dry
	@echo "Testing auto-detect deployment..."
	time make deploy-auto-dry
