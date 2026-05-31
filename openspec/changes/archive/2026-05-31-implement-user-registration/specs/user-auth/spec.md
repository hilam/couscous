## MODIFIED Requirements

### Requirement: Register new user
The system SHALL allow a new user to create an account with name and password. The registration form SHALL be available at `/register` route or via toggle on the login page.

#### Scenario: Successful registration
- **WHEN** user enters a unique name and a password and submits the registration form
- **THEN** the system creates the user, logs them in automatically, and navigates to `/feeds`

#### Scenario: Duplicate username
- **WHEN** user enters a name that already exists in the database
- **THEN** the system shows an error message "Nome de usuário já existe"

#### Scenario: Navigate to registration
- **WHEN** user clicks "Criar conta" on the login page
- **THEN** the system navigates to `/register`
