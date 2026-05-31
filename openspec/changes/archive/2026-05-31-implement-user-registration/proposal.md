## Why

The login page has a "Criar conta" link that should allow new users to register, but the registration flow is not working properly. Without user registration, new users cannot create accounts, making the app unusable for onboarding.

## What Changes

- Fix the registration toggle on the login page so "Criar conta" correctly switches to registration mode
- Ensure the registration form validates input and shows proper error/success feedback
- After successful registration, log the user in automatically and redirect to `/feeds`
- Optionally add a dedicated `/register` route for direct access to registration
- Add a "Já tenho conta" (I already have an account) link in registration mode to toggle back to login
- Ensure the user_service `register` function handles all edge cases and returns properly

## Capabilities

### New Capabilities
- `user-registration`: User registration flow with form validation, error handling, and automatic login after successful signup

### Modified Capabilities
- `user-auth`: Updated requirements for registration flow — the existing spec already covers basic registration but needs detail on the toggle UI behavior and dedicated route

## Impact

- `app/views/login_view.py` — fix/enhance registration toggle logic
- `app/views/register_view.py` — new file for dedicated registration page (optional)
- `app/app.py` — add `/register` route if creating a separate view
- `app/services/user_service.py` — review and ensure `register` function is robust
- `openspec/specs/user-registration/spec.md` — new spec for registration capability
