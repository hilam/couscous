## 1. Refresh Service — Separate metadata commit from entry processing

- [x] 1.1 Commit feed metadata (title, link, updated) before processing entries, so at least the feed header is saved
- [x] 1.2 Wrap each entry creation in try/except so a malformed entry is skipped instead of aborting the entire feed
- [x] 1.3 Log (print) the error of each skipped entry for debugging

## 2. Feed List View — Show actual error message

- [x] 2.1 In `on_feed_added`, show `str(feed.last_exception)` in the SnackBar instead of generic message

## 3. Verify

- [x] 3.1 Run `ruff check .` and `uv run mypy .` — no new errors
- [x] 3.2 Run `uv run pytest` — existing tests pass
