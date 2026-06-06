## Context

`_oauth_click()` in `app/controls/oauth_buttons.py` currently calls `ft.UrlLauncher().launch_url(uri)`. The Flet API has two URL launchers:

| API | Sync/Async | Notes |
|-----|-----------|-------|
| `ft.UrlLauncher().launch_url(url)` | async | Needs `await`, creates new instance |
| `page.launch_url(url)` | sync | Uses the page's built-in launcher |

The async version returns a coroutine that is never awaited, producing a `RuntimeWarning` and never opening the URL.

## Goals / Non-Goals

**Goals:**
- Make the OAuth button click actually open the authorization URL in the browser

**Non-Goals:**
- No changes to the OAuth flow, session handling, or any other file
- No refactoring of `_oauth_click` to be async (unnecessary when `page.launch_url` exists)

## Decisions

**Decision: Use `page.launch_url(uri)` instead of `ft.UrlLauncher().launch_url(uri)`**

`page` is already passed to `_oauth_click()`, and `page.launch_url()` is synchronous with the same effect. This is a one-line fix that requires no structural changes.

**Alternative considered: Make `_oauth_click` async and `await` the call**

This would work but introduces unnecessary complexity — `page.launch_url()` exists precisely for this use case.
