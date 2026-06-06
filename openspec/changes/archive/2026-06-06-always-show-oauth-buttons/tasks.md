## 1. Shared Control

- [x] 1.1 Create `app/controls/oauth_buttons.py` with `get_oauth_buttons(page, error_text)` function that always renders Google and GitHub buttons (no `is_provider_available` guard), and a private `_oauth_click` helper

## 2. Login View

- [x] 2.1 In `app/views/login_view.py`, remove `_oauth_click` and `_oauth_buttons` functions (lines 11-40), remove `from app.services import oauth_service` import, add `from app.controls.oauth_buttons import get_oauth_buttons` import
- [x] 2.2 Replace `_oauth_buttons(page, error_text)` call at line 89 with `get_oauth_buttons(page, error_text)`

## 3. Registration View

- [x] 3.1 In `app/views/register_view.py`, remove `_oauth_click` and `_oauth_buttons` functions (lines 11-40), remove `from app.services import oauth_service` import, add `from app.controls.oauth_buttons import get_oauth_buttons` import
- [x] 3.2 Replace `_oauth_buttons(page, error_text)` call at line 89 with `get_oauth_buttons(page, error_text)`

## 4. Verification

- [x] 4.1 Run `uv run pytest` to verify all existing tests pass
- [x] 4.2 Run `ruff check . && uv run mypy .` to verify lint and type-check pass
