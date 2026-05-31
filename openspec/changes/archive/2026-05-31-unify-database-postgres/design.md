## Context

The current database layer supports two backends (SQLite sync, PostgreSQL async) selected at runtime via `COUSCOUS_DATABASE_TYPE`. This dual-path design infects every layer: `config.py` branches URL construction, `database.py` branches engine creation, `app/db.py` branches session creation, and tests use in-memory SQLite (sync) while production uses Postgres (async). The branching adds `isinstance` checks, type confusion (casting `Session` to `AsyncSession`), and two code paths to maintain. All application code already uses async patterns — the SQLite path is a legacy convenience that no longer pulls its weight.

## Goals / Non-Goals

**Goals:**
- PostgreSQL becomes the only supported database backend
- Remove all sync/SQLite branching in config, engine, and session code
- Add `docker-compose.yml` with `postgres:16-alpine` for local development
- Add `asyncpg` as a required dependency
- Update `.env.sample` to reflect mandatory Postgres vars
- Update test fixtures to use PostgreSQL (async) instead of in-memory SQLite
- Update `AGENTS.md` and quick-start instructions

**Non-Goals:**
- Changing the SQLModel models or schema
- Changing the service interfaces or application logic
- Adding connection pooling configuration beyond default SQLAlchemy settings
- Adding migration tooling (Alembic) — schema is still created via `init_async_db()`
- Containerizing the Python application itself — only the database is containerized

## Decisions

### Decision 1: Always asyncpg, always async

- **Choice**: Remove `COUSCOUS_DATABASE_TYPE` env var. `config.py` always builds a `postgresql+asyncpg://` URL using all five connection vars (`HOST`, `PORT`, `USER`, `PASS`, `NAME`).
- **Rationale**: Simpler config, single engine path, no runtime branches. Every piece of code currently assumes async anyway — the sync SQLite path was unused in practice for any async operation.
- **Alternatives**: Keep the env var but make Postgres the only valid value; default to Postgres. Rejected because the var becomes meaningless.

### Decision 2: Sync `init_db()` removed, only `init_async_db()` remains

- **Choice**: Delete `init_db()`. Keep `init_async_db()` as the sole schema creation path.
- **Rationale**: With no sync engine, the sync init function has no purpose. `init_async_db()` is already used in practice.
- **Alternatives**: Rename `init_async_db()` to `init_db()`. Rejected to avoid unnecessary churn — callers can be updated to call `init_async_db()`.

### Decision 3: Docker Compose for local Postgres

- **Choice**: A single `docker-compose.yml` at the project root with a `db` service using `postgres:16-alpine`, mapped to port 5432, with configurable env vars defaulting to `couscous`/`couscous` credentials.
- **Rationale**: Zero-install Postgres for developers who have Docker. Matches production target. Single command (`docker compose up -d`) replaces manual Postgres setup.
- **Alternatives**: Use a system-installed Postgres. Rejected because it adds setup friction and version inconsistency across dev machines.

### Decision 4: Tests use a dedicated test database in the same Postgres instance

- **Choice**: The `db_session` fixture in `tests/conftest.py` connects to the same Docker Postgres but uses a separate database name (`couscous_test`). The fixture creates all tables before the test and drops them after.
- **Rationale**: Dev/test parity (same Postgres backend). No test containers library needed. Requires `docker compose up -d` before running tests.
- **Alternatives**: 
  - In-memory SQLite (status quo). Rejected: defeats dev/test parity, keeps branching complexity.
  - Testcontainers library to spin up a disposable Postgres. Rejected: adds a new dependency and startup latency to every test run.
  - Separate `docker-compose.test.yml`. Rejected: unnecessary duplication — one Postgres instance can serve both databases.

### Decision 5: `asyncpg` promoted from optional to required dependency

- **Choice**: Add `"asyncpg>=0.30.0"` to `[project.dependencies]` in `pyproject.toml`.
- **Rationale**: It's no longer an optional driver for an alternative backend — it's the only driver.
- **Alternatives**: Keep it out and rely on users installing it manually. Rejected: it's mandatory now.

## Risks / Trade-offs

- **Risk**: Developers without Docker cannot run the app locally.
  - **Mitigation**: Document Docker as a prerequisite in AGENTS.md quick-start. Most modern dev machines have Docker available.
- **Risk**: Tests now depend on a running Postgres container — they will fail if `docker compose` is not up.
  - **Mitigation**: Document the prerequisite prominently. Consider adding a pytest `skipif` that checks for Postgres connectivity and skips tests with a clear message.
- **Trade-off**: Slightly heavier dev environment (Docker + Postgres container) vs. the zero-dependency SQLite approach.
  - This is intentional — dev/prod parity is more valuable than minimal dev setup.
- **Risk**: Breaking change for existing contributors who used SQLite.
  - **Mitigation**: Clear CHANGELOG/commit message and updated quick-start guide.
- **Trade-off**: Test setup/teardown overhead (CREATE/DROP TABLE per fixture) is higher than in-memory SQLite.
  - Acceptable — fixtures do schema creation once per session, not per test.
