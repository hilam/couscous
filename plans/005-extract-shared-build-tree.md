# Plano 005: Extrair `_build_tree` compartilhado para `category_service.py`

> **Instruções ao executor**: Siga este plano passo a passo. Execute todo
> comando de verificação e confirme o resultado esperado antes de passar para
> o próximo passo. Se algo na seção "Condições STOP" ocorrer, pare e reporte
> — não improvise. Quando terminar, atualize a linha de status deste plano
> em `plans/README.md`.
>
> **Verificação de deriva (execute primeiro)**: `git diff --stat c24a31f..HEAD -- app/services/feed_browser.py app/views/category_list_view.py app/services/category_service.py tests/test_category_service.py`
> Se qualquer arquivo no escopo mudou desde que este plano foi escrito,
> compare os excertos de "Estado atual" contra o código vivo antes de
> prosseguir; em caso de incompatibilidade, trate como condição STOP.

## Status

- **Prioridade**: P2
- **Esforço**: P
- **Risco**: BAIXO
- **Depende de**: plano 003 (testes de feed_browser) — idealmente feito depois para que os testes existentes protejam a refatoração
- **Categoria**: tech-debt
- **Planejado em**: commit `c24a31f`, 2026-07-12

## Por que isso é importante

A função `_build_tree` está duplicada em dois arquivos com ~35 linhas idênticas cada:
- `app/services/feed_browser.py:265-300`
- `app/views/category_list_view.py:277-312`

O ADR-0006 aceitou o overlap como tradeoff, mas a duplicação é real: qualquer mudança na estrutura da árvore (ex: adicionar `has_unread` ou um campo `icon`) requer tocar dois arquivos, e a probabilidade de divergência silenciosa cresce com o tempo. Extrair para uma função compartilhada em `category_service.py` resolve sem adicionar complexidade — o módulo já contém `get_categories_with_counts` que retorna os dados planos, e `_build_tree` é o consumidor natural desses dados.

## Estado atual

As duas cópias são funcionalmente idênticas. Comparação:

**feed_browser.py:265-300:**
```python
def _build_tree(
    cats: list, feed_counts: dict[int, int], unread_counts: dict[int, int]
) -> list[dict]:
    cat_map: dict[int, dict] = {}
    for c in cats:
        cat_map[c.id] = {
            "id": c.id,
            "name": c.name,
            "parent_id": c.parent_id,
            "children": [],
            "feed_count": feed_counts.get(c.id, 0),
            "total_feed_count": 0,
            "unread_count": 0,
        }

    tree: list[dict] = []
    for c in cats:
        node = cat_map[c.id]
        if c.parent_id and c.parent_id in cat_map:
            cat_map[c.parent_id]["children"].append(node)
        else:
            tree.append(node)

    def _rollup(node: dict) -> tuple[int, int]:
        fc = node["feed_count"]
        ur = unread_counts.get(node["id"], 0)
        for child in node["children"]:
            child_fc, child_ur = _rollup(child)
            fc += child_fc
            ur += child_ur
        node["total_feed_count"] = fc
        node["unread_count"] = ur
        return fc, ur

    for root in tree:
        _rollup(root)

    return tree
```

**category_list_view.py:277-312:** Idêntica (mesma lógica, mesmos nomes de variáveis, mesmo algoritmo).

Arquivos e seus papéis:

- `app/services/category_service.py` — já exporta `get_categories_with_counts()` que retorna `(list[Category], dict[int,int], dict[int,int])`. É o lugar natural para `_build_tree`.
- `app/services/feed_browser.py` — importa `get_categories_with_counts` de `category_service.py` (linha 11). Usa `_build_tree` local na função `load()` (linha 43).
- `app/views/category_list_view.py` — importa `get_categories_with_counts` de `category_service.py` (linha 7). Usa `_build_tree` local em `refresh_tree()` (linha 67) e em `_build_create_dialog` (linha 189).

Convenções: funções exportadas em services usam `async def` (ex: `get_categories_with_counts`). `_build_tree` é pura (síncrona, sem I/O) — mantenha-a síncrona.

## Comandos que você vai precisar

| Propósito | Comando | Esperado em caso de sucesso |
|-----------|---------|------------------------------|
| Typecheck | `make typecheck` | "Success: no issues found" |
| Testes | `make test` | todos passam |
| Lint | `make lint` | "All checks passed!" |
| Cobertura | `uv run pytest tests/test_category_service.py -v` | todos passam |

## Escopo

**No escopo**:
- `app/services/category_service.py` — adicionar função `build_category_tree()`
- `app/services/feed_browser.py` — substituir `_build_tree` local por import
- `app/views/category_list_view.py` — substituir `_build_tree` local por import

**Fora de escopo** (NÃO toque):
- A lógica interna de `_build_tree` — apenas mova, não refatore
- `app/views/explore_view.py` — não usa `_build_tree` diretamente
- Qualquer outro service ou view

## Fluxo git

- Branch: `advisor/005-extract-build-tree`
- Commits: `refactor: extrai _build_tree duplicada para category_service.py`
- NÃO faça push ou abra PR a menos que o operador o instrua.

## Passos

### Passo 1: Adicionar `build_category_tree()` em `category_service.py`

Adicione a função pública ao final de `app/services/category_service.py`, antes das funções privadas existentes:

```python
def build_category_tree(
    cats: list[Category],
    feed_counts: dict[int, int] | None = None,
    unread_counts: dict[int, int] | None = None,
) -> list[dict]:
    """Build a nested category tree from flat category data.

    Returns a list of root-level dicts, each with keys:
    id, name, parent_id, children, feed_count, total_feed_count, unread_count.

    total_feed_count includes feeds from descendant categories (rollup).
    unread_count includes unread entries from descendant categories (rollup).
    """
    fc = feed_counts or {}
    ur = unread_counts or {}

    cat_map: dict[int, dict] = {}
    for c in cats:
        cat_map[c.id] = {
            "id": c.id,
            "name": c.name,
            "parent_id": c.parent_id,
            "children": [],
            "feed_count": fc.get(c.id, 0),
            "total_feed_count": 0,
            "unread_count": 0,
        }

    tree: list[dict] = []
    for c in cats:
        node = cat_map[c.id]
        if c.parent_id and c.parent_id in cat_map:
            cat_map[c.parent_id]["children"].append(node)
        else:
            tree.append(node)

    def _rollup(node: dict) -> tuple[int, int]:
        fc_node = node["feed_count"]
        ur_node = ur.get(node["id"], 0)
        for child in node["children"]:
            child_fc, child_ur = _rollup(child)
            fc_node += child_fc
            ur_node += child_ur
        node["total_feed_count"] = fc_node
        node["unread_count"] = ur_node
        return fc_node, ur_node

    for root in tree:
        _rollup(root)

    return tree
```

Adicione `from __future__ import annotations` no topo se ainda não estiver presente (está em `feed_browser.py`, verifique `category_service.py`).

**Verificar**: `make typecheck` → "Success: no issues found".

### Passo 2: Substituir `_build_tree` em `feed_browser.py`

No topo de `app/services/feed_browser.py`, adicione o import:
```python
from app.services.category_service import build_category_tree, get_categories_with_counts
```

(Nota: `get_categories_with_counts` já é importado. Ajuste a linha existente.)

Na função `load()` (linha ~43), substitua:
```python
    tree = _build_tree(cats, feed_counts, unread_counts)
```
por:
```python
    tree = build_category_tree(cats, feed_counts, unread_counts)
```

Remova a função `_build_tree` local (linhas 265-300 de `feed_browser.py`).

**Verificar**: `make typecheck` → "Success: no issues found". `make lint` → "All checks passed!".

### Passo 3: Substituir `_build_tree` em `category_list_view.py`

No topo de `app/views/category_list_view.py`, ajuste o import existente:
```python
from app.services.category_service import (
    build_category_tree,
    create_category,
    delete_category,
    get_categories_with_counts,
    rename_category,
)
```

Substitua todas as chamadas a `_build_tree(cats, feed_counts, unread_counts)` por `build_category_tree(cats, feed_counts, unread_counts)`. São 3 chamadas:
1. Na função `refresh_tree()` (linha ~67)
2. Na função `_build_create_dialog` (linha ~189)
3. Na inicialização que constrói `initial_tree` (linha ~121)

Remova a função `_build_tree` local (linhas 277-312 de `category_list_view.py`).

**Verificar**: `make typecheck` → "Success: no issues found". `make lint` → "All checks passed!".

### Passo 4: Verificação final

```bash
make test
# Esperado: todos os testes passam (12 falhas existentes dos views não relacionados)
# Nenhum novo teste deve falhar

make lint
# Esperado: "All checks passed!"

make typecheck
# Esperado: "Success: no issues found"

# Confirme que _build_tree não existe mais como função local
grep -rn "def _build_tree" app/
# Esperado: nenhum resultado (a função foi removida de ambos os arquivos)

# Confirme que build_category_tree existe em category_service.py
grep -n "def build_category_tree" app/services/category_service.py
# Esperado: mostra a linha da nova função
```

## Plano de testes

Nenhum novo teste necessário. A lógica é movida, não alterada. Os testes existentes que dependem indiretamente de `_build_tree` continuam passando:

- `test_category_service.py` — não testa `_build_tree` diretamente, mas `get_categories_with_counts` é testado e produz os dados planos que alimentam a árvore.
- Os testes de `feed_browser.py` (plano 003) exercitam `load()` que chama `build_category_tree`.

Se o plano 003 já foi executado, execute `uv run pytest tests/test_feed_browser.py -v` para confirmar que nada quebrou.

## Critérios de conclusão

- [ ] `build_category_tree` existe em `app/services/category_service.py`
- [ ] `_build_tree` NÃO existe em `app/services/feed_browser.py`
- [ ] `_build_tree` NÃO existe em `app/views/category_list_view.py`
- [ ] Ambos os arquivos importam `build_category_tree` de `category_service`
- [ ] `make typecheck` → "Success: no issues found"
- [ ] `make lint` → "All checks passed!"
- [ ] `make test` → mesmo número de pass/fail de antes (nenhuma regressão)
- [ ] Nenhum arquivo fora da lista de escopo foi modificado

## Condições STOP

Pare e reporte (não improvise) se:

- As duas cópias de `_build_tree` divergiram desde que este plano foi escrito — compare linha por linha. Se houver diferenças, a extração pode precisar de uma versão que acomode ambas, ou uma delas está errada.
- Remover `_build_tree` de `category_list_view.py` quebra o `_build_create_dialog` — a função `_flatten_tree_for_dropdown` também existe lá e depende do formato da árvore. Se o formato mudar, ajuste `_flatten_tree_for_dropdown` para usar a nova função.
- `make test` mostra novos testes falhando (além dos 12 já quebrados do plano 002).

## Notas de manutenção

- `build_category_tree` é síncrona e pura — não requer session. Se no futuro precisar de dados do banco durante a construção da árvore (ex: carregar ícones de categoria), a função provavelmente deve ser dividida: carregamento async + construção sync.
- Se o formato do dicionário retornado mudar (novos campos), os consumidores (`feed_browser.py`, `category_list_view.py`) devem ser atualizados. A centralização torna isso mais fácil — antes eram 2 lugares, agora é 1 definição + 2 usos.
