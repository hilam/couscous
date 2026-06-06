## 1. OAuth State Persistence

- [x] 1.1 In `app/services/oauth_service.py`, modify `get_authorization_url(page, provider)` to store `code_verifier` and `provider` in `page.session.store` under key `oauth_state_{state}` instead of module-level `_oauth_states` dict
- [x] 1.2 In `app/services/oauth_service.py`, modify `handle_callback(page, code, state)` to retrieve and pop state from `page.session.store` instead of module-level `_oauth_states` dict
- [x] 1.3 Remove the module-level `_oauth_states` dict from `app/services/oauth_service.py`

## 2. Update Callers (new `page` parameter)

- [x] 2.1 In `app/controls/oauth_buttons.py`, pass `page` to `get_authorization_url(page, provider)` in `_oauth_click`
- [x] 2.2 In `app/views/oauth_callback_view.py`, pass `page` to `handle_callback(page, code, state_param)`

## 3. Fix `launch_url` Deprecation

- [x] 3.1 In `app/controls/oauth_buttons.py`, replace `await page.launch_url(uri)` with `ft.UrlLauncher().launch_url(uri)` (synchronous, no await)
- [x] 3.2 In `app/views/entry_view.py`, replace `page.launch_url(entry.link or \"\")` with `ft.UrlLauncher().launch_url(entry.link or \"\")`

## 4. Update Tests

- [x] 4.1 In `tests/test_oauth_service.py`, update calls to `get_authorization_url()` to pass a mock `page` with `page.session.store` as a dict, and `handle_callback()` calls (if any) similarly
- [x] 4.2 In `tests/test_oauth_service.py`, remove or adapt any test that directly accesses the removed `_oauth_states` dict

## 5. Verification

- [x] 5.1 Run `uv run pytest tests/test_oauth_service.py` to verify OAuth tests pass
- [x] 5.2 Run `ruff check . && uv run mypy .` to verify lint and type-check pass
