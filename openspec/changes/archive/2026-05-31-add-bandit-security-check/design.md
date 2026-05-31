## Context

The project uses `ruff` for linting and formatting but has no dedicated security scanning. While `ruff` catches some security issues (e.g., `S` rules), `bandit` provides deeper AST-based security analysis specifically targeting common vulnerability patterns in Python. The project already follows a `ruff format .` / `ruff check .` workflow; bandit will complement this.

## Goals / Non-Goals

**Goals:**
- Add `bandit` as a dev dependency
- Configure bandit via `pyproject.toml`
- Add a `ruff`-style `lint:security` script runnable via `uv run`
- Integrate into CI alongside existing lint steps
- Document the security check workflow

**Non-Goals:**
- Fixing existing security issues found by bandit (separate follow-up)
- Adding pre-commit hooks (out of scope for this change)
- Dependency vulnerability scanning (use `pip-audit` or `safety` separately)

## Decisions

- **Bandit over ruff's S rules**: `bandit` has richer security-specific checks and wider community adoption for security auditing. `ruff`'s S plugin covers a subset; bandit is the standard Python security linter.
- **`pyproject.toml` config**: Bandit supports `pyproject.toml` via `[tool.bandit]`. Keeps configuration co-located with other tool configs instead of a separate `.bandit` file.
- **`lint:security` script**: Follows existing pattern in `pyproject.toml` scripts (e.g., existing ruff commands). Consistent with project conventions.
- **Exclude `tests/` and `.venv/`**: Tests often intentionally use patterns bandit flags. `.venv/` is third-party code. In line with how `ruff check .` is configured.

## Risks / Trade-offs

- **False positives**: Bandit may flag intentional code (e.g., `assert` in tests). Mitigation: configure skips in `pyproject.toml` and use `# nosec` comments for inline overrides.
- **Slower CI**: Adding a new lint step increases CI time (~5-10s). Mitigation: bandit is fast on moderate codebases; acceptable trade-off.
