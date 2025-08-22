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
