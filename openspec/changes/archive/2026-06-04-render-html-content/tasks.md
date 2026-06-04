## 1. Content type detection helper

- [x] 1.1 Add `_is_html(content)` function in `entry_view.py` that checks for common HTML tags using regex
- [x] 1.2 Add `_get_content_renderer(page, content)` that returns the appropriate Flet control based on content type

## 2. Update entry_view.py rendering

- [x] 2.1 Replace the hardcoded `ft.Markdown(content, ...)` on line 87-90 with the renderer from `_get_content_renderer`
- [x] 2.2 Wrap WebView in a scrollable container with appropriate height (`page.height - 300` or `expand=True`)

## 3. Fallback and edge cases

- [x] 3.1 Handle case where `ft.WebView` is not available on the platform (fall back to `ft.Markdown`)
- [x] 3.2 Inform the user the OS requirement to use `ft.WebView`
- [x] 3.3 Ensure null/empty content doesn't break the renderer
