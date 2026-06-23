# AGENTS.md – CousCous RSS Feed Reader (Flet)

## Quick start

```bash
cp .env.sample .env            # required — .env is gitignored
make db-up                     # start PostgreSQL 16 (required)
make install                   # uv sync — install dependencies
make run-web                   # run in web browser on localhost:8550
make test                      # run all tests (pytest)
make format                    # format code (ruff)
make lint                      # lint code (ruff)
make typecheck                 # type-check (mypy, scoped to app/ and database/)
make security                  # security scan (bandit)
make check-all                 # lint + typecheck + test + security (CI gate)
```

**Always use `make` targets** instead of raw commands. `make <target>` is the single source of truth for how to run each tool. Do not guess executable names or paths.

## Makefile reference

| Target | Command |
|--------|---------|
| `make install` | `uv sync` |
| `make run` | `uv run python main.py` |
| `make run-web` | `uv run flet run -w -p 8550` |
| `make test` | `uv run pytest` |
| `make lint` | `uv run ruff check` |
| `make lint-fix` | `uv run ruff check --fix` |
| `make format` | `uv run ruff format` |
| `make typecheck` | `uv run mypy` |
| `make security` | `uv run bandit -r app/ database/` |
| `make check-all` | lint + typecheck + test + security |
| `make db-up` | `docker compose up -d` |
| `make db-down` | `docker compose down --remove-orphans` |
| `make db-clean` | `docker compose down --volumes --remove-orphans` |
| `make db-shell` | psql shell into couscous database |
| `make clean` | remove `__pycache__`, `.pyc`, `.pytest_cache`, `reports/` |

## Project architecture

| Directory | Purpose |
|-----------|---------|
| `main.py` | Entrypoint: loads `.env`, calls `ft.run(app_run)` |
| `app/app.py` | Flet app lifecycle, route table (`_ROUTES`), `app_run` entrypoint |
| `app/context.py` | `PageContext` dataclass — holds `page`, `state`, `session`, session factory |
| `app/views/` | One file per route: `login_view`, `register_view`, `oauth_callback_view`, `home_view`, `about_view`, `feed_list_view`, `entry_list_view`, `entry_view`, `category_list_view` |
| `app/controls/` | Reusable UI: `feed_card`, `article_card`, `add_feed_dialog`, `confirm_dialog`, `nav_bar`, `oauth_buttons`, `tag_chip` |
| `app/services/` | Async service layer: `feed_service`, `entry_service`, `user_service`, `refresh_service`, `category_service`, `tag_service`, `oauth_service`, `feed_fetcher` |
| `database/service/database.py` | `get_db_session()` — async context manager wrapping async engine; `init_async_db()` |
| `database/models/couscous.py` | SQLModel models: `User`, `Feed`, `Entry`, `FeedMetadata`, `Category`, `EntryTag` |
| `app/state.py` | `State` class holding `user`, `active_feed_url`, `loading` |
| `tests/` | `pytest` + `pytest-asyncio`, one file per service/view/module |
| `openspec/` | Structured change artifacts (specs, proposals, designs, tasks) |

## Environment variables

`.env` is auto-loaded by `main.py` (via `dotenv`) and by tests via `tests/conftest.py`.

| Var | Default | Purpose |
|-----|---------|---------|
| `APP_WEB_HOST` | `127.0.0.1` | Bind address (use `0.0.0.0` to expose) |
| `APP_WORKERS` | `1` | Workers (1 = reload mode, >1 = production) |
| `APP_SERVER_PORT` | `8550` | Server port |
| `COUSCOUS_DATABASE_NAME` | `couscous` | Database name |
| `COUSCOUS_DATABASE_HOST` | `localhost` | Postgres host |
| `COUSCOUS_DATABASE_PORT` | `5432` | Postgres port |
| `COUSCOUS_DATABASE_USER` | `couscous` | Postgres user |
| `COUSCOUS_DATABASE_PASS` | `couscous` | Postgres password |
| `COUSCOUS_GOOGLE_CLIENT_ID` | (none) | Google OAuth client ID |
| `COUSCOUS_GOOGLE_CLIENT_SECRET` | (none) | Google OAuth client secret |
| `COUSCOUS_GITHUB_CLIENT_ID` | (none) | GitHub OAuth client ID |
| `COUSCOUS_GITHUB_CLIENT_SECRET` | (none) | GitHub OAuth client secret |
| `COUSCOUS_OAUTH_REDIRECT_URI` | `http://localhost:8550/oauth/callback` | OAuth redirect URI |

## Route table

| Prefix | Handler | Requires session | Public |
|--------|---------|-----------------|--------|
| `/login` | `login_view` | No | Yes |
| `/register` | `register_view` | No | Yes |
| `/oauth/callback` | `oauth_callback_view` | Yes | Yes |
| `/about` | `about_view` | No | Yes |
| `/feeds` | `feed_list_view` | Yes | No |
| `/feed/{url}` | `entry_list_view` | Yes | No |
| `/entry/{id}` | `entry_view` | Yes | No |
| `/categories` | `category_list_view` | Yes | No |
| `/` | `feed_list_view` | Yes | No |

Order matters: specific prefixes (`/feed/`, `/entry/`) must appear before generic ones (`/`).

## Test conventions

- All service tests use the `db_session` fixture (PostgreSQL via SQLModel async) from `tests/conftest.py`.
- Every service test is `@pytest.mark.asyncio` and takes `db_session` as first arg.
- Ensure `make db-up` is running before executing tests.
- Run all tests: `make test`
- Run a single test: `uv run pytest tests/test_feed_service.py::test_add_feed`
- Tests connect to `couscous_test` database (hardcoded in conftest), not `couscous`.

## Gotchas

- Password is stored as bcrypt hash via `app/services/user_service.py`.
- All service functions in `app/services/` are **async** and take `session` as first arg.
- `get_db_session()` in `database/service/database.py` is the single source for async sessions.
- `ruff` linting excludes `tests/` (configured in `pyproject.toml`).
- `mypy` only checks `app/` and `database/` dirs.
- `bandit` excludes `tests/` and `.venv/`.
- `.env` is gitignored; `.env.sample` is the template.
- Routes requiring a session receive a `PageContext` with an open `session`; public routes do not (they get `PageContext` with `session=None`).
- View handlers receive `PageContext` as first argument; `entry_view` also receives `entry_id: int` as second.

## OpenSpec

Structured changes live in `openspec/`. Skills in `.opencode/skills/openspec-*` handle the workflow. Use `/opsx-propose` for new change proposals, `/opsx-apply` to implement tasks.

## Convenções de Commit

- **Padrão:** [Conventional Commits](https://www.conventionalcommits.org/).
- **Formato obrigatório:** `<tipo>[escopo opcional]: <descrição em minúsculas>`
- **Tipos permitidos:**
  - `feat`: Nova funcionalidade.
  - `fix`: Correção de bug.
  - `docs`: Alterações na documentação.
  - `style`: Formatação (sem mudança de lógica).
  - `refactor`: Refatoração que não corrige bug nem adiciona feature.
  - `perf`: Melhoria de performance.
  - `test`: Adição ou correção de testes.
  - `chore`: Atualização de dependências, build, tarefas de manutenção.
- **Regras:**
  - A descrição deve ser no imperativo (ex: "adiciona rota de login" em vez de "adicionado rota de login").
  - Evite commits gigantes; divida as entregas em blocos lógicos.
