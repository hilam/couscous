## Why

Flet 0.80.0 deprecated `page.go()` in favor of `page.push_route()`. The app currently uses `go()` in 7 source files across all views, producing deprecation warnings at runtime. This change silences those warnings and future-proofs against removal.

## What Changes

- Replace all `page.go(route)` calls with `page.push_route(route)` across all views and `app.py`
- 8 files affected: `app.py`, `login_view.py`, `home_view.py`, `feed_list_view.py`, `entry_list_view.py`, `entry_view.py`, `about_view.py`

## Capabilities

### New Capabilities

- `app-navigation`: Page routing via `push_route()` — all navigation actions (initial load, login redirect, feed/article clicks, bottom nav) use the new non-deprecated API.

### Modified Capabilities

None — no spec-level behavior changes. The routing behavior (which view is shown for which route) remains identical.

## Impact

- `app/app.py` — initial route navigation on app start
- `app/views/login_view.py` — post-login redirect
- `app/views/home_view.py` — navigation bar and button clicks
- `app/views/feed_list_view.py` — feed card clicks and navigation bar
- `app/views/entry_list_view.py` — article card clicks and navigation bar
- `app/views/entry_view.py` — navigation bar only
- `app/views/about_view.py` — navigation bar only
