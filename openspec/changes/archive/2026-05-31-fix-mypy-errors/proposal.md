## Why

Running `mypy .` reports 78 type errors across 14 files, masking real type issues and blocking clean CI. These are caused by Flet API mismatches (icons enum, control attributes, method names), SQLAlchemy async engine type-narrowing gaps, and missing optional handling.

## What Changes

- Fix all `ft.icons.*` attribute errors by using correct Flet icon constants
- Fix `ft.padding.all()` / `ft.alignment.center` not-found errors by importing or using correct access patterns
- Fix `update_async` not found on dialog controls
- Fix `TextThemeStyle` where `TextStyle` is expected
- Fix `page.show_snack_bar`, `page.dialog`, `page.session.set` unresolved attributes
- Fix DB engine union-type narrowing for `sessionmaker` and `engine.begin()`
- Fix `Entry.published` optional `.desc()` call
- Fix `Column()` unexpected `padding` keyword
- Fix missing `await` on `session.close()`
- Fix `get_session` return type annotation

## Capabilities

### New Capabilities

- `mypy-cleanup`: Resolve all mypy type errors in the codebase without changing `pyproject.toml` mypy rules

### Modified Capabilities

- *None* — spec-level behavior does not change; only type annotations and Flet API usage are corrected

## Impact

- **14 files** across `app/controls/`, `app/views/`, `app/services/`, `app/db.py`, `database/service/database.py`
- No runtime behavior changes — only type-correctness and API-correctness fixes
- No dependency changes
