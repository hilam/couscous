## Why

The project uses environment variables for database configuration, but there is no `.env.sample` file documenting what variables are available. New contributors must read source code to discover configuration. A `.env.sample` makes setup obvious and prevents `.env`-related bugs.

## What Changes

- Add `.env.sample` to the project root listing all recognized environment variables with descriptions and examples
- Expose all `COUSCOUS_DATABASE_*` vars currently used by `database/service/config.py`
- Include documentation about how `.env` is auto-loaded by services and tests

## Capabilities

### New Capabilities
- `env-config`: Document the set of configuration environment variables the application reads, their defaults, and example values

### Modified Capabilities

<!-- No existing capabilities change -->

## Impact

- New file: `.env.sample` (project root)
- No runtime code changes
- No breaking changes
