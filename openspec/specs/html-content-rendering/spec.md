## Purpose

Define requirements for rendering HTML and plain text entry content in CousCous.

## Requirements

### Requirement: Detect content type
The system SHALL detect whether entry content is HTML or plain text before choosing how to render it.

#### Scenario: Content with HTML tags detected as HTML
- **WHEN** entry content contains at least one common HTML tag (`<html>`, `<p>`, `<div>`, `<br`, `<table>`, `<img`, `<a `, `<h1`-`<h6`)
- **THEN** the system SHALL render it with `ft.WebView`

#### Scenario: Content without HTML tags detected as plain text
- **WHEN** entry content contains no HTML tags
- **THEN** the system SHALL render it with `ft.Text`

### Requirement: Render HTML content with WebView
The system SHALL render HTML content using `ft.WebView` with the raw HTML string.

#### Scenario: HTML content renders in WebView
- **WHEN** content is detected as HTML
- **THEN** the system SHALL display the HTML formatted content in a `ft.WebView` control

#### Scenario: WebView has appropriate height
- **WHEN** content is rendered in `ft.WebView`
- **THEN** the WebView SHALL be sized to fill available viewport height and be scrollable

### Requirement: Render plain text with Text control
The system SHALL render plain text content using `ft.Text` with `selectable=True`.

#### Scenario: Plain text renders as selectable text
- **WHEN** content is detected as plain text
- **THEN** the system SHALL display it in a `ft.Text` control and the text SHALL be selectable

### Requirement: Fallback to Markdown
If content type cannot be determined, the system SHALL fall back to `ft.Markdown`.

#### Scenario: Ambiguous content falls back to Markdown
- **WHEN** content does not clearly match HTML or plain text patterns
- **THEN** the system SHALL render it using `ft.Markdown` with `GITHUB_WEB` extension set
