## Purpose

Define requirements for theme and font scale customization in CousCous.

## Requirements

### Requirement: Theme mode selection
The system SHALL allow the user to choose between light theme, dark theme, or follow the system setting. The preference SHALL be persisted and restored on next login.

#### Scenario: Toggle selects theme mode
- **WHEN** user selects "Dark" in the theme toggle
- **THEN** the toggle highlights "Dark" and the page applies `ft.ThemeMode.DARK` immediately

#### Scenario: Switch to system theme
- **WHEN** user selects "System" in the theme toggle
- **THEN** the toggle highlights "System" and the page applies `ft.ThemeMode.SYSTEM` immediately

#### Scenario: Theme persisted on save
- **WHEN** user clicks "Salvar" after changing the theme toggle
- **THEN** the system persists the current `theme_mode` to the database and updates `State.theme_mode`

#### Scenario: Theme restored on login
- **WHEN** a user with `theme_mode="dark"` stored in the database logs in
- **THEN** the system reads the preference, updates State, and applies `ft.ThemeMode.DARK` on the page

#### Scenario: Default theme for new users
- **WHEN** a new user registers and logs in for the first time
- **THEN** `User.theme_mode` defaults to "light" and the page is in light mode

### Requirement: Font scale adjustment
The system SHALL allow the user to adjust the global text size via a slider, with a scale range of 0.8 to 1.5 in 0.1 increments. The preference SHALL be persisted and restored on next login.

#### Scenario: Preview updates in real time
- **WHEN** user moves the font scale slider
- **THEN** a preview text ("Aa") next to the slider updates its size in real time (local effect only)

#### Scenario: Font scale applied globally on save
- **WHEN** user clicks "Salvar" with slider at 1.3
- **THEN** `page.theme.text_theme` is scaled to 1.3x, the preference is persisted to DB, and `State.font_scale` is updated

#### Scenario: Font scale restored on login
- **WHEN** a user with `font_scale=1.2` logs in
- **THEN** the system reads the preference, updates State, and applies 1.2x via `page.theme`

#### Scenario: Save button disabled when no changes
- **WHEN** user has not changed theme or font scale since last save
- **THEN** the "Salvar" button is disabled

### Requirement: Settings view
The system SHALL provide a settings view at route `/about` with theme toggle, font scale slider + preview, a "Salvar" button, and an "About" button that opens a popup.

#### Scenario: Navigate to settings
- **WHEN** user taps "Config" in the NavigationBar
- **THEN** the app navigates to `/about` and displays the settings view

#### Scenario: Open about popup
- **WHEN** user taps the "Sobre" button in settings
- **THEN** a popup dialog shows the app name, version, and description (previously in about_view)

#### Scenario: Settings requires authentication
- **WHEN** an unauthenticated user navigates to `/about`
- **THEN** the app redirects to `/login`
