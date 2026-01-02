SHELL := /bin/bash

UV ?= uv
VENV ?= .venv
BIN := $(VENV)/bin

.PHONY: help venv install install-dev dev prod run test lint format clean docker-build docker-run docker-dev docker-down

help:
	@echo "Setup:"
	@echo "  venv         Create virtualenv with uv in $(VENV)"
	@echo "  install      Install package (production) into venv"
	@echo "  install-dev  Install package + dev dependencies into venv"
	@echo ""
	@echo "Development:"
	@echo "  dev          Run API server with reload"
	@echo "  prod         Run API server (no reload)"
	@echo "  run          Alias for 'prod'"
	@echo "  test         Run test suite with coverage"
	@echo "  lint         Lint code with ruff"
	@echo "  format       Format code with ruff"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build Build Docker image"
	@echo "  docker-run   Run Docker container (production)"
	@echo "  docker-dev   Run Docker container (development with reload)"
	@echo "  docker-down  Stop and remove containers"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean        Remove build artifacts and venv"

venv:
	$(UV) venv $(VENV)

install: venv
	$(UV) pip install -e .

install-dev: venv
	$(UV) pip install -e ".[dev]"

dev:
	@set -a; [ -f .env ] && source .env; set +a; \
	$(UV) run uvicorn python_template.api.asgi:app --reload --reload-dir src \
		--host $${PYTHON_TEMPLATE_HOST:-127.0.0.1} \
		--port $${PYTHON_TEMPLATE_PORT:-8000}

prod:
	@set -a; [ -f .env ] && source .env; set +a; \
	$(UV) run uvicorn python_template.api.asgi:app \
		--host $${PYTHON_TEMPLATE_HOST:-127.0.0.1} \
		--port $${PYTHON_TEMPLATE_PORT:-8000}

run: prod

test:
	$(UV) run --extra dev pytest --cov=python_template

lint:
	$(UV) run --extra dev ruff check src/ tests/

format:
	$(UV) run --extra dev ruff format src/ tests/

docker-build:
	docker build -t python-template:latest --target runtime .

docker-run: docker-build
	docker compose up -d api

docker-dev:
	docker build -t python-template:dev --target runtime-dev .
	docker compose --profile dev up -d api-dev

docker-down:
	docker compose down

clean:
	rm -rf $(VENV) build dist *.egg-info .pytest_cache .coverage coverage.xml htmlcov .ruff_cache
