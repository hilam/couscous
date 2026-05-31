import asyncio

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
                    on_click=lambda _, eid=entry.id: asyncio.create_task(
                        page.push_route(f"/entry/{eid}")
                    ),
                )
            )
        page.update()

    for entry in entries:
        entry_list.controls.append(
            ArticleCard(
                entry=entry,
                on_click=lambda _, eid=entry.id: asyncio.create_task(
                    page.push_route(f"/entry/{eid}")
                ),
            )
        )

    if not entries:
        entry_list.controls.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.ARTICLE, size=60, color=ft.Colors.GREY_400),
                        ft.Text(
                            "Nenhum artigo encontrado",
                            theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                            color=ft.Colors.GREY,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.Alignment.CENTER,
                padding=ft.Padding.all(40),
            )
        )

    return ft.View(
        route=f"/feed/{feed_url}",
        navigation_bar=ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Início"),
                ft.NavigationBarDestination(icon=ft.Icons.RSS_FEED, label="Feeds"),
                ft.NavigationBarDestination(icon=ft.Icons.INFO, label="Sobre"),
            ],
            selected_index=1,
            on_change=lambda e: asyncio.create_task(
                page.push_route(
                    ["/feeds", "/feeds", "/about"][e.control.selected_index]
                )
            ),
        ),
        controls=[
            ft.AppBar(
                title=ft.Text(feed_title),
                bgcolor=ft.Colors.CYAN_50,
                actions=[
                    ft.Text(state.user.name if state.user else "", size=14),
                    ft.IconButton(ft.Icons.REFRESH, on_click=refresh),
                ],
            ),
            entry_list,
        ],
    )
