## Why

`feed_browser.py` contém a lógica de domínio mais crítica da aplicação — filtro por categoria, toggle de tags, busca full-text, e carregamento inicial de estado. São 5 funções puras extraídas da `explore_view` (ADR-0004) especificamente para serem testáveis sem Flet. Mas não há nenhum teste para elas. Zero cobertura = risco invisível de regressão.

## What Changes

- Criar `tests/test_feed_browser.py` com testes para todas as 5 funções de operação do `ExploreState`:
  - `load()` — 3 testes (vazio, com entries, com categorias)
  - `select_category()` — 3 testes (filtro, subcategorias, expand/collapse)
  - `toggle_tag()` — 2 testes (add/remove, filtra entries)
  - `clear_tags()` — 1 teste (remove todas)
  - `search()` — 2 testes (encontra por texto, query vazia limpa)
- Nenhuma mudança em `app/` — apenas testes

## Capabilities

### New Capabilities

Nenhuma — testes não introduzem capacidades de sistema.

### Modified Capabilities

Nenhuma — os requisitos do sistema não mudam.

## Impact

- **1 arquivo criado**: `tests/test_feed_browser.py` (~mínimo 11 testes)
- **Nenhum arquivo em `app/`** alterado
- **Nenhuma dependência nova** adicionada
- **Verificável**: `uv run pytest tests/test_feed_browser.py -v` → 0 failed, cobertura >80%
