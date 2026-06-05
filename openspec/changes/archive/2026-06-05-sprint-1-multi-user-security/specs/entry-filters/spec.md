## ADDED Requirements

### Requirement: Filter entries by read status
The system SHALL allow the user to filter the entry list to show only unread entries.

#### Scenario: Show only unread entries
- **WHEN** user toggles the "Não lidos" filter in the entry list view
- **THEN** the system displays only entries where `is_read` is false

#### Scenario: Show all entries
- **WHEN** user toggles the "Não lidos" filter off
- **THEN** the system displays all entries for the current feed

### Requirement: Filter entries by importance
The system SHALL allow the user to filter the entry list to show only important (starred) entries.

#### Scenario: Show only important entries
- **WHEN** user toggles the "Importantes" filter in the entry list view
- **THEN** the system displays only entries where `is_important` is true

#### Scenario: Show all entries after important filter
- **WHEN** user toggles the "Importantes" filter off
- **THEN** the system displays all entries for the current feed
