## 1. Dependency setup

- [x] 1.1 Add `fletify-html` to `pyproject.toml` dependencies

## 2. Core implementation

- [x] 2.1 Rewrite `_get_content_renderer` to use `fletify-html` conversion + `ft.Markdown` for all content
- [x] 2.2 Remove `_is_html()`, `_HTML_TAG_RE`, `_HTML_TAG_THRESHOLD`, `import re`, `import contextlib`
- [x] 2.3 Remove `page` parameter from `_get_content_renderer` (no longer needed without `ft.WebView`)

## 3. Verify

- [x] 3.1 Run `ruff check .` and `uv run mypy .`
