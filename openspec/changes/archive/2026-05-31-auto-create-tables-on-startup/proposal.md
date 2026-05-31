## Why

Currently, users must manually run a Python one-liner to create database tables before the app will work. This is a friction point for new developers and a potential source of runtime errors. The app should create tables automatically on startup if they don't already exist.

## What Changes

- Call `init_async_db()` at application startup, before the Flet app begins serving views
- This eliminates the manual setup step for developers and ensures the database schema is always present at runtime
- No changes to the table creation logic itself — only where/when it is invoked

## Capabilities

### New Capabilities
- `auto-db-init`: Run database schema migrations (table creation) automatically when the application starts

### Modified Capabilities

- None

## Impact

- `main.py` or `app/app.py`: Add the call to `init_async_db()` during startup
- `database/service/database.py`: No changes needed — `init_async_db()` already exists and works correctly
- No new dependencies
- No breaking changes to existing functionality
