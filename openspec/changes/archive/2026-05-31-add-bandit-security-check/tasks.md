## 1. Add bandit dependency

- [x] 1.1 Add `bandit` to `[dependency-groups] dev` in `pyproject.toml`

## 2. Configure bandit

- [x] 2.1 Add `[tool.bandit]` section to `pyproject.toml` with exclusions for `tests/` and `.venv/`

## 3. Add run script

- [x] 3.1 Create a `lint:security` script entry in `pyproject.toml` that runs `bandit -r app/ -r database/`
- [x] 3.2 Verify the script works with `uv run lint:security`

## 4. Integrate into CI

- [x] 4.1 Create Makefile with a `lint-security` target (`make lint-security`)

## 5. Document

- [x] 5.1 Update `AGENTS.md` to include `uv run lint:security` in the quick start / linting section
