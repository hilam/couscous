## ADDED Requirements

### Requirement: Convert HTML content to Markdown
The system SHALL convert HTML entry content to Markdown using `fletify-html` before rendering.

#### Scenario: HTML content converted to Markdown
- **WHEN** entry content contains HTML
- **THEN** the system SHALL convert it to Markdown using `fletify-html`

#### Scenario: Plain text passes through unchanged
- **WHEN** entry content is plain text (no HTML)
- **THEN** `fletify-html` SHALL return the text unchanged

### Requirement: Render converted content with Markdown
The system SHALL render all entry content using `ft.Markdown` with `GITHUB_WEB` extension set, after `fletify-html` conversion.

#### Scenario: Converted HTML renders as Markdown
- **WHEN** HTML content has been converted to Markdown by `fletify-html`
- **THEN** the system SHALL display it using `ft.Markdown` with `GITHUB_WEB` extension set

#### Scenario: Plain text renders as Markdown
- **WHEN** plain text content has passed through `fletify-html`
- **THEN** the system SHALL display it using `ft.Markdown` with `GITHUB_WEB` extension set
