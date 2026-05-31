## ADDED Requirements

### Requirement: Refresh all feeds
The system SHALL allow the user to trigger a refresh of all feeds to fetch the latest articles.

#### Scenario: Manual refresh triggers background update
- **WHEN** user taps the "Atualizar" button
- **THEN** the system starts fetching new articles from all feeds in background and shows a loading indicator

#### Scenario: New articles appear after refresh
- **WHEN** the background refresh completes and new articles are found
- **THEN** the feed entry list updates to include the new articles

### Requirement: Non-blocking refresh
The feed refresh operation SHALL NOT block the UI.

#### Scenario: UI remains responsive during refresh
- **WHEN** a feed refresh is running in the background
- **THEN** the user can still navigate, scroll, and interact with the app
