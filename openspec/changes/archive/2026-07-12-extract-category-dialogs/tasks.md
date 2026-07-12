## 1. Git Setup e Planejamento

- [x] 1.1 Criar branch de funcionalidade: `git checkout -b chore/extract-category-dialogs`
- [x] 1.2 Fazer commit dos artefatos de planejamento gerados: `git add openspec/changes/extract-category-dialogs/ && git commit -m "docs(planning): gera artifacts para extract-category-dialogs"`

## 2. Implementação — Extrair dialogs para `app/controls/category_dialogs.py`

- [x] 2.1 Criar `app/controls/category_dialogs.py` com `RenameCategoryDialog` (classe que herda `ft.AlertDialog`, recebe `node`, `page`, `refresh_cb`, `ctx`)
- [x] 2.2 Commit incremental: `git add app/controls/category_dialogs.py && git commit -m "refactor(controls): adiciona RenameCategoryDialog"`

- [x] 2.3 Adicionar `CreateCategoryDialog` em `app/controls/category_dialogs.py` (herda `ft.AlertDialog`, recebe `page`, `refresh_cb`, `ctx`, com método `load_parents()`)
- [x] 2.4 Commit incremental: `git add app/controls/category_dialogs.py && git commit -m "refactor(controls): adiciona CreateCategoryDialog"`

- [x] 2.5 Atualizar `app/views/category_list_view.py`:
      - Adicionar imports de `CreateCategoryDialog` e `RenameCategoryDialog`
      - Substituir `_build_rename_dialog(...)` por `RenameCategoryDialog(...)` em `_open_rename_dialog`
      - Substituir `_build_create_dialog(...)` por `CreateCategoryDialog(...)` em `open_new_dialog`, chamando `create_dlg.load_parents()`
      - Remover funções `_build_create_dialog()` e `_build_rename_dialog()`
- [x] 2.6 Commit incremental: `git add app/views/category_list_view.py && git commit -m "refactor(category-list): usa dialogs extraídos"`

## 3. Validação e Qualidade

- [x] 3.1 Verificar typecheck: `make typecheck` — esperado "Success: no issues found"
- [x] 3.2 Verificar lint: `make lint` — esperado "All checks passed!"
- [x] 3.3 Verificar testes existentes: `make test` — esperado mesmo resultado de antes (sem regressão)
- [x] 3.4 Confirmar que `_build_create_dialog` e `_build_rename_dialog` não existem mais na view: `grep -c "def _build_create_dialog\|def _build_rename_dialog" app/views/category_list_view.py` — esperado "0"
- [x] 3.5 Executar formatação: `ruff check --fix . && ruff format .`
- [x] 3.6 Commit final de formatação se houver mudanças: `git commit -m "style: aplica ruff e formata arquivos"`
