import flet as ft

from database.models.couscous import Feed


class FeedCard(ft.Card):
    def __init__(
        self,
        feed: Feed,
        on_click,
        on_delete,
    ):
        super().__init__()
        self.feed = feed
        self.on_click = on_click
        self.on_delete = on_delete

        title = feed.title or feed.url
        link = feed.link or ""

        self.content = ft.Container(
            content=ft.ListTile(
                leading=ft.Icon(ft.icons.RSS_FEED, color=ft.colors.CYAN_400),
                title=ft.Text(title, weight=ft.FontWeight.BOLD),
                subtitle=ft.Text(link, max_lines=1) if link else None,
                trailing=ft.IconButton(
                    ft.icons.DELETE_OUTLINE,
                    icon_color=ft.colors.RED_300,
                    on_click=lambda e: self._delete(e),
                ),
                on_click=lambda e: self._click(e),
            ),
            padding=ft.padding.all(4),
        )

    def _click(self, e):
        if self.on_click:
            self.on_click(e)

    def _delete(self, e):
        if self.on_delete:
            self.on_delete(e)
