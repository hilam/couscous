## ADDED Requirements

### Requirement: View functions return valid ft.View objects
The system SHALL test that each view function returns an `ft.View` instance with the correct route and controls present.

#### Scenario: Login view returns correct structure
- **WHEN** `login_view` is called with a page and state
- **THEN** the returned View SHALL have route "/login"
- **AND** SHALL contain a TextField for username and a TextField for password
- **AND** SHALL contain a login button

#### Scenario: Feed list view returns correct structure
- **WHEN** `feed_list_view` is called with a page and state
- **THEN** the returned View SHALL have route "/feeds"
- **AND** SHALL contain an AppBar with title "Meus Feeds"
- **AND** SHALL contain a ListView for feeds
- **AND** SHALL contain a NavigationBar

#### Scenario: Entry list view returns correct structure
- **WHEN** `entry_list_view` is called with a page and state after setting `state.active_feed_url`
- **THEN** the returned View SHALL have route matching the feed URL
- **AND** SHALL contain an AppBar and a ListView for entries

#### Scenario: Entry view returns correct structure
- **WHEN** `entry_view` is called with a page, state, and a valid entry_id
- **THEN** the returned View SHALL have route "/entry/{id}"
- **AND** SHALL display the entry title and content

#### Scenario: Home view returns correct structure
- **WHEN** `home_view` is called with a page and state
- **THEN** the returned View SHALL have route "/"
- **AND** SHALL contain a NavigationBar

#### Scenario: About view returns correct structure
- **WHEN** `about_view` is called with a page and state
- **THEN** the returned View SHALL have route "/about"
- **AND** SHALL contain a NavigationBar

#### Scenario: Register view returns correct structure
- **WHEN** `register_view` is called with a page and state
- **THEN** the returned View SHALL have route "/register"
- **AND** SHALL contain username and password fields

### Requirement: View tests use mocked Flet page
The system SHALL use `unittest.mock.AsyncMock` for the `ft.Page` argument in view tests, providing mock implementations for `update()`, `push_route()`, and `go()`.

#### Scenario: View function calls page update on interaction
- **WHEN** a view handles a user action (e.g., button click)
- **THEN** the test SHALL verify `page.update()` was called

### Requirement: Route dispatching covers all defined routes
The system SHALL test that `app_run` dispatches each route to the correct view function.

#### Scenario: Navigate to /login shows login view
- **WHEN** the route changes to "/login"
- **THEN** `login_view` SHALL be called and its result appended to page views

#### Scenario: Navigate to /feeds shows feed list view
- **WHEN** the route changes to "/feeds" and user is logged in
- **THEN** `feed_list_view` SHALL be called and its result appended to page views

#### Scenario: Navigate to /feed/{url} shows entry list view
- **WHEN** the route changes to "/feed/some-url"
- **THEN** `entry_list_view` SHALL be called and `state.active_feed_url` SHALL be set

#### Scenario: Navigate to /entry/{id} shows entry view
- **WHEN** the route changes to "/entry/42"
- **THEN** `entry_view` SHALL be called with entry_id 42

#### Scenario: Unauthenticated user redirected to login
- **WHEN** the route changes to "/feeds" and `state.user` is None
- **THEN** the view SHALL be redirected to `login_view`

#### Scenario: Public routes accessible without authentication
- **WHEN** the route changes to "/about" or "/register" and `state.user` is None
- **THEN** the corresponding view SHALL be shown without redirect
