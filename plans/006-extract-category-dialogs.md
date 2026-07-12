# Plano 006: Extrair dialogs de `category_list_view.py` para controles dedicados

> **Instruções ao executor**: Siga este plano passo a passo. Execute todo
> comando de verificação e confirme o resultado esperado antes de passar para
> o próximo passo. Se algo na seção "Condições STOP" ocorrer, pare e reporte
> — não improvise. Quando terminar, atualize a linha de status deste plano
> em `plans/README.md`.
>
> **Verificação de deriva (execute primeiro)**: `git diff --stat c24a31f..HEAD -- app/views/category_list_view.py app/controls/`
> Se qualquer arquivo no escopo mudou desde que este plano foi escrito,
> compare os excertos de "Estado atual" contra o código vivo antes de
> prosseguir; em caso de incompatibilidade, trate como condição STOP.

## Status

- **Prioridade**: P3
- **Esforço**: M
- **Risco**: MÉDIO
- **Depende de**: plano 005 (extrair _build_tree) — recomenda-se executar 005 primeiro para reduzir o código movido
- **Categoria**: tech-debt
- **Planejado em**: commit `c24a31f`, 2026-07-12

## Por que isso é importante

`category_list_view.py` tem 341 linhas e é a segunda maior view do projeto (atrás de explore_view.py com 425). Contém dois dialogs inline com lógica de validação e callbacks assíncronos embutidos na view:

1. `_build_create_dialog()` — 45 linhas criando um `ft.AlertDialog` com campo de nome, dropdown de categoria pai, validação de duplicata.
2. `_build_rename_dialog()` — 30 linhas criando um `ft.AlertDialog` com campo de nome e validação.

Extrair esses dialogs para `app/controls/` segue o padrão já existente no projeto: `AddFeedDialog` está em `app/controls/add_feed_dialog.py`, `ConfirmDialog` em `app/controls/confirm_dialog.py`. A view fica mais enxuta e os dialogs ficam isolados, testáveis e reutilizáveis.

## Estado atual

`app/views/category_list_view.py` contém três builders de dialog inline:

**`_build_create_dialog(page, refresh_cb, ctx)`** (~linhas 152-226):
- Cria `name_field` (TextField) + `parent_dropdown` (Dropdown)
- Carrega categorias async via `_load_parent_dropdown()`
- Callback `_do_create()` chama `create_category()` com `ctx.open_session()`
- Callback `_submit_and_close()` também chama `refresh_cb()`
- Callback `_submit_and_continue()` limpa campo e refoca
- Botões: Cancelar, Criar outro, Criar

**`_build_rename_dialog(node, page, refresh_cb, ctx)`** (~linhas 253-293):
- Cria `name_field` (TextField) com valor preenchido do nó
- Callback `_submit()` chama `rename_category()` com `ctx.open_session()`
- Botões: Cancelar, Renomear

Arquivos de controle existentes como referência:
- `app/controls/add_feed_dialog.py` — padrão a seguir: classe que herda de `ft.AlertDialog`, recebe callbacks no `__init__`, tem método `_cancel` e `_submit`.
- `app/controls/confirm_dialog.py` — mais simples, também herda `ft.AlertDialog`.

Convenções do repositório:
- Controles em `app/controls/` são classes que herdam de controles Flet (`ft.AlertDialog`, `ft.Card`, `ft.Container`).
- Callbacks assíncronos são disparados via `asyncio.create_task()`.
- Sessões de banco são abertas via `ctx.open_session()` (ADR-0003).
- Nomes de arquivo: `snake_case.py`.

## Comandos que você vai precisar

| Propósito | Comando | Esperado em caso de sucesso |
|-----------|---------|------------------------------|
| Typecheck | `make typecheck` | "Success: no issues found" |
| Lint | `make lint` | "All checks passed!" |
| Testes | `make test` | sem novas falhas |

## Escopo

**No escopo**:
- `app/controls/category_dialogs.py` — criar, com `CreateCategoryDialog` e `RenameCategoryDialog`
- `app/views/category_list_view.py` — remover builders inline, substituir por imports

**Fora de escopo** (NÃO toque):
- `app/controls/add_feed_dialog.py` — referência de padrão, não modificar
- `app/views/explore_view.py` — não usa estes dialogs
- A lógica de `_flatten_tree_for_dropdown` — permanece em category_list_view.py (é específica do dropdown)
- `_build_tree_controls` — permanece na view (é renderização, não dialog)

## Fluxo git

- Branch: `advisor/006-extract-category-dialogs`
- Commits:
  - `refactor: extrai CreateCategoryDialog para app/controls/category_dialogs.py`
  - `refactor: extrai RenameCategoryDialog para app/controls/category_dialogs.py`
  - `refactor: remove dialogs inline de category_list_view.py`
- NÃO faça push ou abra PR a menos que o operador o instrua.

## Passos

### Passo 1: Criar `app/controls/category_dialogs.py` com `RenameCategoryDialog`

Comece pelo dialog mais simples. Crie `app/controls/category_dialogs.py`:

```python
"""Dialog controls for category management."""

import asyncio

import flet as ft

from app.services.category_service import rename_category


class RenameCategoryDialog(ft.AlertDialog):
    """Dialog to rename an existing category."""

    def __init__(self, node: dict, page: ft.Page, refresh_cb, ctx):
        super().__init__()
        self._node = node
        self._page = page
        self._refresh_cb = refresh_cb
        self._ctx = ctx

        self._name_field = ft.TextField(
            label="Novo nome",
            value=node["name"],
            autofocus=True,
            expand=True,
        )
        self._name_field.on_submit = self._submit

        self.title = ft.Text("Renomear Categoria")
        self.content = ft.Column(
            controls=[self._name_field],
            width=300,
            tight=True,
        )
        self.actions = [
            ft.TextButton("Cancelar", on_click=self._cancel),
            ft.FilledButton("Renomear", on_click=self._submit),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def _cancel(self, e):
        self.open = False
        self.update()

    async def _submit(self, e):
        new_name = self._name_field.value.strip()
        if not new_name:
            return
        self.open = False
        self.update()
        try:
            async with self._ctx.open_session() as s:
                await rename_category(
                    s, self._ctx.state.user.id, self._node["id"], new_name
                )
        except ValueError:
            snack = ft.SnackBar(
                content=ft.Text("Categoria já existe neste nível")
            )
            self._page.overlay.append(snack)
            snack.open = True
            self._page.update()
            return
        await self._refresh_cb()
```

**Verificar**: `make typecheck` → "Success: no issues found".

### Passo 2: Adicionar `CreateCategoryDialog` em `category_dialogs.py`

Adicione a segunda classe ao mesmo arquivo. Siga o padrão de `AddFeedDialog` (herda `ft.AlertDialog`, recebe callbacks no init, carrega dados async):

```python
class CreateCategoryDialog(ft.AlertDialog):
    """Dialog to create a new category with optional parent."""

    def __init__(self, page: ft.Page, refresh_cb, ctx):
        super().__init__()
        self._page = page
        self._refresh_cb = refresh_cb
        self._ctx = ctx

        self._name_field = ft.TextField(
            label="Nome da categoria",
            autofocus=True,
            expand=True,
        )
        self._parent_dropdown = ft.Dropdown(
            label="Categoria pai",
            expand=True,
        )

        self._name_field.on_submit = lambda e: asyncio.create_task(
            self._parent_dropdown.focus()
        )

        self.title = ft.Text("Nova Categoria")
        self.content = ft.Column(
            controls=[self._name_field, self._parent_dropdown],
            width=350,
            tight=True,
        )
        self.actions = [
            ft.TextButton("Cancelar", on_click=self._cancel),
            ft.FilledButton("Criar outro", on_click=self._submit_and_continue),
            ft.FilledButton("Criar", on_click=self._submit_and_close),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    async def load_parents(self):
        """Load parent category options for the dropdown."""
        from app.services.category_service import get_categories_with_counts
        from app.views.category_list_view import _flatten_tree_for_dropdown
        from app.services.category_service import build_category_tree

        async with self._ctx.open_session() as s:
            cats, _, _ = await get_categories_with_counts(s, self._ctx.state.user.id)

        tree = build_category_tree(cats) if cats else []
        options = [ft.dropdown.Option("0", "Nenhuma (raiz)")]
        _flatten_tree_for_dropdown(tree, options, 0)
        self._parent_dropdown.options = options
        self._parent_dropdown.value = "0"
        self._page.update()

    def _cancel(self, e):
        self.open = False
        self.update()

    async def _do_create(self) -> bool:
        name = self._name_field.value.strip()
        if not name:
            return False
        raw = self._parent_dropdown.value
        parent_id = int(raw) if raw and raw != "0" else None
        async with self._ctx.open_session() as s:
            try:
                await create_category(s, self._ctx.state.user.id, name, parent_id)
            except ValueError:
                snack = ft.SnackBar(
                    content=ft.Text("Categoria já existe neste nível")
                )
                self._page.overlay.append(snack)
                snack.open = True
                self._page.update()
                return False
            else:
                return True

    async def _submit_and_close(self, e):
        self.open = False
        self.update()
        if await self._do_create():
            await self._refresh_cb()

    async def _submit_and_continue(self, e):
        if not await self._do_create():
            return
        self._name_field.value = ""
        self._name_field.update()
        await self.load_parents()
        await self._refresh_cb()
        await self._name_field.focus()
```

Adicione o import de `create_category`:
```python
from app.services.category_service import create_category, rename_category
```

**Verificar**: `make typecheck` → "Success: no issues found". `make lint` → "All checks passed!".

### Passo 3: Atualizar `category_list_view.py` para usar os novos dialogs

Substitua as chamadas inline pelos imports:

No topo do arquivo, adicione:
```python
from app.controls.category_dialogs import CreateCategoryDialog, RenameCategoryDialog
```

Na função `category_list_view()`, substitua:

1. `_open_rename_dialog(node)` — em vez de chamar `_build_rename_dialog(...)`, crie e mostre o dialog:
```python
    async def _open_rename_dialog(node):
        dlg = RenameCategoryDialog(node, page, refresh_tree, ctx)
        page.show_dialog(dlg)
        page.update()
```

2. `open_new_dialog(e)` — em vez de chamar `_build_create_dialog(...)`, crie, carregue e mostre:
```python
    async def open_new_dialog(e):
        create_dlg = CreateCategoryDialog(page, refresh_tree, ctx)
        page.overlay.append(create_dlg)
        create_dlg.open = True
        await create_dlg.load_parents()
        page.update()
```

Remova as funções `_build_create_dialog()` e `_build_rename_dialog()` do arquivo (linhas ~152-293).

**Verificar**: `make typecheck` → "Success: no issues found". `make lint` → "All checks passed!".

### Passo 4: Verificação final

```bash
make typecheck
# Esperado: "Success: no issues found"

make lint
# Esperado: "All checks passed!"

make test
# Esperado: sem novas falhas (os 12 testes quebrados do plano 002 podem continuar falhando)

grep -c "def _build_create_dialog\|def _build_rename_dialog" app/views/category_list_view.py
# Esperado: 0 (funções removidas)

wc -l app/views/category_list_view.py
# Esperado: significativamente menos que 341
```

## Plano de testes

Nenhum novo teste neste plano. A extração é puramente estrutural — move código de um arquivo para outro sem alterar comportamento. Os testes de view existentes (que testam `category_list_view`) continuam passando ou falhando da mesma forma.

Se o plano 002 (corrigir testes de view) já foi executado, os testes de view podem validar indiretamente que os dialogs funcionam.

## Critérios de conclusão

- [ ] `app/controls/category_dialogs.py` existe com `CreateCategoryDialog` e `RenameCategoryDialog`
- [ ] `_build_create_dialog` e `_build_rename_dialog` foram removidas de `category_list_view.py`
- [ ] `category_list_view.py` importa e usa `CreateCategoryDialog` e `RenameCategoryDialog`
- [ ] `make typecheck` → "Success: no issues found"
- [ ] `make lint` → "All checks passed!"
- [ ] Nenhum arquivo fora da lista de escopo foi modificado

## Condições STOP

Pare e reporte (não improvise) se:

- `_flatten_tree_for_dropdown` não está acessível de `category_list_view.py` (ela é importada pelo novo dialog). Se o import `from app.views.category_list_view import _flatten_tree_for_dropdown` falhar por import circular, mova `_flatten_tree_for_dropdown` para `category_service.py` também.
- `make typecheck` reporta erro sobre `ctx.state.user.id` ser potencialmente None — adicione a guarda `user_id: int = (ctx.state.user.id or 0) if ctx.state.user else 0` no dialog.
- O comportamento do dialog de criação (submit, cancel, criar outro) difere do original — teste manualmente abrindo a view de categorias e criando/renomeando uma categoria.

## Notas de manutenção

- `CreateCategoryDialog.load_parents()` importa `_flatten_tree_for_dropdown` de `category_list_view.py` — um acoplamento temporário. Idealmente `_flatten_tree_for_dropdown` seria movida para `category_service.py` também, mas isso está fora do escopo deste plano.
- Se novos dialogs de categoria forem adicionados (ex: mover categoria, reordenar), eles devem ir em `category_dialogs.py`, não em `category_list_view.py`.
- O padrão de receber `page`, `refresh_cb` e `ctx` no construtor é intencional — mantém os dialogs independentes de estado global e fáceis de testar com mocks.
