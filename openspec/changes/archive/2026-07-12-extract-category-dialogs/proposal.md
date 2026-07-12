## Why

`category_list_view.py` tem 341 linhas e é a segunda maior view do projeto. Contém dois dialogs inline (`_build_create_dialog` e `_build_rename_dialog`) com lógica de validação e callbacks assíncronos embutidos, misturando preocupações de UI com regras de negócio. Extrair para `app/controls/category_dialogs.py` reduz o tamanho da view, isola a lógica dos dialogs, e segue o padrão já estabelecido por `AddFeedDialog` e `ConfirmDialog`.

## What Changes

- Criar `app/controls/category_dialogs.py` com classes `CreateCategoryDialog` e `RenameCategoryDialog`
- Remover `_build_create_dialog()` e `_build_rename_dialog()` de `category_list_view.py`
- Substituir chamadas inline pelos novos imports dos dialogs
- `RenameCategoryDialog`: herda `ft.AlertDialog`, recebe `node`, `page`, `refresh_cb`, `ctx` no construtor
- `CreateCategoryDialog`: herda `ft.AlertDialog`, recebe `page`, `refresh_cb`, `ctx` no construtor, carrega categorias pai via `load_parents()`
- Nenhuma mudança de comportamento visível ao usuário

## Capabilities

### New Capabilities

_Nenhuma._ Refatoração interna (tech-debt) sem nova capacidade visível em spec-level.

### Modified Capabilities

_Nenhuma._ Nenhuma especificação existente tem requirements alterados.

## Impact

- `app/controls/category_dialogs.py` — novo arquivo (~80 linhas) com `CreateCategoryDialog` e `RenameCategoryDialog`
- `app/views/category_list_view.py` — perde ~75 linhas (dois builders inline), ganha imports
- Nenhum outro arquivo é afetado
- `_flatten_tree_for_dropdown` permanece em `category_list_view.py` (acoplamento via import no dialog)
