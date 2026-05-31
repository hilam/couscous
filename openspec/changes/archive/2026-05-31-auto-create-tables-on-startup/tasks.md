## 1. App Startup

- [x] 1.1 Import `init_async_db` in `app/app.py`
- [x] 1.2 Call `await init_async_db()` at the top of `app_run()`, before the route handler setup

## 2. Documentation

- [x] 2.1 Remove the manual `init_async_db` one-liner from AGENTS.md quick-start section
- [x] 2.2 Verify the app starts cleanly (fresh database) and existing tables are left untouched
