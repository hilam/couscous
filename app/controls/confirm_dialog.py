import asyncio

import flet as ft


class ConfirmDialog(ft.AlertDialog):
    def __init__(self, title: str, message: str, on_confirm):
        super().__init__()
        self.on_confirm = on_confirm
        self.title = title
        self.content = ft.Text(message)
        self.actions = [
            ft.TextButton("Cancelar", on_click=self._cancel),
            ft.FilledButton("Confirmar", on_click=self._confirm),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def _cancel(self, e):
        self.open = False
        self.update()

    def _confirm(self, e):
        self.open = False
        self.update()
        if self.on_confirm:
            self._task = asyncio.create_task(self.on_confirm(e))
