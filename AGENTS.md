# AGENTS.md – CousCous RSS Feed Reader (Flet)

## Quick start

```bash
docker compose up -d             # start PostgreSQL 16 (required)
uv sync                          # install all dependencies (uv is the package manager)
uv run python -c "from database.service.database import init_async_db; import asyncio; asyncio.run(init_async_db())"  # create tables
uv run python main.py            # run the Flet app (desktop)
uv run flet run -w               # run in web browser on localhost:8550
uv run pytest                    # run all tests
ruff format .                    # format code
ruff check .                     # lint (config excludes tests/)
uv run mypy .                    # type-check (only app/ and database/ per config)
make lint-security             # security scan with bandit (or `make lint-security`)
```

## Project architecture

| Directory | Purpose |
|-----------|---------|
| `main.py` | Entrypoint: `ft.run(app_run)` |
| `app/app.py` | Flet app lifecycle, route table, page setup |
| `app/views/` | One file per route: `login_view`, `feed_list_view`, `entry_list_view`, `entry_view`, `home_view`, `about_view` |
| `app/controls/` | Reusable UI: `feed_card`, `article_card`, `add_feed_dialog`, `confirm_dialog` |
| `app/services/` | Async service layer: `feed_service`, `entry_service`, `user_service`, `refresh_service` |
| `app/db.py` | `get_db_session()` — async context manager wrapping async engine |
| `app/state.py` | `State` class: `user`, `active_feed_url`, `loading` |
| `database/models/couscous.py` | SQLModel models: `User`, `Feed`, `Entry`, `FeedMetadata`, `FeedTag` |
| `database/service/` | Engine, config, `init_async_db()` |
| `tests/` | `pytest` + `pytest-asyncio`, each file tests one service |

## Environment variables

`.env` is auto-loaded by services (`database/service/config.py`) and tests (`tests/conftest.py`).

| Var | Default | Purpose |
|-----|---------|---------|
| `COUSCOUS_DATABASE_NAME` | couscous | Database name |
| `COUSCOUS_DATABASE_HOST` | localhost | Postgres host |
| `COUSCOUS_DATABASE_PORT` | 5432 | Postgres port |
| `COUSCOUS_DATABASE_USER` | couscous | Postgres user |
| `COUSCOUS_DATABASE_PASS` | couscous | Postgres password |

## Test conventions

- All service tests use the `db_session` fixture (PostgreSQL via SQLModel async) from `tests/conftest.py`.
- Every service test is `@pytest.mark.asyncio` and takes `db_session` as first arg.
- Ensure `docker compose up -d` is running before executing tests.
- Run a single test: `uv run pytest tests/test_feed_service.py::test_add_feed`.

## Gotchas

- Password is stored in plaintext (no hashing yet).
- All service functions in `app/services/` are **async** and take `session` as first arg.
- `get_db_session()` returns an async session via `async_sessionmaker`.
- `ruff check .` skips `tests/` (configured in `pyproject.toml`).
- `mypy` only checks `app/` and `database/` dirs.

## OpenSpec

Structured changes live in `openspec/`. Skills in `.opencode/skills/openspec-*` handle the workflow. Use `/opsx-propose` for new change proposals, `/opsx-apply` to implement tasks.

## graphify

Knowledge graph at `graphify-out/`. Run `graphify update .` after modifying code. Query it with `graphify query "..."`, use `graphify path "A" "B"` for relationships, read `graphify-out/GRAPH_REPORT.md` for architecture overview.
