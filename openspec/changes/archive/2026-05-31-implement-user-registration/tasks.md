## 1. New Registration View

- [x] 1.1 Create `app/views/register_view.py` with a registration form (name + password fields, submit button, "Já tenho conta" link)
- [x] 1.2 Wire up form submission to call `user_service.register`, handle errors, and auto-login on success
- [x] 1.3 Add "Já tenho conta" link that navigates to `/login`

## 2. Route Registration

- [x] 2.1 Add `/register` route in `app/app.py` routing table pointing to `register_view`
- [x] 2.2 Import `register_view` in `app/app.py`

## 3. Update Login View

- [x] 3.1 Change the "Criar conta" toggle in `login_view.py` from inline mode-switching to `page.push_route("/register")`
- [x] 3.2 Remove unused registration form logic from `login_view.py`

## 4. Tests

- [x] 4.1 Write tests for registration flow (service-level: registration + auto-login, duplicate username)
- [x] 4.2 Verify navigation: login_view navigates to /register, register_view links back to /login
