## Why

Test coverage is currently thin: only 3 of 4 service files have tests, no views or controls are tested, the refresh service has zero coverage despite being the most critical component (HTTP fetching, feed parsing, entry creation). Two test files (`test_home.py`, `test_factory.py`) sit empty. This leaves the app vulnerable to regressions and makes refactoring risky.

## What Changes

- Add comprehensive tests for `refresh_service.py` covering feed fetching, parsing, entry creation, deduplication, and error handling
- Add tests for `app/state.py` (State class) and `app/app.py` (route dispatching)
- Add tests for all 4 reusable controls (`FeedCard`, `ArticleCard`, `AddFeedDialog`, `ConfirmDialog`)
- Add view-level tests for all 7 views (`login_view`, `register_view`, `home_view`, `feed_list_view`, `entry_list_view`, `entry_view`, `about_view`)
- Add model-level tests for database models (`User`, `Feed`, `Entry`, `FeedMetadata`, `FeedTag`)
- Fill the empty `test_home.py` and `test_factory.py` with actual tests
- Ensure coverage tool (`pytest-cov`) reports meaningful results with existing config targeting `app/`

## Capabilities

### New Capabilities
- `refresh-service-tests`: Tests for `refresh_service.py` — feed fetching, parsing (RSS/Atom), entry creation, deduplication, and error recovery
- `view-tests`: Tests for all view functions — rendering, navigation, event handling, and state updates
- `control-tests`: Tests for reusable UI controls — rendering, callbacks, and user interaction
- `app-core-tests`: Tests for `app/state.py` State class and `app/app.py` route dispatching
- `model-tests`: Tests for SQLModel database models — creation, validation, constraints, and relationships

### Modified Capabilities
<!-- None — no existing spec requirements change; this is purely additive test coverage -->

## Impact

- Affected code: `app/services/refresh_service.py`, `app/state.py`, `app/app.py`, all `app/views/*.py`, all `app/controls/*.py`, `database/models/couscous.py`
- New test files: `tests/test_refresh_service.py`, `tests/test_state.py`, `tests/test_app.py`, `tests/test_controls.py`, `tests/test_models.py`, additional per-view test files
- Fills empty files: `tests/test_home.py`, `tests/test_factory.py`
- Dependencies: may need `pytest-mock` or `responses` for HTTP mocking in refresh service tests
- No breaking changes — test-only additions
