## Context

`ruff check .` produces 28 errors across 13 source files. The `pyproject.toml` lint configuration (`select` + `ignore`) must remain untouched. Each error class requires a specific code fix pattern.

## Goals / Non-Goals

**Goals:**
- Zero `ruff check .` errors after changes
- Every fix addresses the root cause per rule semantics (no `# noqa` suppression)
- All existing tests continue to pass

**Non-Goals:**
- No rule additions/removals or new ignores in `pyproject.toml`
- No refactoring beyond what's needed to satisfy the linter
- No functional changes to app behavior

## Decisions

| Error | Rule | Approach | Rationale |
|-------|------|----------|-----------|
| **PLR1714** — merge comparisons | `app/app.py:32` | `route in {"/feeds", "/"}` | Use set membership — idiomatic and shorter |
| **PLR2004** — magic value `120` | `app/controls/article_card.py:40` | Extract `SUMMARY_MAX_LENGTH = 120` constant | Named constant clarifies intent |
| **PLW0108** — unnecessary lambda | `app/controls/feed_card.py:29,31` | Pass method ref directly: `on_click=self._delete` | Lambda wrapper is redundant when method signature matches |
| **N806** — `Session` uppercase | `app/db.py:19` | Rename `Session → session_cls` (or lower-case pattern) | Convention for local variable shadowing a class reference |
| **FBT001/FBT002** — boolean positional args | `app/services/entry_service.py:18,27` | Make keyword-only: `async def mark_read(session, entry_id: int, *, read: bool = True)` | Rules disallow positional boolean args — keyword-only `*` separator is the least invasive fix |
| **TRY003/EM101** — exception message | `app/services/feed_service.py:14`, `app/services/user_service.py:16,30,33` | Assign message to variable before raising: `msg = "..."; raise ValueError(msg)` | Rule requires non-literal message or custom exception — variable assignment is simplest |
| **DTZ005/DTZ006** — datetime without tz | `app/services/refresh_service.py:30,51,63,64,65`, `database/models/couscous.py:31` | Use `datetime.now(tz=timezone.utc)` and `datetime.fromtimestamp(..., tz=timezone.utc)` | UTC is the standard timezone; fixes both DTZ005 and DTZ006 |
| **TC001** — import in type-checking block | `app/state.py:1` | Add `from __future__ import annotations` at top and/or wrap import in `if TYPE_CHECKING:` | Standard Python pattern for type-only imports |
| **E501** — line too long (89>88) | `app/views/about_view.py:29` | Split string across lines or shorten text | Trivial line-length fix |
| **C901** — function too complex | `app/views/feed_list_view.py:12` | Extract sub-logic into helper functions | McCabe complexity of 12 vs threshold 10 — minor extraction needed |
| **ERA001** — commented-out code | `database/service/database.py:13,19` | Remove the two commented `# await conn.run_sync(SQLModel.metadata.drop_all)` lines | Dead code should not remain |

## Risks / Trade-offs

- [Regression] Fixing C901 (complexity) may introduce subtle bugs if refactoring is aggressive → Mitigation: Extract one helper at a time, run tests after each.
- [TC001] Adding `from __future__ import annotations` changes stringification of annotations globally — may affect runtime type checks → Mitigation: Only wrap the import in `TYPE_CHECKING` guard, no `__future__` import needed.
- [FBT] Making booleans keyword-only requires updating all callers of `mark_read` and `mark_important` → Mitigation: Only 2 callers exist; grep and update both.
