## 1. Feed Service Changes

- [x] 1.1 Make `add_feed` return the created `Feed` object (already returns, verify)
- [x] 2.1 In `on_feed_added`, after `add_feed` succeeds, import and call `refresh_single_feed` with the created feed
- [x] 2.2 On success, navigate to `/feed/<url>` via `page.push_route`
- [x] 2.3 On refresh failure (exception), show SnackBar with error message but keep feed in list

## 3. Verification

- [x] 3.1 Run `ruff check .` and `uv run mypy .` — no new errors
- [x] 3.2 Run `uv run pytest` — existing tests pass
