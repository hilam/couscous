"""Dialog controls for category management."""

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
                content=ft.Text("Categoria j\u00e1 existe neste n\u00edvel")
            )
            self._page.overlay.append(snack)
            snack.open = True
            self._page.update()
            return
        await self._refresh_cb()
