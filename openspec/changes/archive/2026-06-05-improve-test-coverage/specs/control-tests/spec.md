## ADDED Requirements

### Requirement: FeedCard renders feed information correctly
The system SHALL test that `FeedCard` displays the feed title (or URL if no title) and link in its widget tree.

#### Scenario: FeedCard with title and link
- **WHEN** a `FeedCard` is created with a Feed that has title "My Blog" and link "https://example.com"
- **THEN** the card content SHALL display "My Blog" as the title text
- **AND** SHALL display "https://example.com" as the subtitle text

#### Scenario: FeedCard with no title falls back to URL
- **WHEN** a `FeedCard` is created with a Feed that has no title but has URL "https://example.com/rss"
- **THEN** the card content SHALL display the URL as the title text

### Requirement: FeedCard fires click and delete callbacks
The system SHALL test that `FeedCard` invokes `on_click` when the card is tapped and `on_delete` when the delete button is pressed.

#### Scenario: Click callback fires
- **WHEN** the card's ListTile `on_click` is triggered
- **THEN** the `on_click` callback SHALL be called with a control event

#### Scenario: Delete callback fires
- **WHEN** the delete IconButton is pressed
- **THEN** the `on_delete` callback SHALL be called with a control event

### Requirement: ArticleCard renders entry information correctly
The system SHALL test that `ArticleCard` displays the entry title, author, date, and summary in its widget tree, with visual distinction for read vs unread entries.

#### Scenario: ArticleCard with full entry data
- **WHEN** an `ArticleCard` is created with an Entry that has title, author, published date, and summary
- **THEN** the card SHALL display the title with bold weight
- **AND** SHALL display author and formatted date in the subtitle
- **AND** SHALL display truncated summary (max 120 chars)

#### Scenario: ArticleCard for read entry shows different styling
- **WHEN** an `ArticleCard` is created with a read Entry (`entry.read == 1`)
- **THEN** the title SHALL use normal font weight (not bold)
- **AND** the leading icon color SHALL be GREY_400

#### Scenario: ArticleCard for unread entry shows emphasis
- **WHEN** an `ArticleCard` is created with an unread Entry (`entry.read == 0`)
- **THEN** the title SHALL use bold font weight
- **AND** the leading icon color SHALL be BLUE_400

#### Scenario: ArticleCard click fires callback
- **WHEN** the card's ListTile `on_click` is triggered
- **THEN** the `on_click` callback SHALL be called

### Requirement: AddFeedDialog submits valid URLs
The system SHALL test that `AddFeedDialog` invokes `on_submit` with the URL when the submit button is pressed with non-empty input.

#### Scenario: Submit with valid URL
- **WHEN** the URL field contains "https://example.com/feed.xml" and the submit button is pressed
- **THEN** `on_submit` SHALL be called with the URL string
- **AND** the dialog SHALL close (`open = False`)
- **AND** the URL field SHALL be cleared

#### Scenario: Cancel closes without submitting
- **WHEN** the cancel button is pressed
- **THEN** the dialog SHALL close (`open = False`)
- **AND** `on_submit` SHALL NOT be called

#### Scenario: Submit with empty URL does nothing
- **WHEN** the submit button is pressed with empty URL field
- **THEN** `on_submit` SHALL NOT be called
- **AND** the dialog SHALL remain open

### Requirement: ConfirmDialog fires confirmation callback
The system SHALL test that `ConfirmDialog` invokes `on_confirm` when the confirm button is pressed, and closes on both confirm and cancel.

#### Scenario: Confirm button triggers callback
- **WHEN** the confirm button is pressed
- **THEN** `on_confirm` SHALL be called
- **AND** the dialog SHALL close

#### Scenario: Cancel button closes dialog
- **WHEN** the cancel button is pressed
- **THEN** the dialog SHALL close
- **AND** `on_confirm` SHALL NOT be called

### Requirement: ConfirmDialog renders title and message
The system SHALL test that `ConfirmDialog` displays the provided title and message text.

#### Scenario: Dialog renders provided text
- **WHEN** a `ConfirmDialog` is created with title "Remove Feed" and message "Are you sure?"
- **THEN** the dialog title SHALL be "Remove Feed"
- **AND** the content text SHALL be "Are you sure?"
