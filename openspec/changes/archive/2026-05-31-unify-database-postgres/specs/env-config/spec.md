## MODIFIED Requirements

### Requirement: Documented environment variables

The project SHALL provide an `.env.sample` file in the repository root that documents every environment variable recognized by the application.

#### Scenario: `.env.sample` exists at project root

- **WHEN** a developer clones the repository
- **THEN** a file named `.env.sample` SHALL exist in the project root directory

#### Scenario: `.env.sample` lists all recognized variables

- **WHEN** a developer opens `.env.sample`
- **THEN** it SHALL list `COUSCOUS_DATABASE_NAME`, `COUSCOUS_DATABASE_HOST`, `COUSCOUS_DATABASE_PORT`, `COUSCOUS_DATABASE_USER`, and `COUSCOUS_DATABASE_PASS`
- **THEN** it SHALL NOT list `COUSCOUS_DATABASE_TYPE`
- **THEN** each variable SHALL have a comment describing its purpose

#### Scenario: `.env.sample` documents defaults

- **WHEN** a developer reads `.env.sample`
- **THEN** each variable SHALL indicate whether it has a default value and what that default is

#### Scenario: `.env.sample` is gitignored for creation

- **WHEN** a developer copies `.env.sample` to `.env`
- **THEN** the `.env` file SHALL NOT be tracked by git (per `.gitignore`)

## REMOVED Requirements

### Requirement: Optional SQLite fallback

**Reason**: PostgreSQL is now the only supported database backend. The `COUSCOUS_DATABASE_TYPE` env var with SQLite fallback is removed.

**Migration**: Remove `COUSCOUS_DATABASE_TYPE` from `.env` files. All five connection variables (`COUSCOUS_DATABASE_NAME`, `COUSCOUS_DATABASE_HOST`, `COUSCOUS_DATABASE_PORT`, `COUSCOUS_DATABASE_USER`, `COUSCOUS_DATABASE_PASS`) are now required. Run `docker compose up -d` to start a local PostgreSQL instance.
