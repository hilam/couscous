## Context

`entry_view.py` (line 87-90) renders all entry content using `ft.Markdown`. RSS feeds provide content as HTML (from `<content:encoded>` or `<content>` elements) or plain text (from `<description>` or `<summary>`). `ft.Markdown` displays HTML tags as literal text, producing a poor user experience.

Only `entry_view.py` needs to change — the model, service, and data pipeline store content unchanged.

## Goals / Non-Goals

**Goals:**
- Render HTML entry content correctly using `ft.WebView`
- Render plain text entry content using `ft.Text` (preserving whitespace)
- Keep `ft.Markdown` as a fallback for any content that doesn't match HTML or plain text
- Minimal, focused change in `entry_view.py` only

**Non-Goals:**
- No HTML sanitization or rewriting of content
- No changes to how content is fetched, parsed, or stored
- No changes to `article_card.py` summary display (truncated plain text is fine)
- No new external dependencies

## Decisions

### HTML Detection: Simple tag regex
Check if content contains common HTML tags (`<html`, `<p>`, `<div>`, `<br`, `<table`, `<img`, `<a `, `<h[1-6]`) using a regex. This is fast, needs no dependencies, and reliably catches real RSS HTML content.

### HTML Rendering: `ft.WebView`
`ft.WebView` supports an `html` parameter to render raw HTML strings. It handles CSS, images, links, and all HTML formatting correctly.

Constraint: `ft.WebView` needs a fixed height. The design will wrap it in a `ft.Container` with a reasonable default height (e.g., `page.height - 300`) to fill available space while allowing scrolling.

### Plain Text Rendering: `ft.Text`
Simple `ft.Text` with `selectable=True` so users can copy text. No Markdown parsing needed.

### Fallback: `ft.Markdown`
Keep existing `ft.Markdown` rendering for content that doesn't match HTML or plain text patterns (e.g., actual Markdown content).

### Helper function pattern
Extract content type detection into a small private function `_get_content_renderer(page, content)` to keep the view function clean.

## Risks / Trade-offs

- [`ft.WebView` platform support] → `ft.WebView` requires a webview backend (WebView2 on Windows, WKWebView on macOS, WebView on Linux). If unavailable, the app should fall back gracefully. Mitigation: wrap in try/except or check `ft.WebView` availability at runtime, falling back to `ft.Markdown`.
- [Fixed height for WebView] → Content may be clipped or leave too much whitespace. Mitigation: wrap WebView in a scrollable `ft.Column` so the page scroll handles overflow; use `expand=True` on the WebView container.
- [HTML detection false positives] → A plain text article containing `<something>` could be misidentified as HTML. Mitigation: use a conservative threshold (require at least 2 HTML tag occurrences) and keep `ft.Markdown` as fallback.
