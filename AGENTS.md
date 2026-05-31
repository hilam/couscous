# AGENTS.md – CousCous RSS Feed Reader

### Repository‑wide Commands  

- **Run the web UI** (Rio app)
  ```bash
  python -m rio run web
  ```
  *`rio` discovers the `app` object in `web/__init__.py` and serves it on the default port (8080).*

- **Start the FastAPI backend**
  ```bash
  uvicorn api.main:app --reload
  ```
  *`api/main.py` defines the FastAPI instance named **app**.*

- **Create the database schema** (run once, before any API call)
  ```bash
  python -c "from database.service.database import init_db; init_db()"
  ```

- **Run the test suite**
  ```bash
  pytest
  ```
  *Tests rely on the fixtures in `tests/conftest.py` which spin up a temporary SQLite DB and a Flask‑style test client for the web app.*

- **Run a single test**
  ```bash
  pytest tests/test_home.py
  ```

- **Lint / Type‑check** (project uses `ruff` and `pyright` if installed)
  ```bash
  ruff check .
  pyright .
  ```

- **Load environment variables** (required by the test fixtures and the apps)
  ```bash
  export $(cat .env | xargs)   # if you create an .env file
  ```
  *The only variables referenced are:*

  | Variable | Meaning |
  |----------|---------|
  | `COUSCOUS_WEB_PROTOCOL`, `COUSCOUS_WEB_HOST`, `COUSCOUS_WEB_PORT` | Construct the web base URL used by fixtures |
  | `COUSCOUS_API_PROTOCOL`, `COUSCOUS_API_HOST`, `COUSCOUS_API_PORT` | Construct the API base URL used by fixtures |
  | `DB_TYPE` (used internally as `db_type`) | `"asyncpg"` → async engine, otherwise sync engine |
  | `DB_URL` | SQLAlchemy connection string (e.g. `sqlite+aiosqlite:///test.db`) |

---

### Database / ORM Details  

- **Engine selection** (`database/service/config.py`)
  ```python
  db_type = os.getenv("DB_TYPE", "sqlite")
  DB_URL = os.getenv("DB_URL", "sqlite:///couscous.db")
  ```
  *If `DB_TYPE` is `"asyncpg"` the async engine is used; otherwise a sync engine is created.*

- **Models** (`database/models/couscous.py`)
  - `User`: `id` (PK, optional), `name` (PK, unique), `password`
  - `Feed`: `url` PK, many optional fields, relationship to `Entry` via `entries`
  - `Entry`: composite PK (`id`, `feed` FK to `feeds.url`)

- **Session helper** (`database/service/database.py`)
  - `get_session` yields an `AsyncSession` when using asyncpg, otherwise a regular session.

- **Init functions**
  - `init_db()` sync version, called with `python -c "…"`
  - `init_async_db()` async version, used only if you need an async‑only setup.

---

### FastAPI Endpoints (`api/main.py`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health‑check, returns `{ "ping": "pong!" }` |
| `GET` | `/` | Short message pointing to `/docs` |
| `POST` | `/register` | Creates a `User`; returns the created model |
| `GET` | `/feeds` | Returns a list of **Feed** objects (only `title` field is sent) |
| `POST` | `/feeds` | Creates a new **Feed** entry |

*All routes depend on `get_session` for DB access.*

---

### Rio UI Structure (`web/__init__.py`)

- **Theme** – primary `#01dffdff`, secondary `#0083ffff`, light mode.
- **Pages** (ordered as they appear in the navigation bar)
  1. **Home** – `pages.HomePage` (default route `''`)
  2. **NewsPage** – `pages.NewsPage` (`'news-page'`)
  3. **AboutPage** – `pages.AboutPage` (`'about-page'`)
- **Root component** – `pages.RootPage` (holds the persistent navbar/footer).

The app is instantiated as
```python
app = rio.App(
    name='web',
    pages=[…],
    build=pages.RootPage,
    theme=theme,
    assets_dir=Path(__file__).parent / "assets",
)
```
---

### Testing Fixtures (`tests/conftest.py`)

- `web_address` & `api_address` – build URLs from the environment variables above.
- `app` – creates a Flask‑style test client from `web.create_app` (imported implicitly by `web/__init__.py`).
- `client` – `app.test_client()` used by the endpoint tests.
- `runner` – `app.test_cli_runner()` for CLI‑style tests (currently unused).

---

### Gotchas / Agent‑Specific Tips  

- **Database creation must happen before the first API request** – otherwise the tables are missing and the endpoint will error with “no such table”.
- The **async vs sync engine** is chosen solely by `DB_TYPE`. Most local usage leaves it at the default sync engine, so `init_db()` (sync) is sufficient.
- The **web UI runs on port 8080** by default; changing the port requires setting `COUSCOUS_WEB_PORT` **before** starting `rio`.
- The **FastAPI app is not started automatically** by the Rio app; they are independent processes. Run them in separate terminals or use a process manager.
- The FastAPI routes return **only a subset** of model fields (e.g., `Feed` returns only `title`). If you need full data, add a custom response model.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, invoke the `skill` tool with `skill: "graphify"` before doing anything else.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
