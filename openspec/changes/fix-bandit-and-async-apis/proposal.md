## Why

O `make security` (bandit) sempre falha porque os comentários de supressão usam `# noseq` em vez de `# nosec` — a diretiva correta. Além disso, o código mistura três pares de APIs inconsistentes (`page.launch_url` vs `UrlLauncher`, `page.go` vs `push_route`, `ensure_future` vs `create_task`), criando ruído em manutenção futura. Corrigir agora — zero risco, ganho imediato de DX.

## What Changes

- Corrigir 3 typos `# noseq` → `# nosec` em comentários de supressão do bandit
- Substituir `page.launch_url()` (deprecated) por `ft.UrlLauncher().launch_url()`
- Substituir `page.go("/login")` por `page.push_route("/login")` (padrão do codebase)
- Substituir 2 ocorrências de `asyncio.ensure_future()` por `asyncio.create_task()`
- Nenhuma mudança de comportamento em runtime — APIs são funcionalmente equivalentes

## Capabilities

### New Capabilities

Nenhuma — esta mudança não introduz novas capacidades.

### Modified Capabilities

Nenhuma — os requisitos de sistema não mudam. Apenas corrige sintaxe de supressão de ferramenta e padroniza chamadas de API equivalentes.

## Impact

- **6 arquivos modificados** (todos em `app/`):
  - `app/services/oauth_service.py` — 2 supressões bandit
  - `app/services/search_service.py` — 1 supressão bandit
  - `app/controls/oauth_buttons.py` — `launch_url` deprecated
  - `app/views/oauth_callback_view.py` — `page.go` → `push_route`
  - `app/controls/confirm_dialog.py` — `ensure_future` → `create_task`
  - `app/controls/add_feed_dialog.py` — `ensure_future` → `create_task`
- **Nenhuma dependência nova** adicionada
- **Nenhuma API pública** alterada
- **Verificável por máquina**: `make security`, `make lint`, `make typecheck` e greps
