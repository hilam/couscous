## Why

CousCous currently operates as a single-user application with no password hashing and no user scoping for feeds and entries. To support multiple users (required for OAuth, categories, and all downstream features), the data model and services must be updated with proper user ownership, secure password storage, and basic filtering capabilities.

## What Changes

- Hash passwords with bcrypt in `user_service.py`
- Add `user_id` foreign key to `Feed` and `Entry` models
- Recreate or migrate database tables to include new FK columns
- Scope all feed/entry/refresh operations to the current user
- Fix star (important) toggle visual feedback in `entry_view.py`
- Add "unread" and "important" filters to the entry list view
- Update existing tests for the new user FK constraints

## Capabilities

### New Capabilities
- `entry-filters`: Filter entry list by read status ("não lidos") and importance ("importantes")

### Modified Capabilities
- `user-auth`: Password storage SHALL use bcrypt hashing instead of plaintext. Registration and login scenarios must hash/verify passwords.
- `feed-management`: Feeds SHALL be scoped to `user_id`. Add feed, list feeds, and remove feed operations must filter by the authenticated user.
- `feed-viewing`: Entries SHALL be scoped to `user_id`. Entry list and article views must filter by the authenticated user's feeds.
- `feed-refresh`: Refresh operations SHALL create entries scoped to the feed's owning `user_id`.

## Impact

- **Models**: `Feed` and `Entry` gain a non-nullable `user_id` FK column; `User` model unchanged
- **Services**: `feed_service.py`, `entry_service.py`, `refresh_service.py` gain `user_id` parameter; `user_service.py` gains bcrypt hashing
- **Views**: `entry_view.py` star toggle fix; `entry_list_view.py` gains filter controls
- **Dependencies**: Add `bcrypt` to `pyproject.toml`
- **Database**: Schema migration required (new columns + FK constraints)
- **Tests**: All service tests updated for user FK; new tests for bcrypt and filters
