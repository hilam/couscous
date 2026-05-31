lint-security:
	uv run bandit -r app/ database/

db-up:
	docker compose up -d

db-down:
	docker compose down --remove-orphans
