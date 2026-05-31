## 1. App Entry Point

- [x] 1.1 Replace `page.go("/login")` with `page.push_route("/login")` in `app/app.py`

## 2. Views

- [x] 2.1 Replace `page.go("/feeds")` with `page.push_route("/feeds")` in `app/views/login_view.py`
- [x] 2.2 Replace `page.go(...)` with `page.push_route(...)` in `app/views/home_view.py` (2 occurrences)
- [x] 2.3 Replace `page.go(...)` with `page.push_route(...)` in `app/views/feed_list_view.py` (2 occurrences)
- [x] 2.4 Replace `page.go(...)` with `page.push_route(...)` in `app/views/entry_list_view.py` (3 occurrences)
- [x] 2.5 Replace `page.go(...)` with `page.push_route(...)` in `app/views/entry_view.py` (1 occurrence)
- [x] 2.6 Replace `page.go(...)` with `page.push_route(...)` in `app/views/about_view.py` (1 occurrence)

## 3. Verification

- [x] 3.1 Run `ruff check .` to verify no linting issues
- [x] 3.2 Run `uv run mypy .` to verify type correctness
- [x] 3.3 Run `python -m pytest` to verify tests still pass (17/17)
- [ ] 3.4 Run the app with `uv run flet run -d` and verify no deprecation warnings about `go()` in the console
