## Why

The project has no automated security checks. Adding `bandit` as a security linter will catch common vulnerabilities (SQL injection, hardcoded passwords, unsafe deserialization, etc.) in Python code and dependencies during development and CI.

## What Changes

- Add `bandit` to dev dependencies
- Create a `pyproject.toml` config section for bandit
- Add a `lint:security` script to run bandit (skipping tests/)
- Integrate into the existing lint/CI workflow
- Document how to run security checks in contributing guidelines

## Capabilities

### New Capabilities
- `security-linting`: Automated bandit security scanning for Python code, with config, run scripts, and CI integration.

### Modified Capabilities
<!-- No existing capabilities have requirement changes for this addition -->

## Impact

- `pyproject.toml`: new dev dependency and bandit config section
- `Makefile` / `pyproject.toml` scripts: new `lint:security` entry
- CI config: new security check step
- Development workflow: security linting now part of the pre-commit or CI pipeline
