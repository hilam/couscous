## Purpose

TBD — Back navigation provides a way for users to return to the previous view.

## Requirements

### Requirement: Back button on entry detail view

The entry detail view SHALL have a back button in the AppBar leading position that navigates to the feed's entry list.

#### Scenario: Click back from entry detail
- **WHEN** user is viewing an entry at `/entry/<id>`
- **AND** clicks the back button
- **THEN** the system SHALL navigate to `/feed/<feed_url>`

### Requirement: Back button on entry list view

The entry list view SHALL have a back button in the AppBar leading position that navigates to the feed list.

#### Scenario: Click back from entry list
- **WHEN** user is viewing entries at `/feed/<url>`
- **AND** clicks the back button
- **THEN** the system SHALL navigate to `/feeds`
