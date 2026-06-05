## MODIFIED Requirements

### Requirement: Login
The system SHALL allow a registered user to log in via password or OAuth provider. For password login, the password SHALL be verified against the stored bcrypt hash. For OAuth login, the system SHALL authenticate the user based on `oauth_provider` and `oauth_id` match.

#### Scenario: Successful password login
- **WHEN** user enters a valid name and matching password
- **THEN** the system verifies the password against the stored bcrypt hash and logs the user in, navigating to `/feeds`

#### Scenario: Wrong password
- **WHEN** user enters a valid name but incorrect password
- **THEN** the system shows an error message "Senha incorreta"

#### Scenario: Unknown user
- **WHEN** user enters a name that does not exist
- **THEN** the system shows an error message "Usuário não encontrado"

#### Scenario: Successful OAuth login
- **WHEN** user completes OAuth flow with a previously linked provider and id
- **THEN** the system logs the user in without requiring password, navigating to `/feeds`
