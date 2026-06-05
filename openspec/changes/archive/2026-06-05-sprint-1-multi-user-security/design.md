## Context

CousCous currently uses a single implicit user — there is no `user_id` foreign key on `Feed` or `Entry`. Passwords are stored in plaintext. All feed and entry operations assume a single-user context. The app needs to support multi-user as a foundation for OAuth, categories, tags, and other downstream features.

## Goals / Non-Goals

**Goals:**
- Hash all existing and new passwords with bcrypt
- Add `user_id` FK (non-nullable) to `Feed` and `Entry` models
- Scope all feed/entry/refresh service operations to a `user_id` parameter
- Fix star (important) toggle visual feedback in `entry_view.py`
- Add "unread" and "important" entry list filters
- Update tests to cover user-scoped operations

**Non-Goals:**
- OAuth integration (Sprint 2)
- Categories and tags (Sprints 3–4)
- Full-text search (Sprint 5)
- Theme/settings (Sprint 6)

## Decisions

1. **bcrypt over argon2**: bcrypt is simpler to set up, well-supported in Python via `bcrypt` package, and sufficient for this use case. argon2 would be more future-proof but adds complexity (different parameters, no stdlib binding). Decision: bcrypt.

2. **Non-nullable `user_id` FK**: The FK must be non-nullable to maintain data integrity. Existing single-user data will be assigned to user_id=1 (the first user) during migration. Downstream: all service functions accept `user_id` as a required parameter.

3. **Drop and recreate tables vs migration**: Since the app is in early development with no production data, the simplest approach is to drop and recreate tables on startup. The `init_async_db()` function already does this for schema changes. No formal migration script is needed.

4. **Entry filtering at the service layer**: Filtering by "unread" and "important" happens in `entry_service.py` via optional query parameters, not in views. This keeps views thin and filters testable.

5. **Star toggle fix**: The existing star button in `entry_view.py` uses `ft.IconButton` with a `selected_icon` property that sometimes desyncs. Fix: use a controlled `on_click` handler that explicitly sets the icon and calls the update service.

## Risks / Trade-offs

- **[Data loss on recreate]** Dropping tables on every startup destroys data. Mitigation: only do this during development. In production (future), switch to proper Alembic migrations.
- **[bcrypt speed]** bcrypt is intentionally slow (50-200ms per hash). For login/register this is fine, but batch operations should never hash repeatedly. Mitigation: only hash on create and password change.
- **[Single-user -> multi-user breakage]** Views and controls that don't pass `user_id` will fail at runtime. Mitigation: add `user_id` to `app/state.py` State class and make all service calls source it from there.
