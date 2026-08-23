export DOCKER_BUILDKIT := 0
COMPOSE := docker compose
SERVICE := dagster
ASSETS := raw_incidents,processed_incidents,raw_communities,raw_metro_places,enriched_incidents,neighborhood_case_counts,neighborhood_case_bubbles

.DEFAULT_GOAL := help

.PHONY: help setup build up down logs restart materialize preview viz shell

help:
	@echo "make setup        create .env, build, and start Dagster"
	@echo "make up           start Dagster UI at http://127.0.0.1:3000"
	@echo "make down         stop containers"
	@echo "make logs         follow container logs"
	@echo "make materialize  ingest, clean, and enrich incidents"
	@echo "make preview      show sample rows before, after, and enriched"
	@echo "make viz          write the Minneapolis neighborhood bubble map"
	@echo "make shell        open a shell in the container"
	@echo "make build        rebuild the image"

setup: .env build up

.env:
	cp .env.example .env

build:
	$(COMPOSE) build

up: .env
	$(COMPOSE) up -d --wait

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f $(SERVICE)

restart:
	$(COMPOSE) restart $(SERVICE)

materialize: up
	$(COMPOSE) exec -T $(SERVICE) dagster asset materialize -m mpls_public_safety.definitions --select $(ASSETS)

preview: up
	$(COMPOSE) exec -T $(SERVICE) python -m mpls_public_safety.preview

viz: up
	$(COMPOSE) exec -T $(SERVICE) dagster asset materialize -m mpls_public_safety.definitions --select neighborhood_case_counts,neighborhood_case_bubbles

shell: up
	$(COMPOSE) exec $(SERVICE) bash
