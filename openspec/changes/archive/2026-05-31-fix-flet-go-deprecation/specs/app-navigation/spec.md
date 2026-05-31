## ADDED Requirements

### Requirement: Navigate between pages using push_route

All page navigation SHALL use `page.push_route(route)` instead of the deprecated `page.go(route)`. The `on_route_change` handler SHALL clear the view stack (`page.views.clear()`) and append the correct view for the incoming route.

#### Scenario: Initial navigation on app start

- **WHEN** the Flet app starts
- **THEN** `page.push_route("/login")` is called and the login view is displayed

#### Scenario: Login redirect

- **WHEN** user successfully logs in or registers
- **THEN** `page.push_route("/feeds")` is called and the feed list view is displayed

#### Scenario: Navigate via bottom navigation bar

- **WHEN** user taps a destination on the NavigationBar
- **THEN** `page.push_route()` is called with the corresponding route

#### Scenario: Navigate via feed card click

- **WHEN** user taps a feed card
- **THEN** `page.push_route(f"/feed/{feed_url}")` is called

#### Scenario: Navigate via article card click

- **WHEN** user taps an article card
- **THEN** `page.push_route(f"/entry/{entry_id}")` is called

#### Scenario: Navigate via button click

- **WHEN** user clicks "Ver meus feeds" button on the home view
- **THEN** `page.push_route("/feeds")` is called
