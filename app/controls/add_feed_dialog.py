import asyncio

import flet as ft

from app.services.category_service import get_category_tree
from database.service.database import get_db_session


def _flatten_tree_for_dropdown(tree, options, level):
    for node in tree:
        prefix = "  " * level + "└ " if level > 0 else ""
        options.append(ft.dropdown.Option(str(node["id"]), f"{prefix}{node['name']}"))
        if node["children"]:
            _flatten_tree_for_dropdown(node["children"], options, level + 1)


class AddFeedDialog(ft.AlertDialog):
    def __init__(self, on_submit, user_id: int):
        super().__init__()
        self.on_submit = on_submit
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

        self.title = "Adicionar Feed"
        self.content = ft.Column(
            controls=[self.url_field, self.category_dropdown],
            width=350,
            height=160,
            tight=True,
        )
        self.actions = [
            ft.TextButton("Cancelar", on_click=self._cancel),
            ft.FilledButton("Adicionar", on_click=self._submit),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    async def load_categories(self):
        async with get_db_session() as session:
            tree = await get_category_tree(session, self.user_id)
        options = [ft.dropdown.Option("", "Sem categoria")]
        _flatten_tree_for_dropdown(tree, options, 0)
        self.category_dropdown.options = options
        self.category_dropdown.value = ""
        self.update()

    def _cancel(self, e):
        self.open = False
        self.url_field.value = ""
        self.category_dropdown.value = ""
        self.update()

    def _submit(self, e):
        url = self.url_field.value.strip()
        cat_val = self.category_dropdown.value
        category_id = int(cat_val) if cat_val and cat_val != "" else None
        if url:
            self.open = False
            self.url_field.value = ""
            self.category_dropdown.value = ""
            self.update()
            if self.on_submit:
                self._task = asyncio.ensure_future(self.on_submit(url, category_id))
