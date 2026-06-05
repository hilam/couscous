## Context

Current test coverage is limited to 3 service modules (`user_service`, `feed_service`, `entry_service`) with 26 test functions total. The refresh service, all views, all controls, app state, routing, and models have zero direct test coverage. Two test files (`test_home.py`, `test_factory.py`) are empty placeholders. The project uses `pytest` + `pytest-asyncio` with a PostgreSQL `couscous_test` database. Coverage tool (`pytest-cov`) is already configured targeting `app/`.

## Goals / Non-Goals

**Goals:**
- Add tests for `refresh_service.py` covering feed HTTP fetching, RSS/Atom parsing via `feedparser`, entry creation, deduplication, and error handling (network errors, malformed feeds, individual entry skipping)
- Add tests for all 7 views verifying they return correctly structured `ft.View` objects with expected controls and routing behavior
- Add tests for all 4 controls verifying rendering properties, callback wiring, and dialog behavior
- Add tests for `State` class and `app_run` route dispatching
- Add model-level tests for `User`, `Feed`, `Entry`, `FeedMetadata`, and `FeedTag` — creation, validation, constraints, relationships
- Fill empty `test_home.py` and `test_factory.py` files
- Maintain existing test conventions (`@pytest.mark.asyncio`, `db_session` fixture, helper functions)

**Non-Goals:**
- End-to-end Flet UI integration tests (requires running Flet app with real page rendering)
- 100% code coverage target (focus on meaningful behavior coverage)
- Modifying production code (test-only additions)
- Adding new test dependencies beyond stdlib `unittest.mock`
- Testing `database/service/` layer directly (exercised indirectly through other tests)
- Testing `main.py` entrypoint

## Decisions

### Decision 1: Use `unittest.mock.patch` for HTTP mocking in refresh service tests
**Rationale:** `httpx.get()` is called inside `asyncio.to_thread()` — we patch `httpx.get` at module level to return synthetic responses. No need for additional dependencies like `responses` or `pytest-httpx`. The mock can simulate successful RSS, Atom, error responses, and edge cases.

**Alternatives considered:** `responses` library (adds dependency), `pytest-httpx` (adds dependency), test HTTP server (complex). Stdlib mocking keeps dependencies minimal.

### Decision 2: View tests verify returned `ft.View` structure, not runtime rendering
**Rationale:** Full Flet rendering requires a running event loop with page context. Instead, call view functions with mocked `ft.Page` (using `unittest.mock.AsyncMock`) and assert the returned `ft.View` has correct route, controls, and properties. This tests the view composition logic without needing a real Flet runtime.

**Alternatives considered:** Flet's `ft.app(test_mode=True)` (complex setup, still limited), full integration with real page (requires windowing, not feasible in CI). Structural testing is pragmatic and catches the most common bugs.

### Decision 3: Control tests instantiate directly and assert properties
**Rationale:** Controls are Flet component subclasses with no side effects. Instantiate with test data, assert widget tree structure (`content`, `actions`, `title`, etc.) and callback wiring. No mocking needed for core behavior.

### Decision 4: Model tests use the existing `db_session` fixture
**Rationale:** Models are SQLModel table classes. Tests use the real PostgreSQL test database for constraint, relationship, and uniqueness validation — matching the approach already used for service tests.

### Decision 5: Test file organization mirrors the module structure
**Rationale:** Create `test_refresh_service.py`, `test_state.py`, `test_app.py`, `test_controls.py`, `test_models.py`, and per-view test files (`test_home_view.py`, `test_feed_list_view.py`, etc.). Keep `test_home.py` as the test for `home_view.py` (filling the empty file). Use `test_factory.py` for shared test data helpers.

### Decision 6: Use helper factory functions to reduce boilerplate
**Rationale:** Following the pattern in `test_entry_service.py` with `_make_user` and `_create_feed_and_entry`, create reusable factories in `test_factory.py` for creating feeds, entries, and mock parsed feed data. This reduces duplication across test files.

## Risks / Trade-offs

- [Risk] View tests may be brittle because they depend on Flet internal widget structure → Mitigation: Test at the semantic level (route name, control types, key text) rather than exact widget tree depth. If Flet API changes, only targeted tests break.
- [Risk] HTTP mocking may not cover all edge cases of real network behavior → Mitigation: Cover explicit error modes (timeout, 404, malformed XML) plus happy path. Mock the `httpx.get` return value, not lower-level transport.
- [Risk] `FeedMetadata` and `FeedTag` models appear unused in current codebase → Mitigation: Test them anyway for completeness; they may be used in future features or via direct queries.
- [Risk] Refresh service tests create many entries and may be slow → Mitigation: Use `db_session` fixture (which drops tables between tests) and keep test feeds small. Add `@pytest.mark.slow` if needed later.
