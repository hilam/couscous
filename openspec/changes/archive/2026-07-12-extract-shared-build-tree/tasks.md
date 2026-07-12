## 1. Git Setup e Planejamento

- [x] 1.1 Criar branch de funcionalidade: `git checkout -b chore/extract-shared-build-tree`
- [x] 1.2 Fazer commit dos artefatos de planejamento gerados: `git add openspec/changes/extract-shared-build-tree/ && git commit -m "docs(planning): gera artifacts para extract-shared-build-tree"`

## 2. Implementação — Extrair `_build_tree` para `category_service.py`

- [x] 2.1 Adicionar `build_category_tree()` em `app/services/category_service.py` (função pública síncrona, antes das funções privadas existentes)
- [x] 2.2 Commit incremental: `git add app/services/category_service.py && git commit -m "refactor(category): adiciona build_category_tree() pública"`

- [x] 2.3 Substituir `_build_tree` em `app/services/feed_browser.py`:
      - Ajustar import para incluir `build_category_tree` (linha 9)
      - Substituir `_build_tree(cats, feed_counts, unread_counts)` por `build_category_tree(cats, feed_counts, unread_counts)` (linha 35)
      - Remover função `_build_tree` local (linhas 199-234)
- [x] 2.4 Commit incremental: `git add app/services/feed_browser.py && git commit -m "refactor(feed-browser): usa build_category_tree compartilhada"`

- [x] 2.5 Substituir `_build_tree` em `app/views/category_list_view.py`:
      - Adicionar `build_category_tree` ao import de `category_service` (linhas 6-11)
      - Substituir as 3 chamadas de `_build_tree(...)` por `build_category_tree(...)` (linhas 61, 126, 186)
      - Remover função `_build_tree` local (linhas 296-331)
- [x] 2.6 Commit incremental: `git add app/views/category_list_view.py && git commit -m "refactor(category-list): usa build_category_tree compartilhada"`

## 3. Validação e Qualidade

- [x] 3.1 Verificar typecheck: `make typecheck` — esperado "Success: no issues found"
- [x] 3.2 Verificar lint: `make lint` — esperado "All checks passed!"
- [x] 3.3 Verificar testes existentes: `make test` — esperado mesmo resultado de antes (sem regressão)
- [x] 3.4 Confirmar que `_build_tree` não existe mais como função local: `grep -rn "def _build_tree" app/` — esperado nenhum resultado
- [x] 3.5 Confirmar que `build_category_tree` existe em `category_service.py`: `grep -n "def build_category_tree" app/services/category_service.py`
- [x] 3.6 Executar formatação: `ruff check --fix . && ruff format .`
- [x] 3.7 Commit final de formatação se houver mudanças: `git commit -m "style: aplica ruff e formata arquivos"`
