## Why

12 testes de view falham com `TypeError: PageContext.__init__() missing 1 required positional argument: '_session_factory'`. Isso quebra a confiança no `make test` — ninguém pode verificar se mudanças nas views introduzem regressões. Os testes foram escritos antes de o `session` se tornar obrigatório no `PageContext` (ADR-0003) e nunca foram atualizados.

## What Changes

- Adicionar fixture `page_context` reutilizável em `tests/conftest.py` com `session` e `_session_factory` mockados
- Atualizar `tests/test_about_view.py` (2 testes) para usar a fixture
- Atualizar `tests/test_home.py` (3 testes) para usar a fixture
- Atualizar `tests/test_login_view.py` (4 testes) para usar a fixture
- Atualizar `tests/test_register_view.py` (3 testes) para usar a fixture
- Nenhuma mudança em `app/` — o bug está apenas nos testes

## Capabilities

### New Capabilities

Nenhuma — esta mudança não introduz novas capacidades de sistema.

### Modified Capabilities

Nenhuma — os requisitos do sistema não mudam. Apenas corrige testes que quebraram por uma mudança anterior na API do `PageContext`.

## Impact

- **5 arquivos modificados** (todos em `tests/`):
  - `tests/conftest.py` — nova fixture `page_context`
  - `tests/test_about_view.py` — substitui construção manual de `PageContext` pela fixture
  - `tests/test_home.py` — idem
  - `tests/test_login_view.py` — idem
  - `tests/test_register_view.py` — idem
- **Nenhum arquivo em `app/`** é alterado
- **Nenhuma dependência nova** adicionada
- **Verificável**: `uv run pytest tests/test_about_view.py tests/test_home.py tests/test_login_view.py tests/test_register_view.py -v` → 0 failed
