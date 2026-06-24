## Why

A árvore de categorias na tela principal (`explore_view`) atualmente exibe todos os nós planamente com indentação — sem expandir/colapsar. Para usuários com hierarquias profundas, a navegação é visualmente poluída e não há indicação de quais categorias possuem conteúdo. Clicar em qualquer categoria dispara uma query de notícias, mesmo em categorias-container sem feeds. A filtragem por categoria também não inclui notícias das subcategorias, tornando a hierarquia meramente cosmética para a listagem de conteúdo.

## What Changes

- Árvore de categorias com toggle de expandir/colapsar (`▶` / `⮋`) para nós com filhos
- Badge com contagem de artigos não lidos por categoria (contagem recursiva: soma da categoria + todas descendentes)
- Clique na categoria combina duas ações independentes: toggle de expandir/colapsar (se tem filhos) + seleção e carregamento de notícias (se tem feeds recursivamente)
- `list_recent` com suporte a `include_subcategories` para buscar entries de feeds na categoria e em todas as suas descendentes
- Mobile mantém `PopupMenuButton` plano, apenas com adição dos badges de contagem
- Badge com contagem zero é ocultado

## Capabilities

### New Capabilities

- `category-tree-expand`: Árvore interativa na explore_view com expand/colapsar, exibição de badge de não lidos recursivo, e comportamento de clique contextual (toggle + seleção).
- `recursive-category-filtering`: Consulta de entries com suporte a filtro por categoria que inclui todas as subcategorias descendentes recursivamente.

### Modified Capabilities

- `category-management`: O nó da árvore retornado por `get_category_tree` passa a incluir os campos `feed_count`, `total_feed_count` e `unread_count`.

## Impact

- `app/services/category_service.py`: `get_category_tree` — nova query de contagem de feeds e não lidos; nova função auxiliar para coleta de IDs descendentes
- `app/services/entry_service.py`: `list_recent` — novo parâmetro `include_subcategories`
- `app/views/explore_view.py`: `_build_category_tree` refeito com estado `expanded_ids`, badges, e lógica de clique contextual
- `app/views/category_list_view.py`: possível atualização leve para refletir os novos campos do nó (se necessário)
