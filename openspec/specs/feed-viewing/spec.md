## Purpose

Define requirements for viewing RSS feeds and articles in CousCous.

## Requirements

### Requirement: List all feeds
The system SHALL display a list of all registered RSS feeds for the authenticated user on the feeds page, grouped by category. Uncategorized feeds SHALL appear under a "Sem categoria" header displayed last.

#### Scenario: View feed list grouped by category
- **WHEN** user navigates to `/feeds` and has feeds in one or more categories
- **THEN** the system displays feeds grouped under their respective category section headers

#### Scenario: View feed list with uncategorized feeds
- **WHEN** user navigates to `/feeds` and has feeds without a category
- **THEN** the system displays those feeds under a "Sem categoria" section header, shown after all categorized groups

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
