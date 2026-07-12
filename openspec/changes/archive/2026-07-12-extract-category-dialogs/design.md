## Context

`category_list_view.py` (341 linhas) contém dois builders de dialog inline que misturam lógica de UI e regras de negócio:

- `_build_create_dialog()` (~75 linhas) — cria `ft.AlertDialog` com campo de nome, dropdown de categoria pai, validação de duplicata e callbacks `_submit_and_close` / `_submit_and_continue`
- `_build_rename_dialog()` (~40 linhas) — cria `ft.AlertDialog` com campo de nome preenchido e validação de duplicata

O projeto já possui o padrão de dialogs extraídos em `app/controls/`: `AddFeedDialog`, `ConfirmDialog`.

## Goals / Non-Goals

**Goals:**

- Extrair `CreateCategoryDialog` e `RenameCategoryDialog` para `app/controls/category_dialogs.py`
- Remover `_build_create_dialog()` e `_build_rename_dialog()` de `category_list_view.py`
- Seguir o padrão existente: classes que herdam `ft.AlertDialog`, recebem callbacks no `__init__`
- Manter comportamento idêntico (sem mudança funcional)

**Non-Goals:**

- Não mover `_flatten_tree_for_dropdown` (permanece na view)
- Não modificar a lógica de `_build_tree_controls`
- Não tocar `explore_view.py` ou qualquer outro arquivo fora do escopo
- Não adicionar novos testes

## Decisions

| Decisão | Alternativa | Rationale |
|---------|-------------|-----------|
| Classes que herdam `ft.AlertDialog` | Funções que retornam `ft.AlertDialog` | Segue o padrão de `AddFeedDialog` e `ConfirmDialog`. Herança permite estado interno e métodos nomeados. |
| `RenameCategoryDialog` recebe `node`, `page`, `refresh_cb`, `ctx` no construtor | Receber apenas valores escalares | O dialog precisa do `node["id"]` e `node["name"]`, do `page` para `show_dialog`, do `ctx` para sessão de banco. Passar o objeto completo é mais simples e flexível. |
| `CreateCategoryDialog.load_parents()` como método público async | Carregar no construtor | O construtor não pode ser async. Um método separado permite controle explícito do momento do carregamento. |
| `CreateCategoryDialog` importa `_flatten_tree_for_dropdown` de `category_list_view` | Mover para `category_service.py` | Acoplamento temporário aceito. Mover `_flatten_tree_for_dropdown` está fora do escopo. |
| Ambos dialogs em um único arquivo `category_dialogs.py` | Um arquivo por dialog | Os dialogs são pequenos (~40 e ~75 linhas) e semanticamente relacionados. Um arquivo reduz overhead de navegação. |

## Risks / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| Import circular se `category_dialogs.py` importar de `category_list_view.py` | O import é unidirecional (`category_dialogs` → `category_list_view._flatten_tree_for_dropdown`). Não há circularidade porque a view importa o dialog, que importa a view novamente — mas é um import de função, não de módulo no topo do arquivo do dialog, e `_flatten_tree_for_dropdown` não importa nada de volta. O risco é baixo, mas se quebrar, move-se `_flatten_tree_for_dropdown` para `category_service.py`. |
| `ctx.state.user.id` ser None | Adicionar guarda `user_id = (ctx.state.user.id or 0) if ctx.state.user else 0` nos dialogs se mypy reclamar. |
| Comportamento do dialog difere do original | Comparar linha por linha o código extraído com o original. Testar manualmente abrindo a view de categorias. |
