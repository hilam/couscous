## Context

Flet's `SessionStore` exposes explicit method calls (`set`, `get`, `remove`) — it does not implement `__setitem__`, `__getitem__`, or `pop()`. The OAuth service in `app/services/oauth_service.py` currently uses dict-style access, which fails at runtime:

- `get_authorization_url()` line 76: `page.session.store[key] = value`
- `handle_callback()` line 85: `page.session.store.pop(key, None)`

The test fixture in `tests/test_oauth_service.py` hides the bug by replacing `SessionStore` with a plain `dict` that supports both operations.

## Goals / Non-Goals

**Goals:**
- Fix `get_authorization_url()` to use `store.set()` instead of dict assignment
- Fix `handle_callback()` to use `store.get()` + `store.remove()` instead of `.pop()`
- Update the test mock to use `set`/`get`/`remove` so it catches future API misuse

**Non-Goals:**
- No changes to OAuth flow behavior, state management, or session lifecycle
- No changes to any other service or view
- No changes to the `SessionStore` class itself

## Decisions

**Decision: Use `set`/`get`/`remove` directly on `SessionStore`**

The `SessionStore` API is the contract. There's no alternative — the only alternative would be wrapping `SessionStore` to mimic a dict, which adds unnecessary indirection. The API exists as designed; the code should use it correctly.

**Decision: `handle_callback` uses two-step get+remove instead of a single `.pop()`**

`SessionStore` has no atomic get-and-remove. Since this is a synchronous in-memory operation on a single session, a race condition between `get` and `remove` is impossible — there's no concurrency within a single Flet page session.

**Decision: Test mock uses `MagicMock` with `set`/`get`/`remove`**

Replace `page.session.store = {}` with a `MagicMock` that fully matches the `SessionStore` interface. Tests will then catch any further misuse.

## Risks / Trade-offs

- [Low] `get()` + `remove()` is not atomic → Mitigation: Single-threaded WebSocket session, no concurrent access possible
- [Low] The `MagicMock` test fixture won't perfectly replicate every `SessionStore` edge case → Mitigation: The actual `SessionStore` is trivial in-memory storage; the mock only needs `set`/`get`/`remove`
