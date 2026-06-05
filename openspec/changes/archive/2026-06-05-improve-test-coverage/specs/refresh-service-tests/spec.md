## ADDED Requirements

### Requirement: Refresh service fetches and parses a valid feed
The system SHALL test that `refresh_single_feed` fetches a feed URL, parses RSS/Atom content, creates entries for each item, and updates feed metadata.

#### Scenario: Successful RSS feed refresh
- **WHEN** a feed URL returns valid RSS XML with 3 entries
- **THEN** `refresh_single_feed` SHALL create 3 Entry rows linked to the feed and set `feed.title`, `feed.link`, and `feed.updated`
- **AND** `feed.last_exception` SHALL be None

#### Scenario: Successful Atom feed refresh
- **WHEN** a feed URL returns valid Atom XML with entries
- **THEN** `refresh_single_feed` SHALL parse entries correctly from Atom namespace

### Requirement: Refresh service skips duplicate entries
The system SHALL test that `refresh_single_feed` does not create duplicate entries when the same entry link already exists for the feed.

#### Scenario: Entry already exists in database
- **WHEN** a feed entry has a link that already exists in the entries table for that feed
- **THEN** the entry SHALL be skipped and no duplicate created

### Requirement: Refresh service handles HTTP errors gracefully
The system SHALL test that `refresh_single_feed` catches HTTP errors and stores the exception message without crashing.

#### Scenario: Feed URL returns HTTP 404
- **WHEN** `httpx.get()` raises an HTTP 404 error
- **THEN** `feed.last_exception` SHALL contain the error message
- **AND** no entries SHALL be created for the feed

#### Scenario: Feed URL times out
- **WHEN** `httpx.get()` raises a timeout exception
- **THEN** `feed.last_exception` SHALL contain the error message
- **AND** the function SHALL not propagate the exception

### Requirement: Refresh service handles malformed feed content
The system SHALL test that `refresh_single_feed` handles malformed or empty XML without crashing.

#### Scenario: Feed returns empty response body
- **WHEN** the HTTP response body is empty
- **THEN** `feedparser.parse()` SHALL return an empty feed and no entries SHALL be created

#### Scenario: Feed returns non-XML content
- **WHEN** the HTTP response body is not valid XML (e.g., HTML page)
- **THEN** the function SHALL not crash and SHALL handle the parse result gracefully

### Requirement: Refresh service handles individual entry parsing errors
The system SHALL test that `refresh_single_feed` skips malformed entries without failing the entire refresh for valid entries.

#### Scenario: One entry in the feed is malformed
- **WHEN** a feed has 3 entries but one is missing its `id` and `link`
- **THEN** the malformed entry SHALL be skipped (not crash)
- **AND** the other 2 valid entries SHALL still be created

### Requirement: Refresh all feeds iterates over user feeds
The system SHALL test that `refresh_all_feeds` calls `refresh_single_feed` for every feed belonging to the user.

#### Scenario: User has multiple feeds
- **WHEN** a user has 3 feeds and `refresh_all_feeds` is called
- **THEN** all 3 feeds SHALL be refreshed
- **AND** entries from all feeds SHALL be created

### Requirement: Refresh service persists entry metadata correctly
The system SHALL test that created entries have correct metadata including published date, author, summary, and content.

#### Scenario: Entry has all metadata fields
- **WHEN** a feed entry contains title, link, author, published date, summary, and content
- **THEN** the created Entry SHALL have those fields populated correctly
- **AND** `added_by` SHALL be "system"
- **AND** `last_updated`, `first_updated`, `first_updated_epoch` SHALL be set
