## Context

Running `mypy .` on the CousCous codebase produces 78 errors across 14 files. The errors fall into 10 categories:

1. **Flet icons enum** (30 errors) — `ft.icons.RSS_FEED`, `ft.icons.HOME`, etc. not found by mypy
2. **Flet padding/alignment** (7 errors) — `ft.padding.all()`, `ft.alignment.center` not resolvable
3. **TextThemeStyle vs TextStyle** (9 errors) — `style=ft.TextThemeStyle.*` where `TextStyle` expected
4. **Page API** (6 errors) — `page.show_snack_bar`, `page.dialog`, `page.session.set` not found
5. **update_async on controls** (3 errors) — dialogs calling `self.update_async()`
6. **DB engine union narrowing** (10 errors) — `AsyncEngine | Engine` in `sessionmaker` and `engine.begin()`
7. **Optional .desc()** (2 errors) — `Entry.published` is `datetime | None`
8. **Column padding kwarg** (1 error) — `Column()` doesn't accept `padding`
9. **Missing await** (1 error) — `session.close()` without `await`
10. **Return type** (1 error) — async generator with wrong return annotation

All `pyproject.toml` mypy settings must remain unchanged.

## Goals / Non-Goals

**Goals:**
- Resolve all 78 mypy errors with minimal code changes
- Preserve all runtime behavior exactly

**Non-Goals:**
- Changing mypy configuration in `pyproject.toml`
- Upgrading Flet or other dependencies
- Refactoring beyond what type correctness requires

## Decisions

1. **Type narrowing with `isinstance` checks** — For `AsyncEngine | Engine` union, use explicit `isinstance(engine, AsyncEngine)` branches instead of `# type: ignore` or casts. This is type-safe and clear.

2. **Optional handling with `assert` or `if`** — For `Entry.published.desc()`, guard with `if entry.published is not None` or use `coalesce` in the SQL expression.

3. **No `# type: ignore` comments** — Prefer fixing the root cause rather than suppressing errors, to keep the codebase clean.

4. **Flet icon fixes via type-ignore** — Since Flet's type stubs are incomplete and we cannot change `pyproject.toml`, use targeted `# type: ignore[attr-defined]` on icon/padding/alignment references, or switch to string-based icon references where available.

## Risks / Trade-offs

- **Flet type stubs are incomplete** → Using `# type: ignore` on Flet attributes is acceptable since we cannot upgrade the dependency or change config; this is a stub issue, not a code issue.
- **DB engine changes affect two files** (`app/db.py` and `database/service/database.py`) → These are the most complex fixes; test with `uv run mypy .` after each change.
