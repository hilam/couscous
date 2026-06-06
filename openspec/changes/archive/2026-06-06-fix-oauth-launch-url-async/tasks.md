## 1. Fix launch_url call

- [x] 1.1 Replace `ft.UrlLauncher().launch_url(uri)` with `page.launch_url(uri)` in `_oauth_click()` (`app/controls/oauth_buttons.py` line 9)

## 2. Verify

- [x] 2.1 Run `uv run pytest tests/test_oauth_service.py` — all tests must pass
- [x] 2.2 Run `ruff check . && ruff format .` — no lint errors
- [x] 2.3 Run `uv run mypy .` — no new type errors
