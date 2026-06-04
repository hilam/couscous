## ADDED Requirements

### Requirement: Enter submits login form

The login form SHALL submit when the user presses Enter while focused on the password field.

#### Scenario: Enter on password field submits login
- **WHEN** user fills name and password fields
- **AND** presses Enter while focused on the password field
- **THEN** the login form SHALL be submitted
- **AND** the `submit` function SHALL be called

#### Scenario: Enter on name field moves focus to password
- **WHEN** user fills the name field
- **AND** presses Enter while focused on the name field
- **THEN** focus SHALL move to the password field

### Requirement: Enter submits register form

The register form SHALL submit when the user presses Enter while focused on the password field.

#### Scenario: Enter on password field submits registration
- **WHEN** user fills name and password fields
- **AND** presses Enter while focused on the password field
- **THEN** the registration form SHALL be submitted
- **AND** the `submit` function SHALL be called

#### Scenario: Enter on name field moves focus to password
- **WHEN** user fills the name field
- **AND** presses Enter while focused on the name field
- **THEN** focus SHALL move to the password field
