# AGENTS.md – CousCous RSS Feed Reader (Flet)

## Quick start

```bash
uv sync                          # install deps (uv is the package manager)
uv run python main.py                   # run the Flet app (desktop or web via -d)
uv run python -c "from database.service.database import init_db; init_db()"  # one-time schema init
uv run pytest                           # run all tests
ruff check .                     # lint
uv run mypy .                        # type-check
```

Run Flet in web mode: `uv run flet run -d`.

## Project architecture

| Directory | Purpose |
|-----------|---------|
| `main.py` | Entrypoint: `ft.app(target=app_run)` |
| `app/` | Flet app: views, services, controls, DB session, state |
| `app/services/` | Async service functions (`feed_service`, `entry_service`, `user_service`, `refresh_service`) |
| `app/views/` | One file per route: `login_view`, `feed_list_view`, `entry_list_view`, `entry_view`, `home_view`, `about_view` |
| `app/controls/` | Reusable UI components (`feed_card`, `article_card`, `add_feed_dialog`, `confirm_dialog`) |
| `app/db.py` | `get_db_session()` — async context manager wrapping sync/async engine |
| `app/state.py` | `State` class: `user`, `active_feed_url`, `loading` |
| `database/models/couscous.py` | SQLModel models: `User`, `Feed`, `Entry`, `FeedMetadata`, `FeedTag` |
| `database/service/` | DB engine, config, `init_db()` / `init_async_db()` |
| `database/service/config.py` | Reads `COUSCOUS_DATABASE_TYPE`, path env vars |

## Environment variables

| Var | Default | Purpose |
|-----|---------|---------|
| `COUSCOUS_DATABASE_TYPE` | unset (sqlite) | `asyncpg` for async engine |
| `COUSCOUS_DATABASE_NAME` | — | DB name (used for both sqlite and postgres) |
| `COUSCOUS_DATABASE_HOST` | — | Postgres host |
| `COUSCOUS_DATABASE_PORT` | 5432 | Postgres port |
| `COUSCOUS_DATABASE_USER` | — | Postgres user |
| `COUSCOUS_DATABASE_PASS` | — | Postgres password |

## Testing

- All tests use `db_session` fixture (in-memory SQLite via SQLModel).
- Every service test is `@pytest.mark.asyncio` and calls async service functions.
- Run a single test: `pytest tests/test_feed_service.py::test_add_feed`.

## Gotchas

- Run `init_db()` **once** before first app launch (tables created lazily).
- All service functions in `app/services/` are **async** and take a `session` first arg.
- The DB session (`app/db.get_db_session()`) is a sync OR async session depending on env — works with both engines.
- Password is stored in plaintext (no hashing yet).
- `flet run -d` serves via web browser on `localhost:8550` by default.

## OpenSpec

Structured changes live in `openspec/`. Skills in `.opencode/skills/openspec-*` handle the workflow. Use `/opsx-propose` for new change proposals, `/opsx-apply` to implement tasks.

## graphify

Knowledge graph at `graphify-out/`. Run `graphify update .` after modifying code. Query it with `graphify query "..."`, use `graphify path "A" "B"` for relationships, read `graphify-out/GRAPH_REPORT.md` for architecture overview.
