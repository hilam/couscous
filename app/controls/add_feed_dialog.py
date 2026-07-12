import asyncio

import flet as ft

from app.services.category_service import get_categories_with_counts
from database.service.database import get_db_session


class AddFeedDialog(ft.AlertDialog):
    def __init__(self, on_submit, user_id: int, on_submit_another=None):
        super().__init__()
        self.on_submit = on_submit
        self.on_submit_another = on_submit_another
        self.user_id = user_id

        self.url_field = ft.TextField(
            label="URL do Feed RSS",
            hint_text="https://exemplo.com/feed.xml",
            autofocus=True,
            expand=True,
        )

        self.category_dropdown = ft.Dropdown(
            label="Categoria (opcional)",
            expand=True,
        )

        self.url_field.on_submit = lambda e: asyncio.create_task(
            self.category_dropdown.focus()
        )

        self.title = "Adicionar Feed"
        self.content = ft.Column(
            controls=[self.url_field, self.category_dropdown],
            width=350,
            height=160,
            tight=True,
        )
        self.actions = [
            ft.TextButton("Cancelar", on_click=self._cancel),
            ft.FilledButton("Adicionar outro", on_click=self._submit_another),
            ft.FilledButton("Adicionar", on_click=self._submit),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    async def load_categories(self):
        async with get_db_session() as session:
            cats, _, _ = await get_categories_with_counts(session, self.user_id)
        options = [ft.dropdown.Option("", "Sem categoria")] + [
            ft.dropdown.Option(str(c.id), c.name) for c in cats
        ]
        self.category_dropdown.options = options
        self.category_dropdown.value = ""
        self.update()

    def _cancel(self, e):
        self.open = False
        self.url_field.value = ""
        self.category_dropdown.value = ""
        self.update()

    def _do_submit(self):
        url = self.url_field.value.strip()
        if not url:
            return None, None
        cat_val = self.category_dropdown.value
        category_id = int(cat_val) if cat_val and cat_val != "" else None
        return url, category_id

    def _submit(self, e):
        url, category_id = self._do_submit()
        if url:
            self.open = False
            self.url_field.value = ""
            self.category_dropdown.value = ""
            self.update()
            if self.on_submit:
                self._task = asyncio.create_task(self.on_submit(url, category_id))

    async def _submit_another(self, e):
        url, category_id = self._do_submit()
        if not url:
            return
        if self.on_submit_another:
            success = await self.on_submit_another(url, category_id)
            if success:
                self.url_field.value = ""
                self.url_field.update()
                await self.url_field.focus()
        self.update()
