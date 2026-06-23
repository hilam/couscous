## Why

`make typecheck` (`uv run mypy`) reporta 10 erros em 5 arquivos, agrupados em 3 causas raiz. O type checker está efetivamente quebrado — qualquer CI que execute `make check-all` falhará. A causa raiz 2 (OAuth) é um **bug real**: `page.launch_url()` nunca executa porque a coroutine não é awaitada, tornando os botões de login Google/GitHub inoperantes.

## What Changes

- **database/service/database.py**: Corrigir anotação de retorno de `get_db_session()` — `AsyncGenerator` → `AbstractAsyncContextManager`
- **app/context.py**: Corrigir tipo de `_session_factory` na dataclass `PageContext` para refletir que a factory retorna um async context manager, não um async generator
- **app/app.py**: Sem alterações de tipagem (a compatibilidade é herdada da correção em `context.py`)
- **app/controls/oauth_buttons.py**: Tornar `_oauth_click` assíncrono e awaitar `page.launch_url()` — correção de bug funcional
- **app/views/login_view.py** e **app/views/register_view.py**: Anotar `form_controls` explicitamente como `list[ft.Control]` para eliminar erro de variância de `list`

## Capabilities

### New Capabilities

- `mypy-type-correctness`: O projeto SHALL passar `make typecheck` com zero erros, garantindo que o CI (`make check-all`) não falhe por problemas de tipagem e que bugs como coroutines não-awaitadas sejam detectados

### Modified Capabilities

- *Nenhuma* — os requisitos funcionais não mudam. Apenas corrigem-se anotações de tipo e um bug de runtime (OAuth)

## Impact

- **5 arquivos** modificados: `database/service/database.py`, `app/context.py`, `app/controls/oauth_buttons.py`, `app/views/login_view.py`, `app/views/register_view.py`
- **1 bug real corrigido**: botões OAuth Google/GitHub que atualmente não funcionam (coroutine descartada)
- Sem mudanças de dependências, modelo de dados, ou APIs
- Sem breaking changes — comportamento em runtime inalterado exceto pela correção do OAuth
