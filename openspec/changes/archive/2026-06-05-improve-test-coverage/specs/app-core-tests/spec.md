## ADDED Requirements

### Requirement: State initializes with default values
The system SHALL test that `State` is created with `user=None`, `active_feed_url=None`, and `loading=False`.

#### Scenario: New State instance
- **WHEN** a new `State()` is created
- **THEN** `state.user` SHALL be None
- **AND** `state.active_feed_url` SHALL be None
- **AND** `state.loading` SHALL be False

### Requirement: State attributes are mutable
The system SHALL test that `State` attributes can be set and read back after mutation.

#### Scenario: Set and read user
- **WHEN** `state.user` is set to a User instance
- **THEN** `state.user` SHALL return that User instance

#### Scenario: Set and read active_feed_url
- **WHEN** `state.active_feed_url` is set to "https://example.com/rss"
- **THEN** `state.active_feed_url` SHALL return "https://example.com/rss"

#### Scenario: Set and read loading
- **WHEN** `state.loading` is set to True
- **THEN** `state.loading` SHALL return True

### Requirement: App run sets up page configuration
The system SHALL test that `app_run` configures the page title, theme, and padding before setting session state and route handler.

#### Scenario: Page is configured on startup
- **WHEN** `app_run` is called with a mock page
- **THEN** `page.title` SHALL be "CousCous - Leitor de RSS"
- **AND** `page.theme_mode` SHALL be `ThemeMode.LIGHT`
- **AND** `page.padding` SHALL be 0
- **AND** `page.on_route_change` SHALL be set to a callable

### Requirement: State is stored in page session
The system SHALL test that `app_run` stores a `State` instance in `page.session.store`.

#### Scenario: State stored in session
- **WHEN** `app_run` is called
- **THEN** `page.session.store.set` SHALL be called with key "state" and a `State` instance

### Requirement: Initial route is login page
The system SHALL test that `app_run` pushes "/login" as the initial route.

#### Scenario: Push initial route
- **WHEN** `app_run` is called
- **THEN** `page.push_route` SHALL be called with "/login"
