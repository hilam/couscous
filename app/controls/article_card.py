import asyncio

import flet as ft
from flet.controls.client_action import shared_service

from app.controls.tag_chip import TagChip
from database.models.couscous import Entry

SUMMARY_MAX_LENGTH = 120


MAX_VISIBLE_TAGS = 3


class ArticleCard(ft.Card):
    def __init__(
        self, entry: Entry, on_click, page: ft.Page, tags: list[str] | None = None
    ):
        super().__init__()
        self.entry = entry
        self.on_click = on_click
        self._copy_page = page

        title = entry.title or "(Sem título)"
        date_str = entry.published.strftime("%d/%m/%Y") if entry.published else ""
        summary = entry.summary or ""

        subtitle_parts = []
        if entry.author:
            subtitle_parts.append(entry.author)
        if date_str:
            subtitle_parts.append(date_str)

        subtitle = " | ".join(subtitle_parts)

        subtitle_controls: list[ft.Control] = []
        if subtitle:
            subtitle_controls.append(ft.Text(subtitle, size=12))
        if summary:
            subtitle_controls.append(
                ft.Text(
                    (
                        summary[:SUMMARY_MAX_LENGTH] + "..."
                        if len(summary) > SUMMARY_MAX_LENGTH
                        else summary
                    ),
                    size=12,
                    color=ft.Colors.GREY,
                    max_lines=2,
                ),
            )
        if tags:
            visible_tags = tags[:MAX_VISIBLE_TAGS]
            chips: list[ft.Control] = [TagChip(t) for t in visible_tags]
            extra = len(tags) - MAX_VISIBLE_TAGS
            if extra > 0:
                chips.append(
                    ft.Text(
                        f"+{extra} mais",
                        size=11,
                        color=ft.Colors.GREY_500,
                        italic=True,
                    )
                )
            subtitle_controls.append(
                ft.Row(
                    controls=chips,
                    spacing=4,
                    wrap=True,
                ),
            )

        # Copy link button (web-only, only if entry has a link)
        if entry.link and self._copy_page.web:
            subtitle_controls.insert(
                0,
                ft.Row(
                    controls=[
                        ft.IconButton(
                            ft.Icons.CONTENT_COPY,
                            icon_size=16,
                            tooltip="Copiar link",
                            on_click=lambda e: asyncio.create_task(self._copy_link()),
                        ),
                    ],
                    spacing=0,
                ),
            )

        self.content = ft.Container(
            content=ft.ListTile(
                leading=ft.Icon(
                    ft.Icons.ARTICLE,
                    color=ft.Colors.BLUE_400 if not entry.read else ft.Colors.GREY_400,
                ),
                title=ft.Text(
                    title,
                    weight=ft.FontWeight.BOLD
                    if not entry.read
                    else ft.FontWeight.NORMAL,
                ),
                subtitle=ft.Column(
                    controls=subtitle_controls,
                ),
                on_click=lambda e: self._click(),
            ),
            padding=ft.Padding.all(4),
        )

    def _click(self):
        if self.on_click:
            self.on_click(None)

    async def _copy_link(self):
        url = self.entry.link or ""
        if not url:
            return
        await shared_service(ft.Clipboard).set(url)
        self._copy_page.show_dialog(ft.SnackBar(content=ft.Text("Link copiado!")))
        self._copy_page.update()
