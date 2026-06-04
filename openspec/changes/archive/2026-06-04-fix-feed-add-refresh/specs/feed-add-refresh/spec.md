## ADDED Requirements

### Requirement: Feed auto-refresh on add

When a user adds a new RSS feed URL, the system SHALL fetch and parse the feed content immediately so the feed metadata and entries appear without a manual refresh.

#### Scenario: Add new feed with valid URL
- **WHEN** user submits a valid RSS feed URL
- **THEN** system creates the feed record
- **AND** system fetches and parses the feed content
- **AND** system populates feed title, link, and metadata
- **AND** system creates entry records for all items
- **AND** user is navigated to the feed's entry list view

#### Scenario: Add new feed with invalid URL
- **WHEN** user submits an invalid or unreachable URL
- **THEN** system creates the feed record with `last_exception` set
- **AND** user stays on the feed list view
- **AND** an error message is displayed

#### Scenario: Add duplicate feed
- **WHEN** user submits a URL that is already registered
- **THEN** system rejects the operation
- **AND** a "Feed já cadastrado" snackbar is shown
- **AND** the feed list remains unchanged
