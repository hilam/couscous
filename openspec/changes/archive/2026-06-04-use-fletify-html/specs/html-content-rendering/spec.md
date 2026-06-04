## REMOVED Requirements

### Requirement: Detect content type
**Reason**: Content type detection is no longer needed — `fletify-html` handles both HTML and plain text.
**Migration**: Remove `_is_html()` and regex-based detection logic.

### Requirement: Render HTML content with WebView
**Reason**: `ft.WebView` is not available on all platforms (Linux, Web). Replaced by `fletify-html` + `ft.Markdown`.
**Migration**: Replace `ft.WebView` with `fletify-html` conversion followed by `ft.Markdown` rendering.

## MODIFIED Requirements

### Requirement: Render plain text with Text control
The system SHALL render all entry content using `fletify-html` + `ft.Markdown`, including plain text.

#### Scenario: Plain text renders as Markdown
- **WHEN** content is plain text
- **THEN** the system SHALL convert it with `fletify-html` and display it using `ft.Markdown` with `GITHUB_WEB` extension set
- **AND** the text SHALL NOT include `selectable=True` (rendered via Markdown)
