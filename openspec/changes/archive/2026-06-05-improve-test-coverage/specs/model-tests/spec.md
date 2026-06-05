## ADDED Requirements

### Requirement: User model enforces uniqueness constraint
The system SHALL test that creating two users with the same name raises an integrity error.

#### Scenario: Duplicate username
- **WHEN** a User with name "alice" is committed to the database
- **AND** another User with name "alice" is committed
- **THEN** the second commit SHALL raise an integrity error

#### Scenario: User with all required fields can be created
- **WHEN** a User is created with `name="bob"` and `password="secret"`
- **THEN** the User SHALL be persisted and `id` SHALL be auto-generated

### Requirement: Feed model enforces primary key and foreign key constraints
The system SHALL test that Feed requires a unique URL and valid user_id reference.

#### Scenario: Feed with duplicate URL raises error
- **WHEN** two Feeds with the same URL are committed
- **THEN** the second commit SHALL raise an integrity error

#### Scenario: Feed with invalid user_id raises error
- **WHEN** a Feed is created with a non-existent `user_id`
- **THEN** the commit SHALL raise a foreign key violation

#### Scenario: Feed with all required fields can be created
- **WHEN** a Feed is created with valid `url` and `user_id`
- **THEN** the Feed SHALL be persisted with default values for `stale=0` and `updates_enabled=1`
- **AND** `added` SHALL be auto-set to current timestamp

### Requirement: Entry model enforces foreign key and required field constraints
The system SHALL test that Entry requires valid feed and user references, and auto-applies default values.

#### Scenario: Entry with invalid feed URL raises error
- **WHEN** an Entry is created with a non-existent `feed` URL
- **THEN** the commit SHALL raise a foreign key violation

#### Scenario: Entry with all required fields can be created
- **WHEN** an Entry is created with valid `feed`, `user_id`, `title`, `link`, and required datetime fields
- **THEN** the Entry SHALL be persisted with `read=0`, `important=0`, and an auto-generated `id`

### Requirement: Feed and Entry have correct relationship
The system SHALL test that accessing `feed.entries` returns associated Entry objects and `entry.url_feed` returns the parent Feed.

#### Scenario: Access entries from feed
- **WHEN** a Feed has 2 associated Entries in the database
- **THEN** `feed.entries` SHALL return a list containing both entries

#### Scenario: Access feed from entry
- **WHEN** an Entry is associated with a Feed
- **THEN** `entry.url_feed` SHALL return the parent Feed instance

### Requirement: FeedMetadata model stores key-value pairs per feed
The system SHALL test that FeedMetadata can be created and queried.

#### Scenario: Create and query FeedMetadata
- **WHEN** a FeedMetadata is created with a valid feed URL, key "language", and value "en"
- **THEN** the record SHALL be persisted and retrievable by feed and key

#### Scenario: FeedMetadata unique constraint
- **WHEN** two FeedMetadata records have the same feed URL and key
- **THEN** the second commit SHALL raise an integrity error

### Requirement: FeedTag model stores tags per feed
The system SHALL test that FeedTag can be created and queried.

#### Scenario: Create and query FeedTag
- **WHEN** a FeedTag is created with a valid feed URL and tag "technology"
- **THEN** the record SHALL be persisted and retrievable by feed

#### Scenario: FeedTag unique constraint
- **WHEN** two FeedTag records have the same feed URL and tag
- **THEN** the second commit SHALL raise an integrity error
