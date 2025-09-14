#!/usr/bin/env bash
podman compose -f .devcontainer/compose.yaml exec airflow-webserver airflow "$@"
