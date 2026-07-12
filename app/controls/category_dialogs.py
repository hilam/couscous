"""Dialog controls for category management."""

import asyncio

import flet as ft

from app.services.category_service import create_category, rename_category


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
                content=ft.Text("Categoria j\u00e1 existe neste n\u00edvel")
            )
            self._page.overlay.append(snack)
            snack.open = True
            self._page.update()
            return
        await self._refresh_cb()


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
        from app.services.category_service import (
            build_category_tree,
            get_categories_with_counts,
        )
        from app.views.category_list_view import _flatten_tree_for_dropdown

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
                snack = ft.SnackBar(content=ft.Text("Categoria já existe neste nível"))
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
