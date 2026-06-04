## Context

`entry_view.py` currently has a three-way content rendering pipeline: HTML detection via regex → `ft.WebView`, lone-tag fallback → `ft.Markdown`, plain text → `ft.Text`. The `ft.WebView` approach only works on iOS, Android, and macOS. This change replaces it with `fletify-html`, an HTML-to-Markdown converter, so all content renders via `ft.Markdown` on all platforms.

## Goals / Non-Goals

**Goals:**
- Replace `ft.WebView` with `fletify-html` for HTML-to-Markdown conversion
- Remove content-type detection logic (`_is_html`, `_HTML_TAG_RE`, etc.)
- Simplify `_get_content_renderer` to a single `fletify-html` + `ft.Markdown` pipeline
- Add `fletify-html` as a project dependency

**Non-Goals:**
- No changes to entry model, service layer, or data storage
- No changes to `article_card.py` or other views
- No changes to how content is fetched or stored

## Decisions

### Replace WebView with fletify-html + ft.Markdown
`fletify-html` converts HTML strings to GitHub-flavored Markdown. This works on every platform Flet supports (Linux, Windows, macOS, Web, iOS, Android) since `ft.Markdown` is universally available.

### Remove content-type detection entirely
Since `fletify-html` handles HTML gracefully (converting it to Markdown) and passes plain text through unchanged, there is no need to detect content type. The `_is_html()` function, regex patterns, and threshold constants are all removed.

### Simplified rendering function
`_get_content_renderer` becomes a thin wrapper: convert with `fletify-html`, then render with `ft.Markdown`. The `page` parameter is no longer needed since `ft.WebView` is removed.

## Risks / Trade-offs

- [`fletify-html` conversion fidelity] → Complex HTML (tables, embedded CSS, scripts) may lose formatting during conversion. Mitigation: `fletify-html` targets GFM output; accept that some visual fidelity is traded for cross-platform compatibility. The original link is always available via "Ver original" button.
- [New dependency availability] → `fletify-html` must be installable on all target platforms. Mitigation: if unavailable, fall back to raw `ft.Markdown` with the original HTML content (current behavior).
