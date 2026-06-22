import asyncio

import flet as ft

from app.controls.add_feed_dialog import AddFeedDialog
from app.controls.confirm_dialog import ConfirmDialog
from app.controls.feed_card import FeedCard
from app.controls.nav_bar import set_navbar
from app.services.category_service import list_categories
from app.services.feed_service import add_feed, list_feeds, remove_feed
from app.services.refresh_service import refresh_all_feeds, refresh_single_feed
from app.state import State
from database.service.database import get_db_session


def _build_feed_card(feed, confirm_delete, page):
    return FeedCard(
        feed=feed,
        on_click=lambda _, url=feed.url: asyncio.create_task(
            page.push_route(f"/feed/{url}")
        ),
        on_delete=lambda _, url=feed.url: confirm_delete(url),
    )


def _build_group_controls(feeds, categories, confirm_delete, page):
    cat_map = {c.id: c.name for c in categories}
    grouped: dict[int | None, list] = {}
    for feed in feeds:
        grouped.setdefault(feed.category_id, []).append(feed)

    controls = []
    cat_ids = sorted(
        [cid for cid in grouped if cid is not None],
        key=lambda cid: cat_map.get(cid, "").lower(),
    )

    for cid in cat_ids:
        cat_name = cat_map.get(cid, "Categoria")
        controls.append(
            ft.Container(
                content=ft.Text(
                    cat_name,
                    theme_style=ft.TextThemeStyle.TITLE_SMALL,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.CYAN_700,
                ),
                padding=ft.Padding(left=10, top=10, right=10, bottom=2),
            )
        )
        controls.extend(
            _build_feed_card(feed, confirm_delete, page) for feed in grouped[cid]
        )

    if None in grouped:
        controls.append(
            ft.Container(
                content=ft.Text(
                    "Sem categoria",
                    theme_style=ft.TextThemeStyle.TITLE_SMALL,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREY_600,
                ),
                padding=ft.Padding(left=10, top=10, right=10, bottom=2),
            )
        )
        controls.extend(
            _build_feed_card(feed, confirm_delete, page) for feed in grouped[None]
        )

    return controls


def _empty_state():
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.RSS_FEED, size=60, color=ft.Colors.GREY_400),
                ft.Text(
                    "Nenhum feed adicionado",
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


async def _rebuild_feed_list(feed_list, confirm_delete, page, user_id: int):
    async with get_db_session() as session:
        feeds = await list_feeds(session, user_id)
        categories = await list_categories(session, user_id)
    feed_list.controls.clear()
    if feeds:
        feed_list.controls.extend(
            _build_group_controls(feeds, categories, confirm_delete, page)
        )
    else:
        feed_list.controls.append(_empty_state())
    return feeds


async def feed_list_view(page: ft.Page, state: State) -> ft.View:
    user_id: int = (state.user.id or 0) if state.user else 0

    async with get_db_session() as session:
        feeds = await list_feeds(session, user_id)
        categories = await list_categories(session, user_id)

    feed_list = ft.ListView(spacing=10, padding=10, expand=True)

    async def refresh(e):
        state.loading = True
        page.update()

        async with get_db_session() as session:
            await refresh_all_feeds(session, user_id)

        await _rebuild_feed_list(feed_list, confirm_delete, page, user_id)
        state.loading = False
        page.update()

    async def on_feed_added(url: str, category_id: int | None = None):
        async with get_db_session() as session:
            try:
                feed = await add_feed(session, user_id, url, category_id)
            except ValueError:
                snack = ft.SnackBar(content=ft.Text("Feed j\u00e1 cadastrado"))
                page.overlay.append(snack)
                snack.open = True
                page.update()
                return

            await refresh_single_feed(session, feed)

            if feed.last_exception:
                snack = ft.SnackBar(content=ft.Text(f"Erro: {feed.last_exception}"))
                page.overlay.append(snack)
                snack.open = True
                page.update()
                await _rebuild_feed_list(feed_list, confirm_delete, page, user_id)
                page.update()
                return

        await page.push_route(f"/feed/{url}")

    def confirm_delete(feed_url: str):
        dlg: ft.AlertDialog = ConfirmDialog(
            title="Remover feed",
            message="Tem certeza que deseja remover este feed?",
            on_confirm=lambda e: delete_feed(feed_url, dlg),
        )
        page.show_dialog(dlg)
        page.update()

    async def delete_feed(feed_url: str, dlg: ft.AlertDialog):
        dlg.open = False
        page.update()
        async with get_db_session() as session:
            await remove_feed(session, user_id, feed_url)

        await _rebuild_feed_list(feed_list, confirm_delete, page, user_id)
        page.update()

    init_controls = _build_group_controls(feeds, categories, confirm_delete, page)
    feed_list.controls.extend(init_controls if feeds else [_empty_state()])

    add_feed_dialog = AddFeedDialog(on_submit=on_feed_added, user_id=user_id)

    def open_add_dialog(e):
        page.overlay.append(add_feed_dialog)
        add_feed_dialog.open = True
        _task_ref = asyncio.create_task(add_feed_dialog.load_categories())  # noqa: RUF006 - keep task alive
        page.update()

    set_navbar(page)
    return ft.View(
        route="/feeds",
        controls=[
            ft.AppBar(
                title=ft.Text("Meus Feeds"),
                bgcolor=ft.Colors.CYAN_50,
                actions=[
                    ft.Text(state.user.name if state.user else "", size=14),
                    ft.IconButton(ft.Icons.REFRESH, on_click=refresh),
                    ft.IconButton(ft.Icons.ADD, on_click=open_add_dialog),
                ],
            ),
            ft.Stack(
                controls=[
                    feed_list,
                    ft.Container(
                        content=ft.ProgressRing(),
                        visible=state.loading,
                        alignment=ft.Alignment.CENTER,
                    ),
                ],
                expand=True,
            ),
        ],
    )
