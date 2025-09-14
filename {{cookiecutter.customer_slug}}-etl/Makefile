SHELL := /bin/bash

.PHONY: init start stop parse export urls test

init: export
	@echo "Ensure astro-local-config/traefik-bundle is running (docker compose up -d)"
	astro dev start
	./tools/where.sh

start:
	astro dev start

stop:
	astro dev stop || true

parse:
	astro dev parse

export:
	bash tools/uv/export.sh

urls:
	./tools/where.sh

test:
	pytest -q || true
