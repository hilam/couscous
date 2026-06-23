## ADDED Requirements

### Requirement: get_db_session retorna AsyncContextManager

A função `get_db_session()` em `database/service/database.py` SHALL ter anotação de retorno compatível com o fato de que `@asynccontextmanager` transforma a generator function em uma factory que produz `AbstractAsyncContextManager[AsyncSession]`. A anotação atual `AsyncGenerator[AsyncSession]` é incorreta — `AsyncGenerator` não possui `__aenter__`/`__aexit__` e não pode ser usado com `async with`.

#### Scenario: mypy aceita o tipo de retorno de get_db_session

- **WHEN** mypy verifica `database/service/database.py`
- **THEN** nenhum erro `attr-defined` é reportado sobre `__aenter__` ou `__aexit__`

### Requirement: PageContext._session_factory aceita AbstractAsyncContextManager

O campo `_session_factory` da dataclass `PageContext` em `app/context.py` SHALL ser tipado como `Callable[[], AbstractAsyncContextManager[AsyncSession]] | None`, refletindo que a factory retorna um async context manager (compatível com `async with`), não um `AsyncGenerator`.

#### Scenario: new_session funciona com async with sem erros mypy

- **WHEN** mypy verifica `app/context.py`
- **THEN** nenhum erro sobre `__aenter__` ou `__aexit__` no corpo de `new_session()`

### Requirement: app.py passa get_db_session como _session_factory sem erro de tipo

As chamadas a `PageContext(..., _session_factory=get_db_session)` em `app/app.py` SHALL ser aceitas por mypy, pois o tipo de `get_db_session` (após correção) é compatível com `_session_factory`.

#### Scenario: mypy não reporta arg-type em app.py

- **WHEN** mypy verifica `app/app.py`
- **THEN** nenhum erro `arg-type` é reportado nas linhas que instanciam `PageContext` com `_session_factory=get_db_session`

### Requirement: handlers de clique OAuth awaitam launch_url

O handler `_oauth_click` em `app/controls/oauth_buttons.py` SHALL ser declarado como `async def` e SHALL usar `await page.launch_url(uri)`. Atualmente a função é síncrona e chama `page.launch_url()` (que é `async`) sem await, descartando a coroutine e impedindo que a URL seja aberta.

#### Scenario: mypy não reporta unused-coroutine em oauth_buttons.py

- **WHEN** mypy verifica `app/controls/oauth_buttons.py`
- **THEN** nenhum erro `unused-coroutine` é reportado na linha de `page.launch_url(uri)`

### Requirement: listas de controles de formulário passam verificação de variância

As listas `form_controls` em `app/views/login_view.py` e `app/views/register_view.py` SHALL ser explicitamente anotadas como `list[ft.Control]` para evitar erros de invariância de `list` entre `LayoutControl` e `Control` ao usar `.extend()` e ao passar para `Column(controls=...)`.

#### Scenario: mypy não reporta arg-type em login_view.py

- **WHEN** mypy verifica `app/views/login_view.py`
- **THEN** nenhum erro `arg-type` é reportado nas linhas de `form_controls.extend(...)` ou `Column(controls=form_controls)`

#### Scenario: mypy não reporta arg-type em register_view.py

- **WHEN** mypy verifica `app/views/register_view.py`
- **THEN** nenhum erro `arg-type` é reportado nas linhas de `form_controls.extend(...)` ou `Column(controls=form_controls)`
