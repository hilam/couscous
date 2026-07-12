## Why

`refresh_all_feeds` itera sequencialmente sobre todos os feeds do usuário — 20+ segundos bloqueantes para 20 feeds, com `state.loading` travando a UI. O ADR-0005 já previa refresh paralelo com limite de concorrência. A correção é trivial e de alto impacto perceptível.

## What Changes

- Refatorar `refresh_all_feeds` em `app/services/refresh_service.py`:
  - Loop `for feed in feeds` sequencial → `asyncio.gather` com tasks paralelas
  - Cada feed ganha sua própria sessão via `get_db_session()` (evita race conditions em commits)
  - `asyncio.Semaphore(5)` limita concorrência a 5 feeds simultâneos
  - `httpx.AsyncClient` é criado uma vez e compartilhado entre tasks
- Nenhuma mudança na assinatura da função (`session`, `user_id`, `client`)
- Nenhuma mudança em views ou callers

## Capabilities

### New Capabilities

Nenhuma — a API pública (`refresh_all_feeds(session, user_id, client=None)`) não muda.

### Modified Capabilities

Nenhuma — requisitos de sistema inalterados.

## Impact

- **1 arquivo modificado**: `app/services/refresh_service.py`
- **Nova dependência**: `from database.service.database import get_db_session`
- **Nenhuma view ou teste** precisa ser alterado
- **Verificável**: `make typecheck`, `uv run pytest tests/test_refresh_service.py -v`
