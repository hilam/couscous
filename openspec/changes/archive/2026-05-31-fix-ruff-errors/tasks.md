## 1. Simple Fixes — PLR, PLW, N, TC, E, ERA

- [x] 1.1 Merge `or` comparisons into set membership in `app/app.py` (PLR1714)
- [x] 1.2 Extract magic value `120` as `SUMMARY_MAX_LENGTH` constant in `app/controls/article_card.py` (PLR2004)
- [x] 1.3 Replace unnecessary lambdas with direct method refs in `app/controls/feed_card.py` (PLW0108)
- [x] 1.4 Rename `Session` → `sync_session` in `app/db.py` (N806)
- [x] 1.5 Wrap `User` import in `TYPE_CHECKING` guard in `app/state.py` (TC001)
- [x] 1.6 Split long string line in `app/views/about_view.py` (E501)
- [x] 1.7 Remove commented-out `drop_all` lines in `database/service/database.py` (ERA001)

## 2. Exception Messages — TRY003 / EM101

- [x] 2.1 Fix `ValueError("Feed já cadastrado")` → variable pattern in `app/services/feed_service.py`
- [x] 2.2 Fix `ValueError("Nome de usuário já existe")`, `ValueError("Usuário não encontrado")`, `ValueError("Senha incorreta")` → variable pattern in `app/services/user_service.py`

## 3. Datetime Timezone — DTZ005 / DTZ006

- [x] 3.1 Add `import datetime as _dt` import (also covers UP017)
- [x] 3.2 Replace `datetime.now()` → `_dt.datetime.now(tz=_dt.UTC)` in `app/services/refresh_service.py` (4 occurrences)
- [x] 3.3 Replace `datetime.fromtimestamp(...)` → `_dt.datetime.fromtimestamp(..., tz=_dt.UTC)` in `app/services/refresh_service.py`
- [x] 3.4 Replace `datetime.now()` default in `database/models/couscous.py:31` — use `_dt.datetime.now(tz=_dt.UTC)`

## 4. Boolean Positional Args — FBT001 / FBT002

- [x] 4.1 Make `read: bool` keyword-only in `mark_read` (`app/services/entry_service.py`)
- [x] 4.2 Make `important: bool` keyword-only in `mark_important` (`app/services/entry_service.py`)
- [x] 4.3 Update caller of `mark_important` to use keyword argument syntax in `app/views/entry_view.py`

## 5. Function Complexity — C901

- [x] 5.1 Extract feed-card creation into `_build_feed_card` and feed-list rebuilding into `_rebuild_feed_list` helpers in `app/views/feed_list_view.py` to reduce McCabe complexity from 12 to ≤10

## 6. Verify

- [x] 6.1 Run `ruff check .` to confirm zero errors
- [x] 6.2 Run `PYTHONPATH=. uv run pytest` to confirm no test regressions
