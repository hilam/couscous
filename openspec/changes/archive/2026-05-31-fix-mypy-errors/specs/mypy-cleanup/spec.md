## ADDED Requirements

### Requirement: Zero mypy errors after fixes
Running `mypy .` MUST report zero errors. All existing mypy settings in `pyproject.toml` SHALL remain unchanged.

#### Scenario: All files pass mypy
- **WHEN** `uv run mypy .` is executed
- **THEN** the exit code MUST be 0 and output MUST contain no error lines

### Requirement: Flet icon constants are type-resolvable
All `ft.icons.*` references in `app/controls/` and `app/views/` MUST resolve correctly or use appropriate `# type: ignore[attr-defined]` annotations so mypy passes without errors.

#### Scenario: No icon attr-defined errors
- **WHEN** `uv run mypy .` is run
- **THEN** there MUST be no `[attr-defined]` errors for any `ft.icons.*` attribute

### Requirement: Flet padding/alignment references are type-resolvable
All `ft.padding.all()`, `ft.alignment.center`, and similar utility references SHALL resolve correctly.

#### Scenario: No padding/alignment attr-defined errors
- **WHEN** `uv run mypy .` is run
- **THEN** there MUST be no `[attr-defined]` errors for `ft.padding.*` or `ft.alignment.*`

### Requirement: Text style arguments use correct type
All `ft.Text(style=...)` calls SHALL pass a `TextStyle` object or the correct type expected by the Flet API.

#### Scenario: No TextStyle type errors
- **WHEN** `uv run mypy .` is run
- **THEN** there MUST be no incompatible type errors for `style` argument in `ft.Text()` calls

### Requirement: Page API calls match Flet stubs
All `page.show_snack_bar`, `page.dialog`, and `page.session.set` calls SHALL use the correct API as defined by Flet's type stubs.

#### Scenario: No Page attr-defined errors
- **WHEN** `uv run mypy .` is run
- **THEN** there MUST be no `[attr-defined]` errors for `page.*` attributes

### Requirement: Dialog controls have update_async
All `ConfirmDialog` and `AddFeedDialog` instances SHALL have access to `update_async`.

#### Scenario: No update_async attr-defined errors
- **WHEN** `uv run mypy .` is run
- **THEN** there MUST be no `[attr-defined]` errors for `self.update_async()` in dialog controls

### Requirement: Database engine type narrowing
The `AsyncEngine | Engine` union in `app/db.py` and `database/service/database.py` SHALL be properly narrowed so `sessionmaker`, `engine.begin()`, and related calls type-check.

#### Scenario: No union-attr errors on engine
- **WHEN** `uv run mypy .` is run
- **THEN** there MUST be no `[union-attr]` errors for `engine.begin()` calls

#### Scenario: No sessionmaker type-var errors
- **WHEN** `uv run mypy .` is run
- **THEN** there MUST be no `[type-var]` or `[arg-type]` errors for `sessionmaker()` calls

### Requirement: Optional datetime handled before .desc()
All calls to `Entry.published.desc()` SHALL be guarded against `None` values.

#### Scenario: No union-attr errors on Entry.published
- **WHEN** `uv run mypy .` is run
- **THEN** there MUST be no `[union-attr]` errors for `Entry.published.desc()`

### Requirement: Column padding removed or migrated
The `ft.Column` constructor MUST NOT receive an unexpected `padding` keyword argument.

#### Scenario: No Column unexpected kwarg errors
- **WHEN** `uv run mypy .` is run
- **THEN** there MUST be no `[call-arg]` errors for `ft.Column()` with `padding`

### Requirement: Async coroutines are awaited
All async calls SHALL be properly awaited.

#### Scenario: No unused-coroutine errors
- **WHEN** `uv run mypy .` is run
- **THEN** there MUST be no `[unused-coroutine]` errors for unawaited coroutines

### Requirement: Async generator return type is correct
The `get_session` async generator function SHALL have the correct return type annotation per mypy.

#### Scenario: No async generator return type errors
- **WHEN** `uv run mypy .` is run
- **THEN** there MUST be no `[misc]` errors about async generator return types
