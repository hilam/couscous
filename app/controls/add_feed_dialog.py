import asyncio

import flet as ft


class AddFeedDialog(ft.AlertDialog):
    def __init__(self, on_submit):
        super().__init__()
        self.on_submit = on_submit
        self.url_field = ft.TextField(
            label="URL do Feed RSS",
            hint_text="https://exemplo.com/feed.xml",
            autofocus=True,
            expand=True,
        )

        self.title = "Adicionar Feed"
        self.content = ft.Column(
            controls=[self.url_field],
            width=350,
            height=100,
        )
        self.actions = [
            ft.TextButton("Cancelar", on_click=self._cancel),
            ft.FilledButton("Adicionar", on_click=self._submit),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def _cancel(self, e):
        self.open = False
        self.url_field.value = ""
        self.update()

    def _submit(self, e):
        url = self.url_field.value.strip()
        if url:
            self.open = False
            self.url_field.value = ""
            self.update()
            if self.on_submit:
                self._task = asyncio.ensure_future(self.on_submit(url))
