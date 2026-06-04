## Why

RSS feed entries almost universally provide content as HTML, but `entry_view.py` renders it with `ft.Markdown`, which cannot render HTML — resulting in raw HTML tags (`<p>`, `<a>`, etc.) displayed as visible text instead of formatted content.

## What Changes

- Detect whether entry content is HTML or plain text before rendering
- Render HTML content using `ft.WebView` instead of `ft.Markdown`
- Render plain text content using `ft.Text` instead of `ft.Markdown`
- Keep `ft.Markdown` only for content that is explicitly Markdown (or leave it as fallback if neither HTML nor plain text is detected)
- No changes to the entry model, service layer, or data pipeline — only the presentation layer in `entry_view.py`

## Capabilities

### New Capabilities
- `html-content-rendering`: Detect content type (HTML vs plain text) and render it with the appropriate Flet control (`ft.WebView` for HTML, `ft.Text` for plain text, `ft.Markdown` as fallback)

### Modified Capabilities

None.

## Impact

- **File changed**: `app/views/entry_view.py` — content rendering logic
- **No new dependencies**: `ft.WebView` is built into Flet
- **No model/service changes**: content remains stored as-is in the database
