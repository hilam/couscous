## Purpose

Define requirements for rendering HTML and plain text entry content in CousCous.

## Requirements

### Requirement: Render plain text with Markdown
The system SHALL render all entry content using `fletify-html` + `ft.Markdown`, including plain text.

#### Scenario: Plain text renders as Markdown
- **WHEN** content is plain text
- **THEN** the system SHALL convert it with `fletify-html` and display it using `ft.Markdown` with `GITHUB_WEB` extension set

### Requirement: Fallback to Markdown
If content type cannot be determined, the system SHALL fall back to `ft.Markdown`.

#### Scenario: Ambiguous content falls back to Markdown
- **WHEN** content does not clearly match HTML or plain text patterns
- **THEN** the system SHALL render it using `ft.Markdown` with `GITHUB_WEB` extension set
