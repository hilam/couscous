# get_category_tree removido — dados planos, árvore construída inline

Data: 2026-07-12

## Status

Aceito.

## Contexto

`get_category_tree` fazia 3 consultas SQL (categorias, feed_counts,
unread_counts) e construía um dict aninhado com rollup recursivo de
contagens — tudo no mesmo módulo de service. O formato aninhado era então
achatado de volta por `_flatten_tree_for_dropdown`, uma função que existia
em duas réplicas (`add_feed_dialog.py` e `category_list_view.py`). A árvore
era construída só para ser desconstruída.

## Decisão

- `get_category_tree` é removido.
- `get_categories_with_counts(session, user_id)` retorna dados planos:
  `(list[Category], dict[int,int] feed_counts, dict[int,int] unread_counts)`.
- Cada consumidor que precisa de estrutura aninhada (feed_browser,
  category_list_view) constrói a árvore inline a partir dos dados planos —
  implementação trivial (~15 linhas de agrupamento por parent_id + rollup).
- `add_feed_dialog.py` usa dados planos direto para o dropdown — sem
  construir árvore, sem achatar. `_flatten_tree_for_dropdown` eliminado dali.
- `category_list_view.py` mantém `_flatten_tree_for_dropdown` só para o
  dropdown do dialog de criação (que precisa de indentação hierárquica).

## Consequências

**Positivas:**

- `category_service.py` perde 60 linhas de lógica de apresentação.
- `add_feed_dialog.py` perde 8 linhas de código duplicado.
- Dados planos são a interface certa para dropdowns — nenhum consumidor
  precisa construir e achar a mesma estrutura.
- `get_categories_with_counts` retorna tipos simples, fácil de testar e
  compor.

**Negativas:**

- `feed_browser.py` e `category_list_view.py` têm ~15 linhas cada de
  `_build_tree` — overlap aceito.
- Quem quiser a árvore aninhada precisa montá-la — não há função
  compartilhada.

## Alternativas consideradas

- **`build_tree` compartilhado puro:** função separada que os dois
  consumidores chamam. Rejeitado porque adiciona um módulo/export para ~15
  linhas de agrupamento — o overlap não justifica a interface.
