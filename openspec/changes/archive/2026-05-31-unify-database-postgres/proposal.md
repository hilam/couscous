## Why

The current codebase supports both SQLite and PostgreSQL via a runtime branch on `COUSCOUS_DATABASE_TYPE`, but every feature (async services, SQLModel, Flet) already assumes async patterns that PostgreSQL provides natively. SQLite support adds complexity (sync/async engine branching, `isinstance` checks, dual session management) without benefit — users deploy to Postgres in production and should develop against the same database. Removing SQLite eliminates the branching logic, simplifies config, and ensures dev/prod parity.

## What Changes

- **BREAKING**: Remove SQLite support entirely — `COUSCOUS_DATABASE_TYPE` env var is removed; PostgreSQL is always used
- **BREAKING**: All database env vars (`HOST`, `PORT`, `USER`, `PASS`) become required (no more fallback to SQLite)
- Add `docker-compose.yml` with `postgres:16-alpine` for local development
- Simplify `config.py` — remove the `if/else` branching; always build a Postgres async URL
- Simplify `database.py` — remove sync engine creation and `init_db()`; keep only async engine and `init_async_db()`
- Simplify `app/db.py` — remove the `isinstance` branching; always use async session
- Update `.env.sample` to reflect required Postgres-only vars
- Update test fixtures to use PostgreSQL via a test Docker container (or keep in-memory but always async)
- Update `AGENTS.md` quick-start and docs

## Capabilities

### New Capabilities
- `docker-database`: Docker Compose configuration providing PostgreSQL 16 Alpine for local development

### Modified Capabilities
- `env-config`: `COUSCOUS_DATABASE_TYPE` removed; all PostgreSQL connection vars become mandatory without SQLite fallback

## Impact

- `database/service/config.py` — remove branching, always build async Postgres URL
- `database/service/database.py` — remove sync engine, `init_db()`, and `isinstance` checks; keep only async engine + `init_async_db()`
- `app/db.py` — remove `isinstance(engine, AsyncEngine)` branches; always use `async_sessionmaker`
- `.env.sample` — reflect required Postgres vars only
- `docker-compose.yml` — new file at project root
- `AGENTS.md` — update quick-start, DB init, env var table
- `tests/conftest.py` — switch from in-memory SQLite to async test DB
- `pyproject.toml` — may drop sqlite-related deps if any, add `asyncpg` as required dependency (currently only in Postgres path)
