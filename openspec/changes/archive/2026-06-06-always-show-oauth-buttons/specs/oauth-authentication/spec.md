## ADDED Requirements

### Requirement: OAuth button shared control
The system SHALL provide a shared function `get_oauth_buttons` in `app/controls/oauth_buttons.py` that returns a list of OAuth login buttons (Google and GitHub). This control MUST be reusable by login and registration views without code duplication.

#### Scenario: Google and GitHub buttons rendered
- **WHEN** `get_oauth_buttons(page, error_text)` is called
- **THEN** it returns a list containing a divider and both "Entrar com Google" and "Entrar com GitHub" buttons

#### Scenario: Button click when provider is configured
- **WHEN** user clicks an OAuth button and the provider is configured
- **THEN** the system opens the provider's authorization URL in the browser

#### Scenario: Button click when provider is not configured
- **WHEN** user clicks an OAuth button and the provider credentials are not set in environment variables
- **THEN** the system displays an error message indicating the provider is not configured, without navigating away

#### Scenario: Shared control used by login view
- **WHEN** the login view (`/login`) renders
- **THEN** it calls `get_oauth_buttons` from the shared control module and includes the returned buttons in the form

#### Scenario: Shared control used by registration view
- **WHEN** the registration view (`/register`) renders
- **THEN** it calls `get_oauth_buttons` from the shared control module and includes the returned buttons in the form

## MODIFIED Requirements

### Requirement: OAuth environment configuration
The system SHALL read OAuth provider credentials from environment variables. Each provider MUST have `client_id` and `client_secret` configured. A shared `redirect_uri` MUST be configurable.

#### Scenario: Missing OAuth configuration
- **WHEN** OAuth environment variables are not set for a provider
- **THEN** the OAuth button is still visible on the login and registration pages, and clicking it shows an error message indicating the provider is not configured

#### Scenario: Complete OAuth configuration
- **WHEN** `COUSCOUS_GOOGLE_CLIENT_ID` and `COUSCOUS_GOOGLE_CLIENT_SECRET` are set
- **THEN** the Google OAuth button is visible and functional
