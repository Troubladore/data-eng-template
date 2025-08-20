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
