# Plano 003: Testes unitários para `feed_browser.py` (ExploreState)

> **Instruções ao executor**: Siga este plano passo a passo. Execute todo
> comando de verificação e confirme o resultado esperado antes de passar para
> o próximo passo. Se algo na seção "Condições STOP" ocorrer, pare e reporte
> — não improvise. Quando terminar, atualize a linha de status deste plano
> em `plans/README.md`.
>
> **Verificação de deriva (execute primeiro)**: `git diff --stat c24a31f..HEAD -- app/services/feed_browser.py app/services/entry_service.py app/services/category_service.py app/services/tag_service.py app/services/search_service.py tests/test_factory.py tests/conftest.py`
> Se qualquer arquivo no escopo mudou desde que este plano foi escrito,
> compare os excertos de "Estado atual" contra o código vivo antes de
> prosseguir; em caso de incompatibilidade, trate como condição STOP.

## Status

- **Prioridade**: P1
- **Esforço**: M
- **Risco**: BAIXO
- **Depende de**: nenhum
- **Categoria**: tests
- **Planejado em**: commit `c24a31f`, 2026-07-12

## Por que isso é importante

`feed_browser.py` contém a lógica de domínio mais crítica da aplicação — filtro por categoria, toggle de tags, busca full-text, e carregamento inicial de estado. São 5 funções puras que recebem `session + ExploreState` e retornam `ExploreState` novo. O ADR-0004 as extraiu da `explore_view` especificamente para serem testáveis sem Flet.

Mas não há nenhum teste para elas. Zero. Isso significa que toda a lógica de filtro da view principal (a página inicial `/`) não tem cobertura. Se alguém quebrar `select_category` ou `toggle_tag`, ninguém saberá até um teste manual. Como estas funções são puras (sem dependência de Flet), testá-las é barato e direto.

## Estado atual

Arquivos relevantes:

- `app/services/feed_browser.py` (237 linhas) — contém `ExploreState` dataclass + 5 funções de operação: `load()`, `select_category()`, `toggle_tag()`, `clear_tags()`, `search()`. Funções auxiliares: `_load_entry_tags()`, `_find_node()`, `_build_tree()`.
- `tests/test_factory.py` — fábricas reutilizáveis: `make_user()`, `make_feed()`, `make_entry()`, `rss_feed_xml()`, `atom_feed_xml()`.
- `tests/conftest.py` — fixture `db_session` (async session PostgreSQL), fixture `mock_oauth_config`.

Convenções do repositório para testes de serviço (siga estes padrões):

- Testes usam `@pytest.mark.asyncio` e recebem `db_session` como primeiro argumento.
- Usam factories de `tests/test_factory.py` (ex: `make_user`, `make_feed`, `make_entry`).
- Padrão de assert: verifica propriedades do objeto retornado.
- Exemplo canônico: `tests/test_entry_service.py` — cria user/feed/entry via factory, chama função do serviço, faz assert nos resultados.

Termos de domínio (CONTEXT.md):

- **Entry**: artigo individual de um feed. Unidade de consumo.
- **Category**: pasta hierárquica que organiza feeds. Auto-relacionamento via `parent_id`.
- **Tag**: rótulo textual em entry (não em feed). Múltiplas tags por entry.
- **ExploreState**: dataclass imutável com estado completo da explore view (filtros + dados).

## Comandos que você vai precisar

| Propósito | Comando | Esperado em caso de sucesso |
|-----------|---------|------------------------------|
| Testes | `uv run pytest tests/test_feed_browser.py -v` | todos passam |
| Testes gerais | `make test` | 0 failed nas suítes existentes + novos passam |
| Lint | `make lint` | "All checks passed!" |
| Cobertura | `uv run pytest tests/test_feed_browser.py --cov=app.services.feed_browser --cov-report=term-missing` | >80% coverage |

## Escopo

**No escopo** (os únicos arquivos que você deve modificar):
- `tests/test_feed_browser.py` — criar este arquivo com testes para todas as 5 funções de operação

**Fora de escopo** (NÃO toque):
- `app/services/feed_browser.py` — nenhuma mudança no código de produção
- Qualquer view ou controle — este plano é só testes
- Outros arquivos de teste

## Fluxo git

- Branch: `advisor/003-feed-browser-tests`
- Commits: `test: adiciona testes unitários para feed_browser (ExploreState)`
- NÃO faça push ou abra PR a menos que o operador o instrua.

## Passos

### Passo 1: Criar `tests/test_feed_browser.py` — imports e estrutura

```python
"""Testes para feed_browser.py — operações do ExploreState."""
import pytest

from app.services.feed_browser import (
    ExploreState,
    clear_tags,
    load,
    search,
    select_category,
    toggle_tag,
)
from tests.test_factory import make_entry, make_feed, make_user
from app.services.category_service import create_category
from app.services.feed_service import update_feed_category
from app.services.tag_service import assign_tag


def _now():
    from datetime import datetime
    return datetime(2024, 1, 1, 12, 0, 0)
```

### Passo 2: Testar `load()` — carregamento inicial do estado

Escreva 3 testes:

- `test_load_empty`: usuário sem feeds, sem categorias → `ExploreState` com `entries=[]`, `tree=[]`, `tag_counts=[]`.
- `test_load_with_entries`: usuário com 2 feeds, cada um com 1 entry → `ExploreState` com `len(entries) == 2`, `tag_map` populado se entries tiverem tags.
- `test_load_with_categories`: usuário com categorias aninhadas (parent + child) → `tree` contém hierarquia, `total_feed_count` com rollup.

Padrão estrutural (copie de `tests/test_entry_service.py`):
```python
@pytest.mark.asyncio
async def test_load_empty(db_session):
    user = await make_user(db_session)
    state = await load(db_session, user.id)
    assert state.entries == []
    assert state.tree == []
    assert state.tag_counts == []
    assert state.selected_category_id is None
    assert state.selected_tags == set()
```

**Verificar**: `uv run pytest tests/test_feed_browser.py::test_load_empty -v` → 1 passed.

### Passo 3: Testar `select_category()` — filtro por categoria

Escreva 3 testes:

- `test_select_category_filters_entries`: cria 2 feeds em 2 categorias diferentes (cada com 1 entry). Seleciona categoria 1 → `len(state.entries) == 1`.
- `test_select_category_with_subcategories`: cria categoria pai com feed (1 entry) + categoria filha com feed (1 entry). Seleciona pai → `len(state.entries) == 2` (include_subcategories=True).
- `test_select_category_expands_and_collapses`: seleciona categoria com filhos → `category_id in state.expanded_ids`. Seleciona de novo → `category_id not in state.expanded_ids`.

Use `create_category()` e `update_feed_category()` para organizar os feeds em categorias.

**Verificar**: `uv run pytest tests/test_feed_browser.py -k "select_category" -v` → 3 passed.

### Passo 4: Testar `toggle_tag()` e `clear_tags()` — filtro por tags

Escreva 3 testes:

- `test_toggle_tag_adds_and_removes`: cria entry com tag "python". Toggle "python" → `"python" in state.selected_tags`. Toggle de novo → `"python" not in state.selected_tags`.
- `test_toggle_tag_filters_entries`: cria 2 entries, só uma tem tag "python". Toggle "python" → `len(state.entries) == 1`.
- `test_clear_tags_removes_all`: estado com 2 tags selecionadas. `clear_tags()` → `state.selected_tags == set()`, entries voltam ao normal.

Use `assign_tag()` para adicionar tags às entries.

**Verificar**: `uv run pytest tests/test_feed_browser.py -k "tag" -v` → 3 passed.

### Passo 5: Testar `search()` — busca full-text

Escreva 2 testes:

- `test_search_finds_entries`: cria entry com title="Machine learning basics". `search()` com query "machine" → resultado contém a entry.
- `test_search_empty_query_clears`: `search()` com query vazia → `state.is_searching == False`, entries voltam ao estado sem filtro de busca.

Nota: `search()` usa `search_entries()` que depende de PostgreSQL tsvector. A fixture `db_session` em conftest.py já adiciona a coluna `search_vector` via `_add_search_vector_column()`. Se o teste falhar com "column e.search_vector does not exist", verifique se o banco `couscous_test` tem a extensão `tsvector` habilitada (PostgreSQL 16 já inclui por padrão).

**Verificar**: `uv run pytest tests/test_feed_browser.py -k "search" -v` → 2 passed.

### Passo 6: Verificação final

```bash
uv run pytest tests/test_feed_browser.py -v
# Esperado: todos passam (mínimo 11 testes)

uv run pytest tests/test_feed_browser.py --cov=app.services.feed_browser --cov-report=term-missing
# Esperado: >80% coverage em feed_browser.py

make lint
# Esperado: "All checks passed!"
```

## Plano de testes

Este plano É o plano de testes. O arquivo `tests/test_feed_browser.py` cobre:

| Função | Happy path | Borda |
|--------|-----------|-------|
| `load()` | Com entries, com categorias | Vazio (sem dados) |
| `select_category()` | Filtra entries, inclui subcategorias | Expand/collapse toggle |
| `toggle_tag()` | Adiciona/remove tag, filtra entries | — |
| `clear_tags()` | Remove todas tags | — |
| `search()` | Encontra por texto | Query vazia limpa busca |

Total: mínimo 11 testes, cobrindo todas as 5 funções de operação + função `load()`.

## Critérios de conclusão

- [ ] `uv run pytest tests/test_feed_browser.py -v` → todos passam, mínimo 11 testes
- [ ] `--cov=app.services.feed_browser` reporta >80% de cobertura
- [ ] `make lint` sai com "All checks passed!"
- [ ] Nenhum arquivo em `app/` foi modificado
- [ ] `tests/test_feed_browser.py` segue o padrão de imports e estrutura de `tests/test_entry_service.py`

## Condições STOP

Pare e reporte (não improvise) se:

- `search()` falha com "column e.search_vector does not exist" — o banco de teste não tem a coluna gerada. Verifique `tests/conftest.py::_add_search_vector_column`.
- A fixture `db_session` não está disponível ou o banco `couscous_test` não existe — execute `make db-up` antes dos testes.
- `make_entry()` do `test_factory.py` tem assinatura diferente do que este plano assume (verifique com `grep "async def make_entry" tests/test_factory.py`).
- Os testes de `select_category` com subcategorias retornam 0 entries — pode ser que `list_recent()` com `include_subcategories=True` não está funcionando como esperado. Neste caso, reporte o comportamento observado.

## Notas de manutenção

- Se `ExploreState` ganhar novos campos, os testes de `load()` devem ser atualizados para verificá-los.
- Se `list_recent()` ou `search_entries()` mudarem de assinatura, os testes indiretamente testam essa integração — falhas indicam breaking changes.
- Estes testes são de integração (usam banco real via `db_session`), não unitários puros. Se ficarem lentos (>5s), considere reduzir o número de entries criadas por teste.
