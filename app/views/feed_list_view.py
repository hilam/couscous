import asyncio

import flet as ft

from app.controls.add_feed_dialog import AddFeedDialog
from app.controls.confirm_dialog import ConfirmDialog
from app.controls.feed_card import FeedCard
from app.services.category_service import list_categories
from app.services.feed_service import add_feed, list_feeds, remove_feed
from app.services.refresh_service import refresh_all_feeds, refresh_single_feed


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


async def _rebuild_feed_list(feed_list, confirm_delete, session, page, user_id: int):
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


async def _handle_feed_added(  # noqa: PLR0913
    url: str,
    category_id: int | None,
    ctx,
    page: ft.Page,
    user_id: int,
    feed_list: ft.ListView,
    confirm_delete_cb,
) -> None:
    async with ctx.new_session() as s:
        try:
            feed = await add_feed(s, user_id, url, category_id)
        except ValueError:
            snack = ft.SnackBar(content=ft.Text("Feed j\u00e1 cadastrado"))
            page.overlay.append(snack)
            snack.open = True
            page.update()
            return

        await refresh_single_feed(s, feed)

        if feed.last_exception:
            snack = ft.SnackBar(content=ft.Text(f"Erro: {feed.last_exception}"))
            page.overlay.append(snack)
            snack.open = True
            page.update()
            await _rebuild_feed_list(feed_list, confirm_delete_cb, s, page, user_id)
            page.update()
            return

    await page.push_route(f"/feed/{url}")


async def _handle_feed_add_another(  # noqa: PLR0913
    url: str,
    category_id: int | None,
    ctx,
    page: ft.Page,
    user_id: int,
    feed_list: ft.ListView,
    confirm_delete_cb,
    state,
) -> bool:
    async with ctx.new_session() as s:
        try:
            feed = await add_feed(s, user_id, url, category_id)
        except ValueError:
            snack = ft.SnackBar(content=ft.Text("Feed j\u00e1 cadastrado"))
            page.overlay.append(snack)
            snack.open = True
            page.update()
            return False

        state.loading = True
        page.update()

        await refresh_single_feed(s, feed)

        if feed.last_exception:
            snack = ft.SnackBar(content=ft.Text(f"Erro: {feed.last_exception}"))
            page.overlay.append(snack)
            snack.open = True

        await _rebuild_feed_list(feed_list, confirm_delete_cb, s, page, user_id)

        state.loading = False
        page.update()
        return True


async def feed_list_view(ctx) -> ft.View:
    page = ctx.page
    state = ctx.state
    session = ctx.session
    user_id: int = (state.user.id or 0) if state.user else 0

    feeds = await list_feeds(session, user_id)
    categories = await list_categories(session, user_id)

    feed_list = ft.ListView(spacing=10, padding=10, expand=True)

    async def refresh(e):
        state.loading = True
        page.update()

        async with ctx.new_session() as s:
            await refresh_all_feeds(s, user_id)
            await _rebuild_feed_list(feed_list, confirm_delete, s, page, user_id)

        state.loading = False
        page.update()

    def on_feed_added(url, cid=None):
        _task_ref = asyncio.create_task(  # noqa: RUF006 - kept alive by parent scope
            _handle_feed_added(url, cid, ctx, page, user_id, feed_list, confirm_delete)
        )

    async def on_feed_add_another(url, cid=None):
        return await _handle_feed_add_another(
            url, cid, ctx, page, user_id, feed_list, confirm_delete, state
        )

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
        async with ctx.new_session() as s:
            await remove_feed(s, user_id, feed_url)
            await _rebuild_feed_list(feed_list, confirm_delete, s, page, user_id)
        page.update()

    init_controls = _build_group_controls(feeds, categories, confirm_delete, page)
    feed_list.controls.extend(init_controls if feeds else [_empty_state()])

    add_feed_dialog = AddFeedDialog(
        on_submit=on_feed_added,
        on_submit_another=on_feed_add_another,
        user_id=user_id,
    )

    def open_add_dialog(e):
        page.overlay.append(add_feed_dialog)
        add_feed_dialog.open = True
        _task_ref = asyncio.create_task(add_feed_dialog.load_categories())  # noqa: RUF006 - keep task alive
        page.update()

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
