## Capability: category-tree-expand

### Test: Expandir categoria pai colapsada
**Traces**: `specs/category-tree-expand/spec.md` → Requirement: Expandir e colapsar categorias
- **GIVEN** árvore com "Tech" colapsada (indicador ▶) possuindo subcategorias "Frontend" e "Backend" ocultas
- **WHEN** usuário clica em "Tech"
- **THEN** indicador muda para ⮋ e "Frontend" e "Backend" tornam-se visíveis

### Test: Colapsar categoria pai expandida
**Traces**: `specs/category-tree-expand/spec.md` → Requirement: Expandir e colapsar categorias
- **GIVEN** árvore com "Tech" expandida (⮋) mostrando "Frontend" e "Backend"
- **WHEN** usuário clica em "Tech"
- **THEN** indicador muda para ▶ e "Frontend" e "Backend" (e toda sua descendência) somem

### Test: Folha sem indicador de toggle
**Traces**: `specs/category-tree-expand/spec.md` → Requirement: Expandir e colapsar categorias
- **GIVEN** categoria "React" sem subcategorias
- **WHEN** a árvore é renderizada
- **THEN** "React" não exibe ▶ nem ⮋

### Test: Estado interno de filho preservado ao colapsar e expandir pai
**Traces**: `specs/category-tree-expand/spec.md` → Requirement: Expandir e colapsar categorias
- **GIVEN** "Tech" expandida, "Frontend" também expandida mostrando "React"
- **WHEN** usuário colapsa "Tech" e depois expande "Tech" novamente
- **THEN** "Frontend" permanece expandida mostrando "React"

### Test: Badge visível com contagem recursiva
**Traces**: `specs/category-tree-expand/spec.md` → Requirement: Badge de artigos não lidos por categoria
- **GIVEN** "Tech" tem 3 não lidos diretos, "Frontend" (filha) tem 2 não lidos
- **WHEN** a árvore é renderizada
- **THEN** badge de "Tech" exibe "5" e badge de "Frontend" exibe "2"

### Test: Badge oculto com contagem zero
**Traces**: `specs/category-tree-expand/spec.md` → Requirement: Badge de artigos não lidos por categoria
- **GIVEN** "Finanças" não tem artigos não lidos (nem em subcategorias)
- **WHEN** a árvore é renderizada
- **THEN** nenhum badge é exibido ao lado de "Finanças"

### Test: CRITICAL - Categoria com filhos e feeds — toggle + seleção simultâneos
**Traces**: `specs/category-tree-expand/spec.md` → Requirement: Clique contextual na categoria
- **GIVEN** "Tech" está colapsada, possui subcategorias E `total_feed_count > 0`
- **WHEN** usuário clica em "Tech"
- **THEN** "Tech" expande (⮋) E o painel de notícias carrega entries de "Tech" e todas subcategorias

### Test: Categoria com filhos mas sem feeds — somente toggle
**Traces**: `specs/category-tree-expand/spec.md` → Requirement: Clique contextual na categoria
- **GIVEN** "Vazia" tem subcategorias mas `total_feed_count = 0`, painel mostra entries de outra categoria
- **WHEN** usuário clica em "Vazia"
- **THEN** nó expande/colapsa, painel de notícias permanece inalterado

### Test: Categoria folha com feeds — somente seleção
**Traces**: `specs/category-tree-expand/spec.md` → Requirement: Clique contextual na categoria
- **GIVEN** "React" não tem filhos mas tem `feed_count > 0`
- **WHEN** usuário clica em "React"
- **THEN** painel de notícias carrega entries de "React", "React" fica destacada como selecionada

### Test: Categoria folha sem feeds — sem ação
**Traces**: `specs/category-tree-expand/spec.md` → Requirement: Clique contextual na categoria
- **GIVEN** "Vazia" não tem filhos e `feed_count = 0`, painel mostra entries
- **WHEN** usuário clica em "Vazia"
- **THEN** nada muda no painel, sem toggle (pois não tem filhos)

### Test: CRITICAL - Seleção visual alterna entre categoria e Recentes
**Traces**: `specs/category-tree-expand/spec.md` → Requirement: Seleção visual da categoria ativa
- **GIVEN** "Tech" selecionada (destacada), "Recentes" sem destaque
- **WHEN** usuário clica em "Recentes"
- **THEN** "Recentes" fica destacado, "Tech" perde destaque, painel mostra todas as entries

### Test: EDGE - Cliques rápidos consecutivos
**Traces**: `specs/category-tree-expand/spec.md` → (edge case)
- **GIVEN** "Tech" colapsada
- **WHEN** usuário clica 3 vezes rapidamente em "Tech"
- **THEN** o estado final é consistente (expandido após número ímpar de cliques, colapsado após par), e não há erro de concorrência nas chamadas async

### Test: EDGE - Árvore vazia
**Traces**: `specs/category-tree-expand/spec.md` → (edge case)
- **GIVEN** usuário sem categorias
- **WHEN** a explore_view é carregada
- **THEN** painel esquerdo mostra mensagem "Nenhuma categoria", painel central mostra "Recentes" normalmente

### Test: EDGE - Categoria profundamente aninhada
**Traces**: `specs/category-tree-expand/spec.md` → (edge case)
- **GIVEN** árvore com 5 níveis de profundidade (A → B → C → D → E)
- **WHEN** usuário expande todos os níveis sequencialmente
- **THEN** todos os 5 níveis são visíveis com indentação progressiva, sem overflow horizontal

### Test: Mobile - Menu exibe badges
**Traces**: `specs/category-tree-expand/spec.md` → Requirement: Comportamento mobile simplificado
- **GIVEN** dispositivo com largura < 600px, "Tech" tem 5 não lidos
- **WHEN** usuário abre o menu de categorias
- **THEN** item do menu exibe "Tech (5)"

### Test: Mobile - Menu sem badge para zero
**Traces**: `specs/category-tree-expand/spec.md` → Requirement: Comportamento mobile simplificado
- **GIVEN** dispositivo mobile, "Finanças" tem 0 não lidos
- **WHEN** usuário abre o menu
- **THEN** item exibe apenas "Finanças" sem contagem

---

## Capability: recursive-category-filtering

### Test: list_recent com include_subcategories=True
**Traces**: `specs/recursive-category-filtering/spec.md` → Requirement: Filtrar entries por categoria recursivamente
- **GIVEN** categoria 1 tem feed A, subcategoria 2 tem feed B, subcategoria 3 tem feed C
- **WHEN** `list_recent(user_id, category_id=1, include_subcategories=True)` é chamado
- **THEN** retorna entries dos feeds A, B e C

### Test: list_recent com include_subcategories=False (padrão)
**Traces**: `specs/recursive-category-filtering/spec.md` → Requirement: Filtrar entries por categoria recursivamente
- **GIVEN** categoria 1 tem feed A, subcategoria 2 tem feed B
- **WHEN** `list_recent(user_id, category_id=1)` é chamado (sem include_subcategories ou False)
- **THEN** retorna apenas entries do feed A

### Test: include_subcategories sem category_id é ignorado
**Traces**: `specs/recursive-category-filtering/spec.md` → Requirement: Filtrar entries por categoria recursivamente
- **GIVEN** usuário tem entries de múltiplos feeds
- **WHEN** `list_recent(user_id, category_id=None, include_subcategories=True)` é chamado
- **THEN** retorna todas as entries recentes do usuário (comportamento idêntico a category_id=None)

### Test: Coleta de IDs descendentes — árvore de dois níveis
**Traces**: `specs/recursive-category-filtering/spec.md` → Requirement: Coleta de IDs de categorias descendentes
- **GIVEN** árvore com raiz 1, filhos 2 e 3, netos 4 (filho de 2) e 5 (filho de 3)
- **WHEN** `_collect_descendant_ids(tree, category_id=1)` é chamado
- **THEN** retorna [1, 2, 4, 3, 5] (ordem não relevante, mas todos os 5 IDs presentes)

### Test: Coleta de IDs — categoria folha
**Traces**: `specs/recursive-category-filtering/spec.md` → Requirement: Coleta de IDs de categorias descendentes
- **GIVEN** categoria 5 é folha (sem filhos)
- **WHEN** `_collect_descendant_ids(tree, category_id=5)` é chamado
- **THEN** retorna [5]

### Test: EDGE - Coleta de IDs — categoria inexistente
**Traces**: `specs/recursive-category-filtering/spec.md` → (edge case)
- **GIVEN** árvore não contém categoria com id 999
- **WHEN** `_collect_descendant_ids(tree, category_id=999)` é chamado
- **THEN** retorna lista vazia []

### Test: EDGE - list_recent com categoria vazia e include_subcategories
**Traces**: `specs/recursive-category-filtering/spec.md` → (edge case)
- **GIVEN** categoria 1 não tem feeds nem subcategorias com feeds
- **WHEN** `list_recent(user_id, category_id=1, include_subcategories=True)` é chamado
- **THEN** retorna lista vazia

---

## Capability: category-management (delta)

### Test: Nó da árvore inclui feed_count e unread_count
**Traces**: `specs/category-management/spec.md` → Requirement: List categories as tree
- **GIVEN** "Tech" tem 2 feeds e 3 artigos não lidos
- **WHEN** `get_category_tree(session, user_id)` é chamado
- **THEN** nó "Tech" tem `feed_count=2`, `total_feed_count=2`, `unread_count=3`

### Test: total_feed_count agrega subcategorias
**Traces**: `specs/category-management/spec.md` → Requirement: List categories as tree
- **GIVEN** "Tech" tem 1 feed, "Frontend" (filha) tem 2 feeds
- **WHEN** `get_category_tree` é chamado
- **THEN** "Tech" tem `feed_count=1` e `total_feed_count=3`; "Frontend" tem ambos = 2

### Test: EDGE - unread_count zero para todos os nós
**Traces**: `specs/category-management/spec.md` → (edge case)
- **GIVEN** usuário leu todos os artigos
- **WHEN** `get_category_tree` é chamado
- **THEN** todos os nós têm `unread_count=0`

---

## Edge Cases

- **Concorrência de refresh**: Se o usuário clicar em refresh enquanto uma query de entries está em andamento, o resultado da query anterior deve ser descartado (substituído pelo novo).
- **Categoria selecionada é deletada**: Se a categoria atualmente selecionada for deletada (via `/categories`), ao retornar para `/` a seleção deve ser limpa e "Recentes" deve ser exibido.
- **Nomes longos de categoria**: Nomes muito longos não devem quebrar o layout do painel de 220px — usar ellipsis no texto.

## Integration Points

- **`explore_view` ↔ `entry_view`**: Ao navegar para `/entry/<id>` e marcar como lido, ao retornar o badge deve refletir a nova contagem. Atualmente requer refresh manual — este é um gap conhecido (registrado como risco no design).
- **`explore_view` ↔ `category_list_view`**: Alterações em categorias (criar, renomear, deletar) feitas em `/categories` devem refletir na `explore_view` ao navegar de volta. Atualmente a view é reconstruída ao navegar, então isso funciona naturalmente.
- **Filtro de tags + categoria**: A combinação de filtro de tags com seleção de categoria recursiva deve funcionar (o `list_recent` já suporta ambos os parâmetros).

## Review Notes

- Nenhum cenário ambíguo ou não testável identificado nos specs.
