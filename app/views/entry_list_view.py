import asyncio

import flet as ft

from app.controls.article_card import ArticleCard
from app.services.entry_service import list_entries
from app.services.feed_service import get_feed
from app.services.tag_service import get_distinct_tags_for_feed, get_tags_for_entries

PAGE_SIZE = 50


def _empty_state() -> ft.Container:
    return ft.Container(
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


def _filter_chip(label: str, on_click, *, selected: bool = False) -> ft.Chip:  # noqa: FBT001
    chip = ft.Chip(
        label=ft.Text(label, size=12),
        on_click=on_click,
    )
    if selected:
        chip.bgcolor = ft.Colors.CYAN_100
    return chip


def _build_article_card(entry, page, tags: list[str] | None = None) -> ArticleCard:
    return ArticleCard(
        entry=entry,
        tags=tags,
        page=page,
        on_click=lambda _, eid=entry.id: asyncio.create_task(
            page.push_route(f"/entry/{eid}")
        ),
    )


def _populate_entry_list(
    entry_list: ft.ListView,
    entries: list,
    page: ft.Page,
    tag_map: dict[int, list[str]],
):
    entry_list.controls.clear()
    for entry in entries:
        tags = tag_map.get(entry.id, []) if entry.id else None
        entry_list.controls.append(_build_article_card(entry, page, tags))
    if not entries:
        entry_list.controls.append(_empty_state())


async def entry_list_view(ctx) -> ft.View:  # noqa: C901, PLR0915
    page = ctx.page
    state = ctx.state
    session = ctx.session
    feed_url = state.active_feed_url or ""
    user_id: int = (state.user.id or 0) if state.user else 0

    feed = await get_feed(session, feed_url, user_id)
    feed_title = feed.title if feed and feed.title else feed_url

    entries = await list_entries(
        session,
        feed_url,
        user_id=user_id,
        before=None,
        before_id=None,
        limit=PAGE_SIZE,
    )

    entry_list = ft.ListView(spacing=8, padding=10, expand=True)
    show_unread = False
    show_important = False
    active_tag: str | None = None
    cursor: tuple | None = (
        (entries[-1].published, entries[-1].id) if entries else None
    )
    has_more = len(entries) == PAGE_SIZE
    loading_more = False

    feed_tags = await get_distinct_tags_for_feed(session, feed_url, user_id)

    tag_filter_row = ft.Row(controls=[], spacing=4, wrap=True)

    def build_tag_filter_row():
        tag_filter_row.controls.clear()
        for t in feed_tags:
            is_selected = active_tag == t
            label = f"#{t}" if not is_selected else f"#{t} ✕"
            tag_filter_row.controls.append(
                _filter_chip(label, make_toggle_tag(t), selected=is_selected)
            )

    def make_toggle_tag(tag: str):
        async def handler(e):
            nonlocal active_tag
            active_tag = None if active_tag == tag else tag
            build_tag_filter_row()
            await refresh(None)

        return handler

    build_tag_filter_row()

    async def load_entries():
        before, before_id = cursor if cursor is not None else (None, None)
        async with ctx.open_session() as s:
            return await list_entries(
                s,
                feed_url,
                user_id=user_id,
                unread_only=show_unread,
                important_only=show_important,
                tag=active_tag,
                before=before,
                before_id=before_id,
                limit=PAGE_SIZE,
            )

    def _advance_cursor(new_entries):
        nonlocal cursor, has_more
        has_more = len(new_entries) == PAGE_SIZE
        if new_entries:
            cursor = (new_entries[-1].published, new_entries[-1].id)

    async def refresh(e):
        nonlocal cursor, has_more, loading_more
        cursor = None
        has_more = True
        loading_more = False
        entries = await load_entries()
        _advance_cursor(entries)
        async with ctx.open_session() as s:
            tag_map = await get_tags_for_entries(
                s, [entry.id for entry in entries if entry.id is not None], user_id
            )
        _populate_entry_list(entry_list, entries, page, tag_map)
        page.update()

    async def load_more():
        nonlocal loading_more
        if loading_more or not has_more:
            return
        loading_more = True
        try:
            entries = await load_entries()
            _advance_cursor(entries)
            async with ctx.open_session() as s:
                tag_map = await get_tags_for_entries(
                    s,
                    [entry.id for entry in entries if entry.id is not None],
                    user_id,
                )
            for entry in entries:
                tags = tag_map.get(entry.id, []) if entry.id else None
                entry_list.controls.append(_build_article_card(entry, page, tags))
            page.update()
        finally:
            loading_more = False

    def on_scroll(e):
        if e.event_type == ft.ScrollType.END and has_more:
            asyncio.create_task(load_more())  # noqa: RUF006

    entry_list.on_scroll = on_scroll

    async def toggle_unread(e):
        nonlocal show_unread
        show_unread = not show_unread
        await refresh(e)

    async def toggle_important(e):
        nonlocal show_important
        show_important = not show_important
        await refresh(e)

    tag_map = await get_tags_for_entries(
        session, [entry.id for entry in entries if entry.id is not None], user_id
    )
    _populate_entry_list(entry_list, entries, page, tag_map)

    return ft.View(
        route=f"/feed/{feed_url}",
        controls=[
            ft.AppBar(
                leading=ft.IconButton(
                    ft.Icons.ARROW_BACK,
                    on_click=lambda _: asyncio.create_task(page.push_route("/feeds")),
                ),
                title=ft.Text(feed_title),
                bgcolor=ft.Colors.CYAN_50,
                actions=[
                    ft.Text(state.user.name if state.user else "", size=14),
                    ft.IconButton(ft.Icons.REFRESH, on_click=refresh),
                ],
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                _filter_chip("N\u00e3o lidos", toggle_unread),
                                _filter_chip("Importantes", toggle_important),
                            ],
                            spacing=8,
                        ),
                        tag_filter_row,
                    ],
                    spacing=4,
                ),
                padding=ft.Padding(left=10, top=5, right=10, bottom=5),
            ),
            entry_list,
        ],
    )
