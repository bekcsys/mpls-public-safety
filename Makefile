export DOCKER_BUILDKIT := 0
COMPOSE := docker compose
SERVICE := dagster
ASSETS := raw_incidents,processed_incidents

.DEFAULT_GOAL := help

.PHONY: help setup build up down logs restart materialize shell

help:
	@echo "make setup        create .env, build, and start Dagster"
	@echo "make up           start Dagster UI at http://127.0.0.1:3000"
	@echo "make down         stop containers"
	@echo "make logs         follow container logs"
	@echo "make materialize  run raw_incidents -> processed_incidents"
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

shell: up
	$(COMPOSE) exec $(SERVICE) bash
