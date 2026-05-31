## Context

The login page (`app/views/login_view.py`) currently has a `toggle_mode` function that switches between login and registration modes on the same form. The `user_service.register` function exists and creates users in the database. However, the registration flow may have issues with error handling, UX feedback, or the toggle not working as expected. There is no dedicated `/register` route.

## Goals / Non-Goals

**Goals:**
- Make the "Criar conta" link on the login page reliably switch to registration mode
- Ensure registration validates input, shows errors, and logs in the user on success
- Add a dedicated `/register` route with its own view for direct access
- Ensure the `register` service function handles edge cases (empty fields, duplicate names, weak passwords)
- After registration, auto-login and redirect to `/feeds`

**Non-Goals:**
- Password hashing (stored in plaintext per current convention)
- Email verification or user profile management
- OAuth/social login

## Decisions

- **Separate register view**: Create `app/views/register_view.py` and a `/register` route instead of relying solely on the toggle. This gives a cleaner UX and allows direct linking to registration. The login view toggle will be updated to use `page.push_route("/register")` instead of inline toggling.
- **Keep login_view toggle working**: The existing toggle in `login_view.py` will be updated to navigate to `/register` rather than switching modes inline. This avoids duplicating the form logic.
- **Reuse user_service.register**: The existing `register` function is already correct — no changes needed to the service layer.
- **Auto-login**: After successful registration, set `state.user` and navigate to `/feeds`, same as login.

## Risks / Trade-offs

- [Risk] Duplicate form logic if both views maintain separate forms → Mitigation: extract shared form into a reusable control in `app/controls/`
- [Risk] The toggle button in login_view becomes a navigation link instead of inline toggle, changing existing UX → Mitigation: this is an improvement — users get a dedicated page
