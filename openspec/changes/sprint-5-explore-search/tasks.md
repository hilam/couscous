## 1. Git Setup e Planejamento

- [x] 1.1 Criar branch de funcionalidade (`git checkout -b feat/sprint-5-explore-search`)
- [x] 1.2 Fazer commit dos artefatos de planejamento (`git add openspec/changes/sprint-5-explore-search/ && git commit -m "docs(planning): gera proposal, specs, design, qa-plan para sprint-5-explore-search"`)

## 2. Migration — search_vector e índices

- [x] 2.1 Gerar migration Alembic (`make db-migrate-create name="add-search-vector"`)
- [x] 2.2 Editar migration para adicionar coluna `search_vector tsvector` com `GENERATED ALWAYS AS` + `regexp_replace` para strip de HTML, índice GIN, e índice `(user_id, published DESC)`
- [x] 2.3 Aplicar migration (`make db-migrate-up`)
- [x] 2.4 Fazer commit da migration (`git add alembic/versions/ && git commit -m "feat(db): adiciona search_vector tsvector com indice GIN e indice user_published"`)

## 3. Service Layer — busca e listagem cross-feed

- [x] 3.1 Criar `app/services/search_service.py` com função `search_entries(session, query, user_id, category_id, tag, limit)` usando `plainto_tsquery`, `ts_rank`, `ts_headline`
- [x] 3.2 Adicionar `list_recent(session, user_id, category_id, tag, limit)` ao `entry_service.py` — listagem cross-feed com filtro opcional de categoria e tag
- [x] 3.3 Adicionar `get_distinct_tags_with_counts(session, user_id)` ao `tag_service.py` — tags com contagem de entradas
- [x] 3.4 Escrever testes unitários para `search_service.py` (`tests/test_search_service.py`)
- [x] 3.5 Escrever testes unitários para `list_recent()` em `tests/test_entry_service.py`
- [x] 3.6 Escrever testes unitários para `get_distinct_tags_with_counts()` em `tests/test_tag_service.py`
- [x] 3.7 Fazer commit dos services e testes (`git add app/services/search_service.py app/services/entry_service.py app/services/tag_service.py tests/ && git commit -m "feat(services): adiciona search_service, list_recent cross-feed e tag counts"`)

## 4. Explore View — UI principal

- [x] 4.1 Criar `app/views/explore_view.py` com layout de 3 colunas: árvore de categorias (esquerda), conteúdo (centro), drawer de tags (direita)
- [x] 4.2 Implementar árvore de categorias lateral usando `get_category_tree()` — apenas categorias, sem feeds
- [x] 4.3 Implementar coluna central com estado "Recentes" (cross-feed via `list_recent`) e estado "Categoria" (filtrando por `category_id`)
- [x] 4.4 Implementar drawer de tags à direita com `get_distinct_tags_with_counts()`, multi-seleção AND, e badge no AppBar
- [x] 4.5 Implementar barra de busca no AppBar — ao digitar, substitui coluna central por resultados de `search_entries`
- [x] 4.6 Implementar layout responsivo: `page.width < 600` → árvore vira `PopupMenuButton`, drawer vira `ModalBottomSheet`
- [x] 4.7 Implementar integração: tocar numa entrada navega para `/entry/{id}`; filtros de busca + categoria + tag combinam-se com AND
- [ ] 4.8 Fazer commit da explore view (`git add app/views/explore_view.py && git commit -m "feat(ui): cria explore view com drill-down, tags drawer e busca"`)

## 5. Integração — Rotas e Navegação

- [x] 5.1 Alterar `app/app.py`: rota `/` de `feed_list_view` para `explore_view`; manter `/feeds` → `feed_list_view`
- [x] 5.2 Alterar `app/controls/nav_bar.py`: índice 0 vai para `/` (explore); índice 1 vai para `/feeds` (mantido)
- [x] 5.3 Alterar redirecionamento pós-login para `/` (explore) em vez de `/feeds`
- [x] 5.4 Escrever testes de navegação em `tests/test_app_navigation.py` — verificar rotas `/` e `/feeds`
- [x] 5.5 Fazer commit da integração (`git add app/app.py app/controls/nav_bar.py app/views/login_view.py tests/ && git commit -m "feat(nav): home page vira explore view, /feeds mantem lista plana"`)

## 6. Validação e Qualidade

- [x] 6.1 Executar linting com Ruff (`make lint`) e corrigir issues
- [x] 6.2 Executar formatação com Ruff (`make format`)
- [x] 6.3 Executar type checking com mypy (`make typecheck`) — `app/views/explore_view.py` e `app/services/search_service.py` devem passar
- [x] 6.4 Executar security scan (`make security`) — verificar que `sqlalchemy.text()` com interpolação de parâmetros não tem injection
- [x] 6.5 Executar todos os testes (`make test`) e verificar que passam
- [ ] 6.6 Fazer commit de correções de estilo se houver (`git add . && git commit -m "style: aplica ruff format, lint e mypy no sprint 5"`)
- [ ] 6.7 Executar `make check-all` para validação completa (lint + typecheck + test + security)
