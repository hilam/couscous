## MODIFIED Requirements

### Requirement: Register new user
The system SHALL allow a new user to create an account with name and password. The password SHALL be hashed with bcrypt before storage. The registration form SHALL be available at `/register` route or via toggle on the login page.

#### Scenario: Successful registration
- **WHEN** user enters a unique name and a password and submits the registration form
- **THEN** the system hashes the password with bcrypt, creates the user, logs them in automatically, and navigates to `/feeds`

#### Scenario: Duplicate username
- **WHEN** user enters a name that already exists in the database
- **THEN** the system shows an error message "Nome de usuário já existe"

#### Scenario: Navigate to registration
- **WHEN** user clicks "Criar conta" on the login page
- **THEN** the system navigates to `/register`

### Requirement: Login
The system SHALL allow a registered user to log in. The password SHALL be verified against the stored bcrypt hash.

#### Scenario: Successful login
- **WHEN** user enters a valid name and matching password
- **THEN** the system verifies the password against the stored bcrypt hash and logs the user in, navigating to the home page

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
