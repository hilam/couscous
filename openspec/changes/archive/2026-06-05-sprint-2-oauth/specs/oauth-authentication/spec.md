## ADDED Requirements

### Requirement: OAuth login flow initiation
The system SHALL provide buttons on the login and registration pages to initiate OAuth 2.0 login with Google and GitHub. Each button MUST redirect the user to the provider's authorization endpoint with PKCE code challenge and anti-CSRF state parameter.

#### Scenario: Google login button on login page
- **WHEN** user is on the login page (`/login`)
- **THEN** a "Entrar com Google" button is visible and clicking it opens the Google OAuth authorization URL in the browser

#### Scenario: GitHub login button on login page
- **WHEN** user is on the login page (`/login`)
- **THEN** a "Entrar com GitHub" button is visible and clicking it opens the GitHub OAuth authorization URL in the browser

#### Scenario: OAuth buttons on registration page
- **WHEN** user is on the registration page (`/register`)
- **THEN** both Google and GitHub OAuth buttons are visible

### Requirement: OAuth callback handling
The system SHALL handle the OAuth callback at `/oauth/callback` route, exchange the authorization code for tokens, verify the state parameter, and fetch user information from the provider.

#### Scenario: Successful OAuth callback
- **WHEN** the OAuth provider redirects back to the app with a valid `code` and matching `state` parameter
- **THEN** the system exchanges the code for tokens, fetches the user's profile from the provider, finds or creates a user account, logs them in, and navigates to `/feeds`

#### Scenario: State mismatch in callback
- **WHEN** the OAuth callback contains a `state` parameter that does not match the stored state
- **THEN** the system shows an error message and redirects to `/login`

#### Scenario: OAuth callback with error from provider
- **WHEN** the OAuth callback contains an `error` parameter (e.g., user denied access)
- **THEN** the system shows an appropriate error message and redirects to `/login`

### Requirement: Automatic user creation on first OAuth login
The system SHALL automatically create a user account when a person authenticates via OAuth for the first time. The new user MUST have `oauth_provider` and `oauth_id` populated.

#### Scenario: First Google OAuth login
- **WHEN** a user authenticates via Google OAuth and no account exists with the same `oauth_provider=google` and `oauth_id`
- **THEN** the system creates a new `User` record with `oauth_provider="google"`, the Google `sub` as `oauth_id`, the Google `name` as `name`, and a null/empty `password`

#### Scenario: First GitHub OAuth login
- **WHEN** a user authenticates via GitHub OAuth and no account exists with the same `oauth_provider=github` and `oauth_id`
- **THEN** the system creates a new `User` record with `oauth_provider="github"`, the GitHub user `id` as `oauth_id`, the GitHub `login` as `name`, and a null/empty `password`

#### Scenario: Username collision with existing non-OAuth user
- **WHEN** OAuth userinfo `name` matches an existing non-OAuth user's `name`
- **THEN** the system creates the account using a prefixed name (e.g., `gh_<name>` or `google_<name>`) to avoid uniqueness violation

### Requirement: Returning OAuth user login
The system SHALL log in an existing user when they authenticate via OAuth with a previously registered provider and id.

#### Scenario: Returning Google user
- **WHEN** a user authenticates via Google OAuth and an account exists with `oauth_provider=google` and matching `oauth_id`
- **THEN** the system logs the user in without creating a new account and navigates to `/feeds`

#### Scenario: Returning GitHub user
- **WHEN** a user authenticates via GitHub OAuth and an account exists with `oauth_provider=github` and matching `oauth_id`
- **THEN** the system logs the user in without creating a new account and navigates to `/feeds`

### Requirement: OAuth environment configuration
The system SHALL read OAuth provider credentials from environment variables. Each provider MUST have `client_id` and `client_secret` configured. A shared `redirect_uri` MUST be configurable.

#### Scenario: Missing OAuth configuration
- **WHEN** OAuth environment variables are not set for a provider
- **THEN** the corresponding OAuth button is hidden on the login and registration pages

#### Scenario: Complete OAuth configuration
- **WHEN** `COUSCOUS_GOOGLE_CLIENT_ID` and `COUSCOUS_GOOGLE_CLIENT_SECRET` are set
- **THEN** the Google OAuth button is visible and functional

### Requirement: OAuth provider columns in User model
The `User` model SHALL include nullable columns `oauth_provider` (string) and `oauth_id` (string) to store OAuth provider information. These columns MUST be `None` for password-authenticated users and MUST be populated for OAuth-created users.

#### Scenario: Password user has null OAuth fields
- **WHEN** a user is created via the registration form with name and password
- **THEN** the `oauth_provider` and `oauth_id` columns are `NULL`

#### Scenario: OAuth user has populated provider fields
- **WHEN** a user is created via OAuth login
- **THEN** the `oauth_provider` column is set to the provider name and `oauth_id` is set to the provider's unique user identifier
