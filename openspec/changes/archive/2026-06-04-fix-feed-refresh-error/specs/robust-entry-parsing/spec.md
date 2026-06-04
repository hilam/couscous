## ADDED Requirements

### Requirement: Resilient entry parsing

The system SHALL process each RSS entry independently so that a single malformed entry does not cause the entire feed refresh to fail.

#### Scenario: Feed with one malformed entry
- **WHEN** a feed contains a mix of valid and malformed entries
- **THEN** valid entries SHALL be persisted
- **AND** malformed entries SHALL be silently skipped
- **AND** the feed metadata (title, link) SHALL still be updated

#### Scenario: Feed with all valid entries
- **WHEN** all entries in a feed are well-formed
- **THEN** all entries SHALL be persisted
- **AND** the feed metadata SHALL be updated
- **AND** `last_exception` SHALL remain None

#### Scenario: Feed metadata still saved when HTTP succeeds but entries fail
- **WHEN** the HTTP request succeeds and feed metadata is parsed
- **AND** all entries are malformed (none persisted)
- **THEN** the feed metadata SHALL still be saved
- **AND** `last_exception` SHALL remain None (metadata success)

### Requirement: Show actual error to user

The system SHALL display the actual exception message in the error SnackBar so the user can diagnose the issue.

#### Scenario: Refresh fails with specific error
- **WHEN** `refresh_single_feed` fails with `ConnectionError: DNS resolution failed`
- **THEN** the SnackBar SHALL display "ConnectionError: DNS resolution failed"
