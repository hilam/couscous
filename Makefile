.PHONY: install run run-web test lint format format-check typecheck check-all security db-up db-down db-shell db-clean db-migrate-create db-migrate-up db-migrate-down db-migrate-status clean

install:
	uv sync

run:
	uv run python main.py

run-web: db-up db-migrate-up
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

check-all: db-up lint typecheck test security

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

db-migrate-create:
	@if [ -z "$(name)" ]; then \
		echo "ERRO: Forneça um nome para a migration. Exemplo: make db-migrate-create name=\"adiciona campo avatar\""; \
		exit 1; \
	fi
	uv run alembic revision --autogenerate -m "$(name)"

db-migrate-up:
	uv run alembic upgrade head

db-migrate-down:
	uv run alembic downgrade -1

db-migrate-status:
	uv run alembic current

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache/ reports/
