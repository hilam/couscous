## 1. Git Setup e Planejamento

- [x] 1.1 Criar branch de funcionalidade (`git checkout -b feat/collapsible-category-tree`)
- [x] 1.2 Fazer commit dos artefatos de planejamento (`git add openspec/changes/collapsible-category-tree/ && git commit -m "docs(planning): gera artefatos de planejamento para árvore de categorias colapsável"`)

## 2. Serviço — Contagens e estrutura do nó

- [x] 2.1 Adicionar queries de agregação em `category_service.py`: contagem de feeds por `category_id` e contagem de entries não lidas por `category_id` (via JOIN com feeds)
- [x] 2.2 Atualizar `get_category_tree()` para incluir `feed_count`, `total_feed_count` e `unread_count` em cada nó, com roll-up recursivo em memória
- [x] 2.3 Fazer commit do serviço de categorias (`git add app/services/category_service.py && git commit -m "feat(category): adiciona contagens de feeds e não lidos à árvore de categorias"`)

## 3. Serviço — Filtro recursivo de subcategorias

- [x] 3.1 Criar função auxiliar `_collect_descendant_ids(tree, category_id) -> list[int]` em `category_service.py`
- [x] 3.2 Adicionar parâmetro `include_subcategories: bool = False` em `list_recent()` no `entry_service.py`
- [x] 3.3 Implementar lógica: quando `include_subcategories=True` e `category_id` não nulo, usar `_collect_descendant_ids` + `IN` clause na query de feeds
- [x] 3.4 Fazer commit do filtro recursivo (`git add app/services/category_service.py app/services/entry_service.py && git commit -m "feat(entry): adiciona suporte a filtro recursivo de subcategorias no list_recent"`)

## 4. View — Árvore interativa na explore_view

- [x] 4.1 Adicionar estado `expanded_ids: set[int]` no closure da `explore_view`
- [x] 4.2 Refatorar `_build_category_tree()` para: (a) exibir ▶/⮋ condicional baseado em `children` não vazio, (b) badge no `trailing` com `unread_count` quando > 0, (c) renderizar filhos apenas se `id in expanded_ids`
- [x] 4.3 Implementar callback `select_category(cat_id)` com lógica contextual: toggle `expanded_ids` se tem filhos; seleciona + refresca entries se `total_feed_count > 0`; chama `list_recent` com `include_subcategories=True`
- [x] 4.4 Garantir que "Recentes" (selected_category_id=None) funcione como antes, chamando `list_recent` sem `category_id`
- [x] 4.5 Atualizar `_build_mobile_menu()` para incluir badges no texto dos itens (`"Tech (5)"`)
- [x] 4.6 Fazer commit da view (`git add app/views/explore_view.py && git commit -m "feat(explore): implementa árvore de categorias colapsável com badges e seleção recursiva"`)

## 5. Validação e Qualidade

- [x] 5.1 Executar linting e formatação com Ruff (`make lint && make format`)
- [x] 5.2 Fazer commit de correções de estilo se houver (`git commit -m "style: aplica ruff e formata arquivos"`)
- [x] 5.3 Executar typecheck com mypy (`make typecheck`)
- [x] 5.4 Corrigir erros de tipo se houver e commitar (`git commit -m "fix: corrige erros de tipo do mypy"`)
- [x] 5.5 Executar testes existentes (`make test`) e verificar regressões
- [x] 5.6 Executar security scan (`make security`)
- [x] 5.7 Executar check-all completo (`make check-all`)
