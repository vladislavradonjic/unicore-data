SHELL := /bin/bash
VENV := .venv/bin
DBT  := DBT_PROFILES_DIR=. $(VENV)/dbt

.PHONY: help up down reset seed dbt-run dbt-test psql

help:
	@echo "unicore-data targets:"
	@echo "  up         start mock source Postgres"
	@echo "  down       stop and remove containers"
	@echo "  seed       run Python seeder (transactional mock data)"
	@echo "  dbt-run    run dbt seeds + dbt models"
	@echo "  dbt-test   run dbt tests"
	@echo "  reset      full teardown + up + seed + dbt-run"
	@echo "  psql       connect to mock source"

up:
	docker compose up -d
	@echo "Waiting for Postgres to be ready…"
	@until docker exec unicore-mock-source pg_isready -U unicore -d unicore -q; do sleep 1; done
	@echo "Postgres ready."

down:
	docker compose down -v

seed:
	$(VENV)/python scripts/seed_source.py

dbt-run:
	$(DBT) seed
	$(DBT) run

dbt-test:
	$(DBT) test

reset: down up seed dbt-run

psql:
	psql postgresql://unicore:unicore@localhost:5433/unicore
