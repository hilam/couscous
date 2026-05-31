import flet as ft

from app.controls.article_card import ArticleCard
from app.db import get_db_session
from app.services.entry_service import list_entries
from app.state import State


async def entry_list_view(page: ft.Page, state: State) -> ft.View:
    feed_url = state.active_feed_url or ""

    async with get_db_session() as session:
        from sqlmodel import select

        from database.models.couscous import Feed

        result = await session.execute(select(Feed).where(Feed.url == feed_url))
        feed = result.scalar_one_or_none()

    feed_title = feed.title if feed and feed.title else feed_url

    async with get_db_session() as session:
        entries = await list_entries(session, feed_url)

    entry_list = ft.ListView(spacing=8, padding=10, expand=True)

    async def refresh(e):
        async with get_db_session() as session:
            entries = await list_entries(session, feed_url)
        entry_list.controls.clear()
        for entry in entries:
            entry_list.controls.append(
                ArticleCard(
                    entry=entry,
                    on_click=lambda _, eid=entry.id: page.go(f"/entry/{eid}"),
                )
            )
        page.update()

    for entry in entries:
        entry_list.controls.append(
            ArticleCard(
                entry=entry,
                on_click=lambda _, eid=entry.id: page.go(f"/entry/{eid}"),
            )
        )

    if not entries:
        entry_list.controls.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.icons.ARTICLE, size=60, color=ft.colors.GREY_400),
                        ft.Text(
                            "Nenhum artigo encontrado",
                            style=ft.TextThemeStyle.TITLE_MEDIUM,
                            color=ft.colors.GREY,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
                padding=ft.padding.all(40),
            )
        )

    return ft.View(
        route=f"/feed/{feed_url}",
        navigation_bar=ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=ft.icons.HOME, label="Início"),
                ft.NavigationDestination(icon=ft.icons.RSS_FEED, label="Feeds"),
                ft.NavigationDestination(icon=ft.icons.INFO, label="Sobre"),
            ],
            selected_index=1,
            on_change=lambda e: page.go(
                ["/feeds", "/feeds", "/about"][e.control.selected_index]
            ),
        ),
        controls=[
            ft.AppBar(
                title=ft.Text(feed_title),
                bgcolor=ft.colors.CYAN_50,
                actions=[
                    ft.Text(state.user.name if state.user else "", size=14),
                    ft.IconButton(ft.icons.REFRESH, on_click=refresh),
                ],
            ),
            entry_list,
        ],
    )
