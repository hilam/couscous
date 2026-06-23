## Capability: mypy-type-correctness

### Test: Mypy aceita tipo de retorno de get_db_session
**Traces**: `specs/mypy-type-correctness/spec.md` → Requirement: get_db_session retorna AsyncContextManager
- **GIVEN** o arquivo `database/service/database.py` com anotação corrigida para `AbstractAsyncContextManager[AsyncSession]`
- **WHEN** executa-se `make typecheck`
- **THEN** nenhum erro `attr-defined` sobre `__aenter__` ou `__aexit__` é reportado para `database/service/database.py`

### Test: Mypy aceita _session_factory em PageContext
**Traces**: `specs/mypy-type-correctness/spec.md` → Requirement: PageContext._session_factory aceita AbstractAsyncContextManager
- **GIVEN** o arquivo `app/context.py` com `_session_factory` tipado como `Callable[[], AbstractAsyncContextManager[AsyncSession]] | None`
- **WHEN** executa-se `make typecheck`
- **THEN** nenhum erro sobre `__aenter__` ou `__aexit__` é reportado para o método `new_session()`

### Test: Mypy aceita get_db_session como argumento em app.py
**Traces**: `specs/mypy-type-correctness/spec.md` → Requirement: app.py passa get_db_session como _session_factory sem erro de tipo
- **GIVEN** os arquivos `database/service/database.py` e `app/context.py` com as correções de tipo aplicadas
- **WHEN** executa-se `make typecheck`
- **THEN** nenhum erro `arg-type` é reportado nas linhas 78, 81 e 110 de `app/app.py`

### Test: Mypy não reporta unused-coroutine em oauth_buttons.py
**Traces**: `specs/mypy-type-correctness/spec.md` → Requirement: handlers de clique OAuth awaitam launch_url
- **GIVEN** `_oauth_click` declarado como `async def` com `await page.launch_url(uri)`
- **WHEN** executa-se `make typecheck`
- **THEN** nenhum erro `unused-coroutine` é reportado em `app/controls/oauth_buttons.py`

### Test: Mypy não reporta arg-type em login_view.py
**Traces**: `specs/mypy-type-correctness/spec.md` → Requirement: listas de controles de formulário passam verificação de variância
- **GIVEN** `form_controls` anotado como `list[ft.Control]` em `login_view.py`
- **WHEN** executa-se `make typecheck`
- **THEN** nenhum erro `arg-type` nas linhas de `extend()` e `Column(controls=...)`

### Test: Mypy não reporta arg-type em register_view.py
**Traces**: `specs/mypy-type-correctness/spec.md` → Requirement: listas de controles de formulário passam verificação de variância
- **GIVEN** `form_controls` anotado como `list[ft.Control]` em `register_view.py`
- **WHEN** executa-se `make typecheck`
- **THEN** nenhum erro `arg-type` nas linhas de `extend()` e `Column(controls=...)`

### Test: make check-all passa sem erros
**Traces**: `specs/mypy-type-correctness/spec.md` → (edge case)
- **GIVEN** todas as correções aplicadas
- **WHEN** executa-se `make check-all`
- **THEN** todos os estágios (lint, typecheck, test, security) passam sem falhas

### Test: EDGE - Testes automatizados continuam passando
**Traces**: `specs/mypy-type-correctness/spec.md` → (edge case)
- **GIVEN** todas as correções de tipo aplicadas
- **WHEN** executa-se `make test`
- **THEN** todos os testes passam, sem regressões de runtime

### Test: EDGE - OAuth buttons permanecem funcionais
**Traces**: `specs/mypy-type-correctness/spec.md` → (edge case)
- **GIVEN** `_oauth_click` agora é async com `await page.launch_url(uri)`
- **WHEN** usuário clica no botão "Entrar com Google" ou "Entrar com GitHub"
- **THEN** a URL de autorização OAuth é aberta corretamente no navegador

## Edge Cases

- Nenhum outro arquivo usa `get_db_session()` como factory de forma incompatível — verificar se há usos indiretos via `PageContext._session_factory`
- Se `ruff check` detectar imports não utilizados após remoção de código — verificar e limpar
- O Flet pode ter mudanças de comportamento entre versões para handlers async — verificar compatibilidade com 0.85.2

## Integration Points

- `database/service/database.py` ↔ `app/context.py`: a tipagem da factory deve ser consistente entre definição e uso
- `app/context.py` ↔ `app/app.py`: `PageContext` é instanciado em `_build_and_invoke()` e `app_run()`
- `app/controls/oauth_buttons.py` ↔ `app/views/login_view.py`, `app/views/register_view.py`: os botões OAuth são incluídos via `get_oauth_buttons()`

## Review Notes

- Nenhuma ambiguidade detectada nos specs — todos os cenários são verificáveis via `make typecheck`
