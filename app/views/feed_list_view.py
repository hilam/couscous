import flet as ft

from app.controls.add_feed_dialog import AddFeedDialog
from app.controls.confirm_dialog import ConfirmDialog
from app.controls.feed_card import FeedCard
from app.db import get_db_session
from app.services.feed_service import add_feed, list_feeds, remove_feed
from app.services.refresh_service import refresh_all_feeds
from app.state import State


async def feed_list_view(page: ft.Page, state: State) -> ft.View:
    async with get_db_session() as session:
        feeds = await list_feeds(session)

    feed_list = ft.ListView(spacing=10, padding=10, expand=True)

    async def refresh(e):
        state.loading = True
        page.update()

        async with get_db_session() as session:
            await refresh_all_feeds(session)

        async with get_db_session() as session:
            feeds = await list_feeds(session)

        feed_list.controls.clear()
        for feed in feeds:
            feed_list.controls.append(
                FeedCard(
                    feed=feed,
                    on_click=lambda _, url=feed.url: page.go(f"/feed/{url}"),
                    on_delete=lambda _, url=feed.url: confirm_delete(url),
                )
            )
        state.loading = False
        page.update()

    async def on_feed_added(url: str):
        async with get_db_session() as session:
            try:
                await add_feed(session, url)
            except ValueError:
                page.show_snack_bar(ft.SnackBar(content=ft.Text("Feed já cadastrado")))
                return

        async with get_db_session() as session:
            feeds = await list_feeds(session)

        feed_list.controls.clear()
        for feed in feeds:
            feed_list.controls.append(
                FeedCard(
                    feed=feed,
                    on_click=lambda _, url=feed.url: page.go(f"/feed/{url}"),
                    on_delete=lambda _, url=feed.url: confirm_delete(url),
                )
            )
        page.update()

    def confirm_delete(feed_url: str):
        dlg = ConfirmDialog(
            title="Remover feed",
            message="Tem certeza que deseja remover este feed?",
            on_confirm=lambda e: delete_feed(feed_url),
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    async def delete_feed(feed_url: str):
        async with get_db_session() as session:
            await remove_feed(session, feed_url)

        async with get_db_session() as session:
            feeds = await list_feeds(session)

        feed_list.controls.clear()
        for feed in feeds:
            feed_list.controls.append(
                FeedCard(
                    feed=feed,
                    on_click=lambda _, url=feed.url: page.go(f"/feed/{url}"),
                    on_delete=lambda _, url=feed.url: confirm_delete(url),
                )
            )
        page.dialog.open = False
        page.update()

    for feed in feeds:
        feed_list.controls.append(
            FeedCard(
                feed=feed,
                on_click=lambda _, url=feed.url: page.go(f"/feed/{url}"),
                on_delete=lambda _, url=feed.url: confirm_delete(url),
            )
        )

    if not feeds:
        feed_list.controls.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.icons.RSS_FEED, size=60, color=ft.colors.GREY_400),
                        ft.Text(
                            "Nenhum feed adicionado",
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

    add_feed_dialog = AddFeedDialog(on_submit=on_feed_added)

    def open_add_dialog(e):
        page.dialog = add_feed_dialog
        add_feed_dialog.open = True
        page.update()

    return ft.View(
        route="/feeds",
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
                title=ft.Text("Meus Feeds"),
                bgcolor=ft.colors.CYAN_50,
                actions=[
                    ft.Text(state.user.name if state.user else "", size=14),
                    ft.IconButton(ft.icons.REFRESH, on_click=refresh),
                    ft.IconButton(ft.icons.ADD, on_click=open_add_dialog),
                ],
            ),
            ft.Stack(
                controls=[
                    feed_list,
                    ft.Container(
                        content=ft.ProgressRing(),
                        visible=state.loading,
                        alignment=ft.alignment.center,
                    ),
                ],
                expand=True,
            ),
        ],
    )
