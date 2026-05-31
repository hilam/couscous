## ADDED Requirements

### Requirement: Bandit dev dependency
The project SHALL include `bandit` as a dev dependency in `pyproject.toml`.

#### Scenario: Bandit is installable
- **WHEN** a developer runs `uv sync`
- **THEN** `bandit` SHALL be available in the virtual environment

### Requirement: Bandit configuration
The project SHALL configure bandit via `[tool.bandit]` in `pyproject.toml`, excluding `tests/` and `.venv/` directories.

#### Scenario: Bandit skips tests directory
- **WHEN** a developer runs `uv run bandit -r app/`
- **THEN** bandit SHALL scan `app/` and `database/` but skip `tests/` and `.venv/`

### Requirement: lint:security script
The project SHALL provide a `lint:security` script in `pyproject.toml` that runs bandit on the application code.

#### Scenario: Running lint:security via uv
- **WHEN** a developer runs `uv run lint:security`
- **THEN** bandit SHALL be invoked with the configured options against `app/` and `database/`
- **AND** the process SHALL exit with non-zero if any issue with confidence >= MEDIUM is found

### Requirement: CI integration
The CI pipeline SHALL run `lint:security` as a step alongside existing lint checks.

#### Scenario: CI includes security lint step
- **WHEN** CI runs the lint workflow
- **THEN** `uv run lint:security` SHALL be executed as a step
- **AND** a failure SHALL block the pipeline

### Requirement: Documentation
The project SHALL document how to run security checks.

#### Scenario: Developer reads check instructions
- **WHEN** a developer reads the project documentation or AGENTS.md
- **THEN** they SHALL find instructions for running `uv run lint:security`
