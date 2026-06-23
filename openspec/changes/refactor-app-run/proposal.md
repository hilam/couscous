## Why

A função `app_run` em `app/app.py` concentra toda a lógica de roteamento no handler `on_route_change` com 100+ linhas, repetindo o mesmo padrão de criação de `PageContext` com `get_db_session()` em quase todas as branches do if/elif. A extração de parâmetros de rota (feed URL, entry ID) é feita inline com slicing de string. Isso dificulta manutenção, leitura e extensão — adicionar uma nova rota requer duplicar 5+ linhas de boilerplate de sessão e contexto.

## What Changes

- Extrair a criação de `PageContext` (com ou sem sessão de banco) para uma função auxiliar `_build_context`, eliminando a repetição de `async with get_db_session() / PageContext(...)` em cada branch
- Extrair o despacho de rotas para uma tabela de rotas declarativa (`_ROUTE_TABLE`), mapeando `(padrão, handler, requires_session)` em vez de uma cadeia longa de if/elif
- Extrair a extração de parâmetros de rota (feed URL, entry ID, query params) para funções utilitárias
- Simplificar `on_route_change` para: limpar views → obter handler da tabela → construir contexto → chamar view → anexar view → configurar navbar

## Capabilities

### New Capabilities

- `route-handler-refactor`: O handler `on_route_change` deve usar uma tabela de rotas declarativa e uma factory de contexto centralizada, eliminando código duplicado e simplificando a adição de novas rotas

### Modified Capabilities

- *Nenhuma* — o comportamento em runtime não muda; o roteamento, as views e a navbar permanecem idênticos

## Impact

- **1 arquivo core**: `app/app.py` — reescrita do `on_route_change` com extração de helpers
- **Sem mudanças** em views, modelos, serviços, dependências ou APIs
- Nenhum arquivo novo é estritamente necessário (helpers podem ficar como funções privadas no próprio `app.py` ou em um módulo `app/routing.py`)
