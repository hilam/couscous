import flet as ft

from database.models.couscous import Entry

SUMMARY_MAX_LENGTH = 120


class ArticleCard(ft.Card):
    def __init__(self, entry: Entry, on_click):
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

        self.content = ft.Container(
            content=ft.ListTile(
                leading=ft.Icon(
                    ft.icons.ARTICLE,
                    color=ft.colors.BLUE_400 if not entry.read else ft.colors.GREY_400,
                ),
                title=ft.Text(
                    title,
                    weight=ft.FontWeight.BOLD
                    if not entry.read
                    else ft.FontWeight.NORMAL,
                ),
                subtitle=ft.Column(
                    controls=[
                        ft.Text(subtitle, size=12) if subtitle else ft.Text(),
                        ft.Text(
                            (
                                summary[:SUMMARY_MAX_LENGTH] + "..."
                                if len(summary) > SUMMARY_MAX_LENGTH
                                else summary
                            ),
                            size=12,
                            color=ft.colors.GREY,
                            max_lines=2,
                        ),
                    ],
                ),
                on_click=lambda e: self._click(),
            ),
            padding=ft.padding.all(4),
        )

    def _click(self):
        if self.on_click:
            self.on_click(None)
