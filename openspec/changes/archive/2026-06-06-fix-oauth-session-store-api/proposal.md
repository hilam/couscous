## Why

Flet's `SessionStore` is not a dict — it exposes `set()`/`get()`/`remove()` methods. The OAuth service treats it as a dict with `store[key] = value` assignment and `store.pop()`, causing a `TypeError` when users click "Entrar com Google" or "Entrar com GitHub". The bug has gone undetected because the test mock replaces `SessionStore` with a plain dict.

## What Changes

- Replace `page.session.store[key] = value` with `page.session.store.set(key, value)` in `get_authorization_url()`
- Replace `page.session.store.pop(key, None)` with `get()` + `remove()` in `handle_callback()`
- Fix the test fixture to mock `SessionStore` with proper `set`/`get`/`remove` methods instead of a plain dict

## Capabilities

### New Capabilities

None — this is a bug fix, not a new capability.

### Modified Capabilities

None — the spec-level behavior (store state, retrieve state, clean state) is unchanged. Only the implementation API calls are corrected.

## Impact

- `app/services/oauth_service.py` — lines 76 and 85
- `tests/test_oauth_service.py` — `mock_page` fixture (line 11)
