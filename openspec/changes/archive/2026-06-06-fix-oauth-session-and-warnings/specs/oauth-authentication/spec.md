## ADDED Requirements

### Requirement: OAuth state stored in Flet session
The system SHALL store OAuth PKCE `code_verifier` and `provider` identifier in `page.session.store` when generating an authorization URL. The state MUST be retrievable by the callback handler even after the browser redirects back from the OAuth provider (i.e., across potential WebSocket reconnections).

#### Scenario: State survives provider redirect
- **WHEN** user clicks an OAuth button and the authorization URL is generated
- **THEN** the `code_verifier` and `provider` are stored in `page.session.store` under a key derived from the anti-CSRF `state` parameter, and the same values are available when the callback handler processes the redirect

#### Scenario: State cleaned after callback
- **WHEN** the OAuth callback handler successfully retrieves and uses the stored state
- **THEN** the state entry is removed from `page.session.store`

## MODIFIED Requirements

### Requirement: OAuth callback handling
The system SHALL handle the OAuth callback at `/oauth/callback` route, exchange the authorization code for tokens, verify the state parameter against the stored state in `page.session.store`, and fetch user information from the provider.

#### Scenario: Successful OAuth callback
- **WHEN** the OAuth provider redirects back to the app with a valid `code` and a `state` parameter that matches an entry in `page.session.store`
- **THEN** the system exchanges the code for tokens using the stored `code_verifier`, fetches the user's profile from the provider, finds or creates a user account, logs them in, and navigates to `/feeds`

#### Scenario: State mismatch in callback
- **WHEN** the OAuth callback contains a `state` parameter that does not match any stored state in `page.session.store`
- **THEN** the system shows an error message and redirects to `/login`

#### Scenario: OAuth callback with error from provider
- **WHEN** the OAuth callback contains an `error` parameter (e.g., user denied access)
- **THEN** the system shows an appropriate error message and redirects to `/login`
