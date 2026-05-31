## Context

The project reads database configuration from environment variables (`COUSCOUS_DATABASE_*`) via `database/service/config.py`. Both the config module and `tests/conftest.py` call `load_dotenv()` to load a `.env` file if present. However, there is no documented list of accepted variables — new contributors must read source code to learn what to configure.

## Goals / Non-Goals

**Goals:**
- Provide a `.env.sample` file documenting all recognized environment variables
- Include descriptions, defaults, and example values for each variable
- Use comments so the file is self-documenting (uncomment-and-edit pattern)

**Non-Goals:**
- No changes to application code (no new env vars, no new behavior)
- No `.env` file creation or management tooling
- No secrets or actual credentials in the sample file

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| File format | `# comment` lines with `KEY=value` | Matches the `python-dotenv` library already used by the project |
| Variable scope | Only `COUSCOUS_DATABASE_*` vars | These are the only env vars actually read by the current codebase in `database/service/config.py` |
| Default values | Documented inline as comments | Avoids duplication of defaults that exist in code; the sample shows `# Default: sqlite` next to the unset line |

## Risks / Trade-offs

- [Stale sample] If new env vars are added later, `.env.sample` may become outdated → rely on PR review discipline to update it alongside code changes
- [No validation] The sample file is documentation only; no runtime check ensures `.env` keys match `.env.sample` → acceptable for a small project
