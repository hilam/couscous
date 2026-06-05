## 1. Foundation — Dependencies & Data Model

- [x] 1.1 Add `bcrypt` dependency to `pyproject.toml`
- [x] 1.2 Implement password hashing with bcrypt in `user_service.py` (hash on register, verify on login)
- [x] 1.3 Add `user_id` (FK → `user.id`) non-nullable column to `Feed` model
- [x] 1.4 Add `user_id` (FK → `user.id`) non-nullable column to `Entry` model
- [x] 1.5 Update `init_async_db()` to recreate tables with new schema (drop & recreate)

## 2. Service Layer — User Scoping

- [x] 2.1 Add `user_id` parameter to `feed_service.py` functions (`add_feed`, `get_feeds`, `remove_feed`)
- [x] 2.2 Add `user_id` parameter to `entry_service.py` functions (`get_entries`, `get_entry`, `toggle_important`, `toggle_read`)
- [x] 2.3 Add `user_id` parameter to `refresh_service.py` (`refresh_all_feeds`)
- [x] 2.4 Add `user_id` to `app/state.py` State class and wire it into service calls
- [x] 2.5 Add `get_entries` filter parameters: `unread_only` and `important_only` in `entry_service.py`
- [x] 2.6 Add `get_unread_count` function to `entry_service.py` (scoped by user_id)

## 3. UI Layer — Fixes & Filters

- [x] 3.1 Fix star (important) toggle in `entry_view.py` — use controlled `on_click` handler with explicit icon state
- [x] 3.2 Add "Não lidos" filter toggle to `entry_list_view.py`
- [x] 3.3 Add "Importantes" filter toggle to `entry_list_view.py`
- [x] 3.4 Wire filter toggles to `entry_service.get_entries` with filter parameters

## 4. Testing

- [x] 4.1 Update existing feed service tests to pass `user_id` and test per-user scoping
- [x] 4.2 Update existing entry service tests to pass `user_id` and test per-user scoping
- [x] 4.3 Update existing refresh service tests to pass `user_id`
- [x] 4.4 Write tests for bcrypt password hashing (hash + verify + wrong password)
- [x] 4.5 Write tests for entry filters (unread_only, important_only)
