## 1. Docker Compose

- [x] 1.1 Create `docker-compose.yml` at project root with `db` service using `postgres:16-alpine`, port 5432, default creds `couscous`/`couscous`/`couscous`, and a named volume for persistence

## 2. Database Config

- [x] 2.1 Simplify `database/service/config.py` — remove `db_type` branching; always build `postgresql+asyncpg://` URL from `HOST`, `PORT`, `USER`, `PASS`, `NAME`; remove `COUSCOUS_DATABASE_TYPE` env var read

## 3. Database Engine

- [x] 3.1 Simplify `database/service/database.py` — remove sync `create_engine` call, remove `init_db()` function and `isinstance` checks; keep only `create_async_engine`, `init_async_db()`, and `get_session()` (async-only)

## 4. Session Management

- [x] 4.1 Simplify `app/db.py` — remove `isinstance(engine, AsyncEngine)` branching and sync `sessionmaker` path; always use `async_sessionmaker`

## 5. Environment Sample

- [x] 5.1 Update `.env.sample` — remove `COUSCOUS_DATABASE_TYPE` and its comment; make all PostgreSQL vars required; add Docker prerequisite note

## 6. Test Fixtures

- [x] 6.1 Update `tests/conftest.py` — switch from `create_engine("sqlite://")` to `create_async_engine` connecting to PostgreSQL `couscous_test` database; use `async_sessionmaker`; create/drop tables per fixture

## 7. Dependencies

- [x] 7.1 Add `"asyncpg>=0.30.0"` to `[project.dependencies]` in `pyproject.toml`

## 8. Documentation

- [x] 8.1 Update `AGENTS.md` — revise quick-start to include `docker compose up -d` step; update DB init command to use `init_async_db`; update env var table to remove `COUSCOUS_DATABASE_TYPE` and mark all vars required

## 9. Verification

- [x] 9.1 Run `ruff check .` and `ruff format .` — ensure no linting errors
- [x] 9.2 Run `uv run mypy .` — ensure no type errors
- [x] 9.3 Run `docker compose up -d` then `uv run pytest` — ensure all tests pass against PostgreSQL
