## MODIFIED Requirements

### Requirement: Add feed by URL
The system SHALL allow the user to add a new RSS feed by providing its URL. The feed SHALL be associated with the authenticated user's `user_id`. The user MAY optionally select a category for the feed; if no category is selected, the feed remains uncategorized.

#### Scenario: Add valid feed
- **WHEN** user taps the "Adicionar feed" button and enters a valid RSS feed URL
- **THEN** the system creates the feed associated with the current user and shows it in the feed list

#### Scenario: Add valid feed with category
- **WHEN** user taps the "Adicionar feed" button, enters a valid RSS feed URL, and selects a category
- **THEN** the system creates the feed associated with the current user and the selected category, and shows it grouped under that category in the feed list

#### Scenario: Add duplicate feed
- **WHEN** user enters a URL that already exists for the current user
- **THEN** the system shows an error message "Feed já cadastrado"
