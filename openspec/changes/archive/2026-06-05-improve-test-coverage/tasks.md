## 1. Setup — test infrastructure

- [x] 1.1 Create shared test data factory helpers in `tests/test_factory.py` — functions to create mock `Feed` objects, mock `Entry` objects, mock `httpx.Response` objects with RSS/Atom XML bodies, and a `_make_user` helper
- [x] 1.2 Add any missing test fixtures to `tests/conftest.py` if needed (e.g., reusable mock page factory)

## 2. Refresh service tests

- [x] 2.1 Create `tests/test_refresh_service.py` with test for `refresh_single_feed` — successful RSS feed with 3 entries: mock `httpx.get` to return valid RSS XML, verify 3 `Entry` rows created, verify `feed.title` and `feed.last_exception=None`
- [x] 2.2 Test `refresh_single_feed` — successful Atom feed: mock `httpx.get` to return valid Atom XML, verify entries are parsed correctly
- [x] 2.3 Test `refresh_single_feed` — entry deduplication: create an existing entry beforehand, mock feed containing the same entry link, verify it is skipped and no duplicate created
- [x] 2.4 Test `refresh_single_feed` — HTTP 404 error: mock `httpx.get` to raise `httpx.HTTPStatusError`, verify `feed.last_exception` contains the error message and no entries created
- [x] 2.5 Test `refresh_single_feed` — timeout: mock `httpx.get` to raise a timeout exception, verify graceful handling
- [x] 2.6 Test `refresh_single_feed` — empty response body: mock response with empty text, verify no crash and no entries created
- [x] 2.7 Test `refresh_single_feed` — malformed XML: mock response with non-XML content, verify no crash and graceful handling
- [x] 2.8 Test `refresh_single_feed` — individual entry skipping: mock feed with 3 entries where one is missing `id` and `link`, verify it's skipped and the other 2 are created
- [x] 2.9 Test `refresh_single_feed` — entry metadata persistence: verify created entry has correct title, author, published date, summary, content, `added_by="system"`, and timestamps
- [x] 2.10 Test `refresh_all_feeds` — user with 3 feeds: verify all 3 feeds are refreshed and entries from all feeds are created

## 3. Model tests

- [x] 3.1 Create `tests/test_models.py` with test for `User` model: successful creation, auto-generated `id`, and duplicate name integrity error
- [x] 3.2 Test `Feed` model: successful creation with defaults (`stale=0`, `updates_enabled=1`, `added` timestamp), duplicate URL error, foreign key violation for invalid `user_id`
- [x] 3.3 Test `Entry` model: successful creation with defaults (`read=0`, `important=0`, auto `id`), foreign key violation for invalid `feed` URL, required fields
- [x] 3.4 Test `Feed` ↔ `Entry` relationship: `feed.entries` returns associated entries, `entry.url_feed` returns parent feed
- [x] 3.5 Test `FeedMetadata` model: successful creation with composite primary key (`feed`, `key`), duplicate key error
- [x] 3.6 Test `FeedTag` model: successful creation with composite primary key (`feed`, `tag`), duplicate tag error

## 4. Control tests

- [x] 4.1 Create `tests/test_controls.py` with test for `FeedCard`: verify title, link rendered in widget tree; fallback to URL when no title
- [x] 4.2 Test `FeedCard` callbacks: verify `on_click` fires on card tap, `on_delete` fires on delete button press
- [x] 4.3 Test `ArticleCard`: full entry data rendering (title bold, author, date, truncated summary), read entry styling (normal weight, grey icon), unread entry styling (bold weight, blue icon)
- [x] 4.4 Test `ArticleCard` click callback fires
- [x] 4.5 Test `AddFeedDialog`: submit with valid URL fires `on_submit` and closes/clears; cancel does not fire callback; empty URL submit does nothing
- [x] 4.6 Test `ConfirmDialog`: title and message rendered; confirm button fires `on_confirm` and closes; cancel button closes without firing `on_confirm`

## 5. App core tests (State + routing)

- [x] 5.1 Create `tests/test_state.py`: verify `State()` initializes with `user=None`, `active_feed_url=None`, `loading=False`; verify attribute mutation
- [x] 5.2 Create `tests/test_app.py`: test `app_run` configures page title, theme, padding, and sets `on_route_change`
- [x] 5.3 Test `app_run` stores `State` in `page.session.store` with key "state"
- [x] 5.4 Test `app_run` pushes initial route "/login"
- [x] 5.5 Test route dispatch: `/login` → `login_view`, `/feeds` → `feed_list_view`, `/feed/{url}` → `entry_list_view` with `active_feed_url` set, `/entry/{id}` → `entry_view`, `/about` → `about_view`, `/register` → `register_view`, `/` → `home_view`
- [x] 5.6 Test unauthenticated redirect: `/feeds` without user redirects to `login_view`
- [x] 5.7 Test public routes allowed without auth: `/about` and `/register`

## 6. View tests

- [x] 6.1 Create `tests/test_login_view.py`: verify returned `ft.View` has route "/login", contains username field, password field, login button. Test login button triggers service call.
- [x] 6.2 Create `tests/test_register_view.py` (or extend existing): verify returned `ft.View` has route "/register", contains username and password fields
- [x] 6.3 Fill `tests/test_home.py` with tests for `home_view`: verify returned `ft.View` has route "/", contains NavigationBar
- [x] 6.4 Create `tests/test_feed_list_view.py`: verify returned `ft.View` has route "/feeds", AppBar title "Meus Feeds", ListView, NavigationBar; verify add feed button opens dialog; verify refresh button triggers refresh
- [x] 6.5 Create `tests/test_entry_list_view.py`: verify returned `ft.View` shows feed entries with correct route; verify entry cards are rendered; verify back navigation
- [x] 6.6 Create `tests/test_entry_view.py`: verify returned `ft.View` has route "/entry/{id}", displays entry title and content, mark read/important buttons work
- [x] 6.7 Create `tests/test_about_view.py`: verify returned `ft.View` has route "/about", contains NavigationBar

## 7. Validation

- [x] 7.1 Run full test suite with `uv run pytest -v` and verify all new tests pass
- [x] 7.2 Run coverage report with `uv run pytest --cov=app --cov-report=term-missing` and verify meaningful coverage increase
- [x] 7.3 Run `ruff check .` and `uv run mypy .` to ensure no lint/type issues in test files
