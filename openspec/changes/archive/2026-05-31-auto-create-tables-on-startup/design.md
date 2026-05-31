## Context

The app currently requires a manual one-time setup step: running `init_async_db()` via a Python one-liner before starting the Flet application. This is documented in both the README and AGENTS.md. The `init_async_db()` function already exists and works correctly — it creates all tables using SQLModel's `metadata.create_all`, which is idempotent (uses `IF NOT EXISTS` semantics).

## Goals / Non-Goals

**Goals:**
- Eliminate the manual database initialization step by calling `init_async_db()` as part of app startup
- Ensure tables exist before any view or service function queries the database
- Keep the startup logic simple and non-blocking for the UI

**Non-Goals:**
- Schema migrations beyond `create_all` (e.g., Alembic) — out of scope
- Any changes to the existing `init_async_db()` or table model definitions
- Connection pooling or engine lifecycle changes

## Decisions

- **Call from `app/app.py` vs `main.py`**: Call from `app/app.py` inside `app_run`, before any view logic runs. This keeps `main.py` clean (just `ft.run(app_run)`) and places the init logic alongside other app lifecycle concerns. The call happens before the route handler is set up, so all subsequent service calls see an initialized database.
- **Sequential await vs fire-and-forget**: Use `await init_async_db()` — sequential and blocking within startup. The engine is already lazily initialized, so this incurs minimal delay (typically <100ms for first connection + table check). Fire-and-forget risks race conditions where a view query runs before tables exist.
- **No try/except wrapping**: Let exceptions propagate naturally. If the database is unreachable or misconfigured, the app should fail fast at startup rather than surfacing cryptic errors later.

## Risks / Trade-offs

- **Startup latency**: First startup is slower by one DB round-trip. Negligible in practice. Trade-off accepted for reliability.
- **Docker race condition**: If the app container starts before PostgreSQL, `init_async_db()` will fail and take down the app. Mitigation: Docker Compose health checks (already configured) should prevent this.
- **Overhead on every start**: `create_all` is a no-op if all tables exist. SQLAlchemy issues a few `SELECT` queries to check, but this is cheap and acceptable.
