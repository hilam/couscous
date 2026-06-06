## 1. Fix OAuth service SessionStore calls

- [x] 1.1 Replace dict-style assignment in `get_authorization_url()` (line 76) with `page.session.store.set(key, value)`
- [x] 1.2 Replace `.pop()` in `handle_callback()` (line 85) with `page.session.store.get(key)` + `page.session.store.remove(key)` — guard against missing key

## 2. Fix test mock

- [x] 2.1 Update `mock_page` fixture in `tests/test_oauth_service.py` to use a `MagicMock` with `set`/`get`/`remove` methods instead of a plain `dict`

## 3. Verify

- [x] 3.1 Run `uv run pytest tests/test_oauth_service.py` — all tests must pass
- [x] 3.2 Run `ruff check . && ruff format .` — no lint errors
- [x] 3.3 Run `uv run mypy .` — no type errors
