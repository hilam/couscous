## ADDED Requirements

### Requirement: Tables are created at application startup
The system SHALL call `init_async_db()` during Flet app initialization, before any view is loaded or route is handled.

#### Scenario: Fresh database
- **WHEN** the application starts and no database tables exist
- **THEN** all tables defined by SQLModel models SHALL be created in the PostgreSQL database

#### Scenario: Existing tables
- **WHEN** the application starts and all required tables already exist
- **THEN** `init_async_db()` SHALL complete without error and no tables SHALL be modified

### Requirement: Startup fails on database error
The system SHALL fail fast if `init_async_db()` encounters a database connection or creation error.

#### Scenario: Unreachable database
- **WHEN** the application starts and PostgreSQL is not reachable
- **THEN** the application SHALL raise an exception and not serve any routes or views
