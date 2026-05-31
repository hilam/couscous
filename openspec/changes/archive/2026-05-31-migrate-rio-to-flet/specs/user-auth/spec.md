## ADDED Requirements

### Requirement: Register new user
The system SHALL allow a new user to create an account with name and password.

#### Scenario: Successful registration
- **WHEN** user enters a unique name and a password and submits the registration form
- **THEN** the system creates the user and logs them in automatically

#### Scenario: Duplicate username
- **WHEN** user enters a name that already exists in the database
- **THEN** the system shows an error message "Nome de usuário já existe"

### Requirement: Login
The system SHALL allow a registered user to log in.

#### Scenario: Successful login
- **WHEN** user enters a valid name and matching password
- **THEN** the system logs the user in and navigates to the home page

#### Scenario: Wrong password
- **WHEN** user enters a valid name but incorrect password
- **THEN** the system shows an error message "Senha incorreta"

#### Scenario: Unknown user
- **WHEN** user enters a name that does not exist
- **THEN** the system shows an error message "Usuário não encontrado"

### Requirement: Persistent session
The system SHALL remember the logged-in user while the app is running.

#### Scenario: Session persists across navigation
- **WHEN** user is logged in and navigates between pages
- **THEN** the system keeps the user logged in across all pages
