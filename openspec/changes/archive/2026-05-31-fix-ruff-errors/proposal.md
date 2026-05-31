## Why

`ruff check .` reports 28 lint errors across the codebase. Every rule violation should be fixed rather than ignored — the project chose these rules deliberately in `pyproject.toml`. Leaving them unfiled degrades code quality and masks regressions in CI.

## What Changes

- Fix all 28 ruff errors across 8 source files without disabling any configured rules.
- No functional changes — only code transformations that satisfy the configured lint rules.
- No changes to `pyproject.toml` lint configuration (no rules added/removed, no ignores added).

## Capabilities

### New Capabilities

_(None — this is purely a lint-cleanup change with no new functionality.)_

### Modified Capabilities

_(None — no spec-level requirement changes.)_

## Impact

- **Files affected**: `app/app.py`, `app/controls/article_card.py`, `app/controls/feed_card.py`, `app/db.py`, `app/services/entry_service.py`, `app/services/feed_service.py`, `app/services/refresh_service.py`, `app/services/user_service.py`, `app/state.py`, `app/views/about_view.py`, `app/views/feed_list_view.py`, `database/models/couscous.py`, `database/service/database.py`
- **Expectation**: `ruff check .` passes cleanly with zero errors after changes.
- **No footprint**: No new dependencies, no new APIs, no new models.
