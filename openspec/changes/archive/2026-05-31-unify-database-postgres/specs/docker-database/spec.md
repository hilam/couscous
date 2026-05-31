## ADDED Requirements

### Requirement: Docker Compose for PostgreSQL

The project SHALL provide a `docker-compose.yml` file at the project root that defines a `db` service running PostgreSQL 16 Alpine for local development.

#### Scenario: docker-compose.yml exists at project root
- **WHEN** a developer clones the repository
- **THEN** a file named `docker-compose.yml` SHALL exist in the project root directory

#### Scenario: db service uses postgres:16-alpine image
- **WHEN** a developer runs `docker compose config`
- **THEN** the `db` service SHALL use the image `postgres:16-alpine`

#### Scenario: Default credentials are configured
- **WHEN** a developer inspects `docker-compose.yml`
- **THEN** the `db` service SHALL set `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` environment variables with sensible defaults

#### Scenario: Port 5432 is exposed
- **WHEN** a developer inspects `docker-compose.yml`
- **THEN** the `db` service SHALL map container port 5432 to host port 5432

#### Scenario: Database data persists across restarts
- **WHEN** the container is stopped and restarted
- **THEN** the database data SHALL persist via a named volume or bind mount

### Requirement: Quick-start documents Docker prerequisite

The project SHALL document in `AGENTS.md` that `docker compose up -d` must be run before starting the application.

#### Scenario: Developer reads AGENTS.md
- **WHEN** a developer reads the quick-start section of `AGENTS.md`
- **THEN** they SHALL find instructions to run `docker compose up -d` before starting the app
