## ADDED Requirements

### Requirement: Dedicated registration page
The system SHALL provide a dedicated `/register` route with a registration form.

#### Scenario: Navigate to registration page
- **WHEN** user clicks "Criar conta" link on the login page
- **THEN** the system navigates to `/register` showing the registration form

#### Scenario: Direct access to registration
- **WHEN** user navigates to `/register` URL directly
- **THEN** the system shows the registration form

### Requirement: Registration form validation
The system SHALL validate registration form input before submitting.

#### Scenario: Empty fields blocked
- **WHEN** user submits registration with empty name or password
- **THEN** the system shows error "Preencha todos os campos"

#### Scenario: Duplicate username rejected
- **WHEN** user submits registration with an existing username
- **THEN** the system shows error "Nome de usuário já existe"

### Requirement: Successful registration auto-login
The system SHALL log the user in automatically after successful registration.

#### Scenario: Register and redirect
- **WHEN** user submits valid registration data
- **THEN** the system creates the account, logs the user in, and redirects to `/feeds`

### Requirement: Toggle back to login
The registration page SHALL provide a link back to the login page.

#### Scenario: Navigate to login
- **WHEN** user clicks "Já tenho conta" link on the registration page
- **THEN** the system navigates to `/login`
