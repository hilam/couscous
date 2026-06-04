## Why

`ft.WebView(html=...)` is only officially supported on iOS, Android, and macOS — it does not work on Linux or Web platforms. This limits cross-platform compatibility for rendering HTML entry content.

## What Changes

- Replace `ft.WebView` with `fletify-html` library for all HTML content rendering
- `fletify-html` converts HTML to Markdown, which is then displayed via `ft.Markdown`
- Remove the HTML-detection logic and `_is_html` / `_get_content_renderer` helper functions
- Simplify `entry_view.py` to always render content through `fletify-html` + `ft.Markdown` pipeline
- Add `fletify-html` to project dependencies in `pyproject.toml`

## Capabilities

### New Capabilities
- `html-to-markdown`: Convert HTML entry content to Markdown using `fletify-html`, then render with `ft.Markdown`

### Modified Capabilities
- `html-content-rendering`: Replaced `ft.WebView`-based rendering with `fletify-html` + `ft.Markdown` approach

## Impact

- **Files changed**: `app/views/entry_view.py` — rewrite content rendering logic; `pyproject.toml` — add dependency
- **New dependency**: `fletify-html` (add to `pyproject.toml` dependencies)
- **Removed**: `import re`, `import contextlib`, `_HTML_TAG_RE`, `_HTML_TAG_THRESHOLD`, `_is_html()`, `_get_content_renderer()`
