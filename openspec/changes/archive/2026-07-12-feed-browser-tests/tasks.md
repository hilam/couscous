## 1. Git Setup

- [x] 1.1 Criar branch de funcionalidade (`git checkout -b advisor/003-feed-browser-tests`)
- [x] 1.2 Fazer commit dos artefatos de planejamento gerados (`git add openspec/changes/feed-browser-tests/ && git commit -m "docs(planning): gera artifacts da change feed-browser-tests"`)

## 2. Implementação dos Testes

- [x] 2.1 Criar `tests/test_feed_browser.py` com imports e estrutura base (ExploreState, factories, funções)
- [x] 2.2 Implementar `test_load_empty`, `test_load_with_entries`, `test_load_with_categories`
- [x] 2.3 Implementar `test_select_category_filters_entries`, `test_select_category_with_subcategories`, `test_select_category_expands_and_collapses`
- [x] 2.4 Implementar `test_toggle_tag_adds_and_removes`, `test_toggle_tag_filters_entries`, `test_clear_tags_removes_all`
- [x] 2.5 Implementar `test_search_finds_entries`, `test_search_empty_query_clears`
- [x] 2.6 Fazer commit incremental (`git add tests/test_feed_browser.py && git commit -m "test: adiciona testes unitarios para feed_browser (ExploreState)"`)

## 3. Validação

- [x] 3.1 Verificar testes: `uv run pytest tests/test_feed_browser.py -v` — 0 failed
- [x] 3.2 Verificar cobertura: `uv run pytest tests/test_feed_browser.py --cov=app.services.feed_browser --cov-report=term-missing` — >80%
- [x] 3.3 Executar `make lint` — "All checks passed!"
- [x] 3.4 Verificar que nenhum `app/` foi modificado (`git diff --name-only main...HEAD | grep app/` → vazio)
