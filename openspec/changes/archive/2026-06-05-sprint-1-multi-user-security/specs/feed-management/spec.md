## MODIFIED Requirements

### Requirement: Add feed by URL
The system SHALL allow the user to add a new RSS feed by providing its URL. The feed SHALL be associated with the authenticated user's `user_id`.

#### Scenario: Add valid feed
- **WHEN** user taps the "Adicionar feed" button and enters a valid RSS feed URL
- **THEN** the system creates the feed associated with the current user and shows it in the feed list

#### Scenario: Add duplicate feed
- **WHEN** user enters a URL that already exists for the current user
- **THEN** the system shows an error message "Feed já cadastrado"

### Requirement: Remove feed
The system SHALL allow the user to remove an existing feed. Only feeds owned by the authenticated user SHALL be removable.

#### Scenario: Remove feed
- **WHEN** user taps the delete icon on a feed card and confirms
- **THEN** the system removes the feed (and its entries) owned by the current user from the database, and the feed disappears from the list

#### Scenario: Cancel removal
- **WHEN** user taps the delete icon on a feed card and then cancels
- **THEN** the feed remains in the list unchanged
