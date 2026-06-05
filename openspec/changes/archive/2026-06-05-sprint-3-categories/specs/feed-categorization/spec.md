## ADDED Requirements

### Requirement: Assign category to feed on creation
The system SHALL allow the user to optionally select a category when adding a new feed.

#### Scenario: Add feed with category
- **WHEN** user adds a feed and selects "Tech" as the category
- **THEN** the feed is created with `category_id` pointing to "Tech" and appears grouped under "Tech" in the feed list

#### Scenario: Add feed without category
- **WHEN** user adds a feed without selecting a category
- **THEN** the feed is created with `category_id = NULL` and appears in the "Sem categoria" group

#### Scenario: Category dropdown shows tree
- **WHEN** user opens the add-feed dialog
- **THEN** the category selector displays all categories in a hierarchical dropdown with indentation for child levels, including a "Sem categoria" default option

### Requirement: Feeds grouped by category in list view
The system SHALL display feeds grouped by their assigned category in the feed list view.

#### Scenario: Feeds in multiple categories
- **WHEN** user has feeds in "Tech" and "News" categories
- **THEN** the feed list shows "Tech" as a section header followed by its feeds, then "News" as a section header followed by its feeds

#### Scenario: Uncategorized feeds
- **WHEN** user has feeds without a category
- **THEN** those feeds appear under a "Sem categoria" section header, displayed last

#### Scenario: Empty category
- **WHEN** a category exists but has no feeds
- **THEN** the category is not displayed in the feed list (only categories with feeds appear)

### Requirement: Change feed category
The system SHALL allow the user to change a feed's category after creation.

#### Scenario: Move feed to different category
- **WHEN** user changes a feed's category from "Tech" to "News"
- **THEN** the feed immediately moves to the "News" group in the feed list

#### Scenario: Remove feed from category
- **WHEN** user sets a feed's category to none ("Sem categoria")
- **THEN** the feed moves to the "Sem categoria" group
