#!/usr/bin/env bash
podman compose -f .devcontainer/compose.yaml exec postgres psql -U airflow -d airflow
