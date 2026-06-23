.PHONY: install run run-web test lint format format-check typecheck check-all security db-up db-down db-shell clean

install:
	uv sync

run:
	uv run python main.py

run-web:
	uv run flet run -w -p 8550

test:
	uv run pytest

lint:
	uv run ruff check

format:
	uv run ruff format

lint-fix:
	uv run ruff check --fix

typecheck:
	uv run mypy

check-all: lint typecheck test lint-security

security:
	uv run bandit -r app/ database/

db-up:
	docker compose up -d

db-down:
	docker compose down --remove-orphans

db-clean:
	docker compose down --volumes --remove-orphans

db-shell:
	PGPASSWORD=couscous psql -h localhost -U couscous -d couscous -p 5432

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache/ reports/
