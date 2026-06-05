## MODIFIED Requirements

### Requirement: List all feeds
The system SHALL display a list of all registered RSS feeds for the authenticated user on the feeds page.

#### Scenario: View feed list
- **WHEN** user navigates to `/feeds`
- **THEN** the system displays a list of feed titles owned by the current user

#### Scenario: Feed list is empty
- **WHEN** user navigates to `/feeds` and no feeds exist for the current user
- **THEN** the system displays an empty state message "Nenhum feed adicionado"

### Requirement: View articles from a feed
The system SHALL display a list of entries/articles for a selected feed, scoped to the authenticated user.

#### Scenario: Open feed entries
- **WHEN** user taps/clicks a feed in the feed list
- **THEN** the system navigates to `/feed/<feed_url>` and shows a list of article titles for that feed

#### Scenario: Empty feed
- **WHEN** user opens a feed that has no entries
- **THEN** the system shows "Nenhum artigo encontrado"

### Requirement: View article content
The system SHALL display the full content of a single article/entry.

#### Scenario: Open article
- **WHEN** user taps/clicks an article in the feed entry list
- **THEN** the system navigates to `/entry/<entry_id>` and shows the article title, author, date, and full content/summary

#### Scenario: Article with no content
- **WHEN** user opens an article that has only a summary (no content field)
- **THEN** the system displays the summary text instead

### Requirement: Toggle article importance
The system SHALL allow the user to mark an article as important (starred) or remove the importance mark.

#### Scenario: Star an article
- **WHEN** user taps the star icon on an article in `entry_view.py`
- **THEN** the system toggles `is_important` to true and the icon changes to a filled star immediately

#### Scenario: Unstar an article
- **WHEN** user taps the filled star icon on a starred article
- **THEN** the system toggles `is_important` to false and the icon changes to an outline star immediately
