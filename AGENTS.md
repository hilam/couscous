# AGENTS.md – CousCous RSS Feed Reader (Flet)

## Quick start

```bash
cp .env.sample .env            # required — .env is gitignored
docker compose up -d            # start PostgreSQL 16 (required)
uv sync                         # install all dependencies (uv is the package manager)
uv run python main.py           # run the Flet app (desktop) — creates DB tables on startup
uv run flet run -w              # run in web browser on localhost:8550
uv run pytest                   # run all tests
ruff format .                   # format code
ruff check .                    # lint (config excludes tests/)
uv run mypy .                   # type-check (only app/ and database/ per config)
make lint-security              # security scan with bandit
```

## Project architecture

| Directory | Purpose |
|-----------|---------|
| `main.py` | Entrypoint: `ft.run(app_run)` |
| `app/app.py` | Flet app lifecycle, route table, page setup |
| `app/views/` | One file per route: `login_view`, `feed_list_view`, `entry_list_view`, `entry_view`, `home_view`, `about_view` |
| `app/controls/` | Reusable UI: `feed_card`, `article_card`, `add_feed_dialog`, `confirm_dialog` |
| `app/services/` | Async service layer: `feed_service`, `entry_service`, `user_service`, `refresh_service` |
| `database/service/database.py` | `get_db_session()` — async context manager wrapping async engine |
| `app/state.py` | `State` class holding `user`, `active_feed_url`, `loading` |
| `database/models/couscous.py` | SQLModel models: `User`, `Feed`, `Entry`, `FeedMetadata`, `FeedTag` |
| `database/service/` | Engine, config, `init_async_db()` |
| `tests/` | `pytest` + `pytest-asyncio`, each file tests one service |
| `openspec/` | Structured change artifacts (specs, proposals, designs, tasks) |

## Environment variables

`.env` is auto-loaded by `database/service/config.py` and tests via `tests/conftest.py`.

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
- Tests connect to `couscous_test` database (hardcoded in conftest), not `couscous`.

## Gotchas

- Password is stored in plaintext (no hashing yet).
- All service functions in `app/services/` are **async** and take `session` as first arg.
- `get_db_session()` in `database/service/database.py` is the single source for async sessions.
- `ruff check .` skips `tests/` (configured in `pyproject.toml`).
- `mypy` only checks `app/` and `database/` dirs.
- `.env` is gitignored; `.env.sample` is the template.

## OpenSpec

Structured changes live in `openspec/`. Skills in `.opencode/skills/openspec-*` handle the workflow. Use `/opsx-propose` for new change proposals, `/opsx-apply` to implement tasks.
