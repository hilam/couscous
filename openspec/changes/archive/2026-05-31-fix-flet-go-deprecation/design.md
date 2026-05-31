## Context

The app uses `page.go(route)` for all navigation — initial load, login redirect, feed/article clicks, and bottom navigation bar. Flet 0.80.0 deprecated `go()` in favor of `push_route()`. The `on_route_change` handler in `app.py` manages the view stack manually (`page.views.clear() + append`), so the only change needed is the method call itself.

## Goals / Non-Goals

**Goals:**
- Replace every `page.go(...)` call with `page.push_route(...)`
- Eliminate all deprecation warnings at runtime
- Keep routing behavior identical

**Non-Goals:**
- No routing logic changes, no new navigation patterns
- No view stack behavior changes (views are already fully managed in `on_route_change`)
- No spec changes — this is purely an internal API migration

## Decisions

- **`push_route` over `go`**: `go()` is deprecated. `push_route()` is the direct replacement. Both trigger `on_route_change` identically. Since the handler does `page.views.clear()` on every route change, the view stack is always reset to a single view regardless of whether `go` or `push_route` was used.
- **No `go` → `navigate` migration**: Flet also offers `page.navigate()` for named routes, but `push_route()` is the closest 1:1 replacement for the current URL-based routing pattern.

## Risks / Trade-offs

- [Back navigation] `push_route()` adds to history, so browser back button would push previous routes back through `on_route_change`. This is benign — the handler always renders the correct view for the incoming route.
