import flet as ft

from app.controls.tag_chip import TagChip
from database.models.couscous import Entry

SUMMARY_MAX_LENGTH = 120


class ArticleCard(ft.Card):
    def __init__(self, entry: Entry, on_click, tags: list[str] | None = None):
        super().__init__()
        self.entry = entry
        self.on_click = on_click

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
            subtitle_controls.append(
                ft.Row(
                    controls=[TagChip(t) for t in tags],
                    spacing=4,
                    wrap=True,
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
