## Capability: theme-settings

### Test: CRITICAL — Toggle selects theme mode
**Traces**: `specs/theme-settings/spec.md` → Requirement: Theme mode selection
- **GIVEN** user is on the settings view
- **WHEN** user selects "Dark" in the theme toggle
- **THEN** the toggle highlights "Dark" and `page.theme_mode` is set to `ft.ThemeMode.DARK` immediately

### Test: Switch to system theme
**Traces**: `specs/theme-settings/spec.md` → Requirement: Theme mode selection
- **GIVEN** user is on the settings view
- **WHEN** user selects "System" in the theme toggle
- **THEN** the toggle highlights "System" and `page.theme_mode` is set to `ft.ThemeMode.SYSTEM`

### Test: CRITICAL — Theme persisted on save button
**Traces**: `specs/theme-settings/spec.md` → Requirement: Theme mode selection
- **GIVEN** user changed toggle to "Dark"
- **WHEN** user clicks "Salvar"
- **THEN** `State.theme_mode` is "dark" and the DB has `theme_mode="dark"` for this user

### Test: CRITICAL — Theme restored on login
**Traces**: `specs/theme-settings/spec.md` → Requirement: Theme mode selection
- **GIVEN** a user with `theme_mode="dark"` stored in the database
- **WHEN** the user logs in
- **THEN** State gets `theme_mode="dark"` and `page.theme_mode` is set to `ft.ThemeMode.DARK`

### Test: Default theme for new users
**Traces**: `specs/theme-settings/spec.md` → Requirement: Theme mode selection
- **GIVEN** a newly registered user
- **WHEN** the user logs in for the first time
- **THEN** `theme_mode` defaults to "light" and page is in light mode

### Test: Preview text updates in real time (local effect only)
**Traces**: `specs/theme-settings/spec.md` → Requirement: Font scale adjustment
- **GIVEN** user is on the settings view
- **WHEN** user moves the slider to 1.3
- **THEN** the preview "Aa" text scales to 1.3x, but other page text remains at 1.0x

### Test: CRITICAL — Font scale applied globally on save
**Traces**: `specs/theme-settings/spec.md` → Requirement: Font scale adjustment
- **GIVEN** slider at 1.3 and user clicks "Salvar"
- **THEN** `page.theme.text_theme` scales to 1.3x, `State.font_scale=1.3`, and DB has `font_scale=1.3`

### Test: Font scale restored on login
**Traces**: `specs/theme-settings/spec.md` → Requirement: Font scale adjustment
- **GIVEN** a user with `font_scale=1.2` stored in the database
- **WHEN** the user logs in
- **THEN** State gets `font_scale=1.2` and page applies 1.2x via `page.theme`

### Test: Save button disabled when no changes
**Traces**: `specs/theme-settings/spec.md` → Requirement: Font scale adjustment
- **GIVEN** user just opened settings (no changes made)
- **THEN** the "Salvar" button is disabled

### Test: CRITICAL — Settings view renders with all controls
**Traces**: `specs/theme-settings/spec.md` → Requirement: Settings view
- **GIVEN** an authenticated user
- **WHEN** user navigates to `/about`
- **THEN** the view shows: theme toggle (light/dark/system), font scale slider + preview, "Salvar" button (disabled), and "Sobre" button

### Test: Settings redirects unauthenticated users
**Traces**: `specs/theme-settings/spec.md` → Requirement: Settings view
- **GIVEN** an unauthenticated user
- **WHEN** user navigates to `/about`
- **THEN** the app redirects to `/login`

### Test: About popup displays app info
**Traces**: `specs/theme-settings/spec.md` → Requirement: Settings view
- **GIVEN** user is on the settings view
- **WHEN** user taps the "Sobre" button
- **THEN** a popup dialog shows "CousCous", version, and description

## Capability: app-navigation

### Test: CRITICAL — Config destination in NavBar
**Traces**: `specs/app-navigation/spec.md` → Requirement: NavigationBar with 4 destinations
- **GIVEN** an authenticated user on any page
- **WHEN** user views the NavigationBar
- **THEN** the 4th destination is labeled "Config" with SETTINGS icon

### Test: Config navigates to settings
**Traces**: `specs/app-navigation/spec.md` → Requirement: NavigationBar with 4 destinations
- **GIVEN** an authenticated user with NavBar visible
- **WHEN** user taps "Config" on the NavBar
- **THEN** `page.push_route("/about")` is called and the settings view is displayed

### Test: Config highlighted on settings page
**Traces**: `specs/app-navigation/spec.md` → Requirement: NavigationBar with 4 destinations
- **GIVEN** user is on the `/about` (settings) route
- **WHEN** user views the NavBar
- **THEN** the "Config" destination index (3) is selected

## Edge Cases

- **ThemeMode.SYSTEM unsupported**: If the platform does not support `SYSTEM`, the app should fall back to `LIGHT` gracefully (no crash)
- **Font scale boundary 0.8**: Slider at minimum should render readable text
- **Font scale boundary 1.5**: Slider at maximum should not cause layout overflow
- **font_scale saved as invalid value (e.g., 0.0, 2.0)**: Should clamp to valid range [0.8, 1.5]
- **theme_mode saved as invalid string**: Should default to "light"
- **Rapid toggle of theme**: No flicker or double-update
- **Settings view while not authenticated**: Should redirect to login (public? No — settings is authenticated)

## Integration Points

- `settings_service.py` ↔ `State` (`theme_mode`, `font_scale`): must sync on login and on save
- `settings_view` ↔ `app.py` `on_route_change`: route `/about` now renders settings_view, not about_view
- `nav_bar.py` ↔ `_ROUTE_INDICES` and `_DESTINATIONS`: 4th index changes from INFO/Sobre to SETTINGS/Config, and route index for `/about` must match index 3
- `user_service.py` ↔ `settings_service.py`: theme/font fields must be loaded when user logs in
- DB migration: new columns must be nullable with defaults — existing users get "light" and 1.0

## Review Notes

_Nenhuma._ Todos os cenários das specs têm cobertura de teste correspondente.
