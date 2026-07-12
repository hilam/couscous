import asyncio

import flet as ft

from app.controls.article_card import ArticleCard
from app.services.feed_browser import (
    ExploreState,
    clear_tags,
    load,
    search,
    select_category,
    toggle_tag,
)

TREE_WIDTH = 220
TAGS_DRAWER_WIDTH = 180
MOBILE_BREAKPOINT = 600
RECENTES_LABEL = "Recentes"


def _empty_state(message: str = "Nenhum artigo encontrado") -> ft.Container:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.ARTICLE, size=60, color=ft.Colors.GREY_400),
                ft.Text(
                    message,
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


def _build_article_card(
    entry, page: ft.Page, tags: list[str] | None = None
) -> ArticleCard:
    return ArticleCard(
        entry=entry,
        tags=tags,
        on_click=lambda _, eid=entry.id: asyncio.create_task(
            page.push_route(f"/entry/{eid}")
        ),
    )


def _build_category_tree(tree, on_select, selected_id, expanded_ids):
    controls: list[ft.Control] = []

    recentes = ft.ListTile(
        leading=ft.Icon(ft.Icons.HOME, size=20),
        title=ft.Text(RECENTES_LABEL, size=14),
        selected=selected_id is None,
        dense=True,
        on_click=lambda _: on_select(None),
    )
    controls.append(recentes)
    controls.append(ft.Divider(height=1))

    def add_nodes(nodes, depth=0):
        for node in nodes:
            has_children = bool(node.get("children"))

            if has_children:
                expanded = node["id"] in expanded_ids
                leading: ft.Control = ft.Icon(
                    ft.Icons.EXPAND_MORE if expanded else ft.Icons.CHEVRON_RIGHT,
                    size=18,
                )
            else:
                leading = ft.Icon(ft.Icons.FOLDER, size=18)

            trailing: ft.Control | None = None
            if node.get("unread_count", 0) > 0:
                trailing = ft.Container(
                    content=ft.Text(
                        str(node["unread_count"]),
                        size=11,
                        color=ft.Colors.WHITE,
                    ),
                    bgcolor=ft.Colors.CYAN_600,
                    border_radius=10,
                    padding=ft.Padding(left=6, right=6, top=2, bottom=2),
                )

            tile = ft.ListTile(
                leading=leading,
                title=ft.Text(node["name"], size=14),
                trailing=trailing,
                selected=selected_id == node["id"],
                dense=True,
                on_click=lambda _, nid=node["id"]: on_select(nid),
            )
            tile.padding = ft.Padding(  # type: ignore[attr-defined]
                left=8 + depth * 16, top=0, right=8, bottom=0
            )
            controls.append(tile)
            if has_children and node["id"] in expanded_ids:
                add_nodes(node["children"], depth + 1)

    if tree:
        add_nodes(tree)
    else:
        controls.append(
            ft.Container(
                content=ft.Text("Nenhuma categoria", size=12, color=ft.Colors.GREY),
                padding=ft.Padding(left=16, top=8, right=8, bottom=8),
            )
        )

    return ft.ListView(controls=controls, spacing=2, padding=ft.Padding.all(4))


def _build_tag_drawer_content(tag_counts, selected_tags, on_toggle_tag, on_clear):
    rows: list[ft.Control] = []
    for tag, count in tag_counts:
        selected = tag in selected_tags
        rows.append(
            ft.ListTile(
                leading=ft.Icon(
                    ft.Icons.CHECK_BOX
                    if selected
                    else ft.Icons.CHECK_BOX_OUTLINE_BLANK,
                    size=18,
                    color=ft.Colors.CYAN_600 if selected else ft.Colors.GREY,
                ),
                title=ft.Text(f"#{tag} ({count})", size=13),
                dense=True,
                on_click=lambda _, t=tag: on_toggle_tag(t),
            )
        )

    if selected_tags:
        rows.append(ft.Divider(height=1))
        rows.append(
            ft.TextButton(
                "Limpar filtros",
                icon=ft.Icons.CLOSE,
                on_click=lambda _: on_clear(),
                style=ft.ButtonStyle(color=ft.Colors.GREY_600),
            )
        )
    return rows


async def explore_view(ctx) -> ft.View:  # noqa: C901, PLR0915
    page = ctx.page
    state = ctx.state
    session = ctx.session
    user_id: int = (state.user.id or 0) if state.user else 0

    browser_state = await load(session, user_id)

    is_mobile = (page.width or 9999) < MOBILE_BREAKPOINT

    entry_list = ft.ListView(spacing=8, padding=10, expand=True)

    search_field = ft.TextField(
        hint_text="Pesquisar...",
        prefix_icon=ft.Icons.SEARCH,
        dense=True,
        border_color=ft.Colors.TRANSPARENT,
        focused_border_color=ft.Colors.CYAN_300,
        content_padding=ft.Padding(left=8, top=8, right=8, bottom=8),
    )

    tag_button = ft.IconButton(
        icon=ft.Icons.LABEL,
        tooltip="Filtrar por tags",
    )

    tag_badge = ft.Text("", size=12)
    drawer_col = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=2)

    tag_drawer_container = ft.Container(
        content=drawer_col,
        width=TAGS_DRAWER_WIDTH,
        visible=False,
        bgcolor=ft.Colors.GREY_50,
        border=ft.Border(left=ft.border.BorderSide(1, ft.Colors.GREY_200)),
    )

    body_row = ft.Row(spacing=0, expand=True)
    tree_panel_ref: list[ft.Container | None] = [None]

    def render():
        nonlocal browser_state
        _populate_entry_list(browser_state)
        _update_tag_badge()
        _refresh_drawer_content()
        body_row.controls = _build_body_controls()

    def _populate_entry_list(bs: ExploreState):
        entry_list.controls.clear()
        for entry in bs.entries:
            t = bs.tag_map.get(entry.id, []) if entry.id else None
            entry_list.controls.append(_build_article_card(entry, page, t))
        if not bs.entries:
            if bs.is_searching:
                msg = f"Nenhum resultado para '{search_field.value}'"
                entry_list.controls.append(_empty_state(msg))
            elif bs.selected_category_id:
                entry_list.controls.append(
                    _empty_state("Nenhum artigo nesta categoria")
                )
            else:
                entry_list.controls.append(_empty_state())

    def _update_tag_badge():
        tag_badge.value = (
            str(len(browser_state.selected_tags))
            if browser_state.selected_tags else ""
        )

    def _refresh_drawer_content():
        drawer_col.controls.clear()
        if not browser_state.tag_counts:
            drawer_col.controls.append(
                ft.Text("Nenhuma tag", size=13, color=ft.Colors.GREY)
            )
        else:
            drawer_col.controls.extend(
                _build_tag_drawer_content(
                    browser_state.tag_counts,
                    browser_state.selected_tags,
                    _toggle_tag,
                    _clear_tags,
                )
            )

    def _build_tree_panel():
        if is_mobile:
            return None
        container = ft.Container(
            content=_build_category_tree(
                browser_state.tree,
                _select_category,
                browser_state.selected_category_id,
                browser_state.expanded_ids,
            ),
            width=TREE_WIDTH,
            bgcolor=ft.Colors.GREY_50,
            border=ft.Border(right=ft.border.BorderSide(1, ft.Colors.GREY_200)),
        )
        tree_panel_ref[0] = container
        return container

    def _refresh_tree_panel():
        if is_mobile or tree_panel_ref[0] is None:
            return
        tree_panel_ref[0].content = _build_category_tree(
            browser_state.tree,
            _select_category,
            browser_state.selected_category_id,
            browser_state.expanded_ids,
        )

    def _build_mobile_menu():
        if not is_mobile:
            return None
        items = [
            ft.PopupMenuItem(  # type: ignore[call-arg]
                text=RECENTES_LABEL,
                on_click=lambda _: _select_category(None),
            )
        ]

        def add_nodes(nodes, depth=0):
            for node in nodes:
                prefix = "  " * depth
                text = f"{prefix}{node['name']}"
                if node.get("unread_count", 0) > 0:
                    text += f" ({node['unread_count']})"
                items.append(
                    ft.PopupMenuItem(  # type: ignore[call-arg]
                        text=text,
                        on_click=lambda _, nid=node["id"]: _select_category(nid),
                    )
                )
                if node.get("children"):
                    add_nodes(node["children"], depth + 1)

        add_nodes(browser_state.tree)
        return ft.PopupMenuButton(icon=ft.Icons.MENU, items=items)

    def _build_body_controls():
        controls: list[ft.Control] = []
        tree_panel = _build_tree_panel()
        if tree_panel:
            controls.append(tree_panel)
        controls.append(ft.Container(content=entry_list, expand=True))
        if tag_drawer_container.visible and not is_mobile:
            controls.append(tag_drawer_container)
        return controls

    async def _refresh_entries():
        nonlocal browser_state
        try:
            async with ctx.open_session() as s:
                browser_state = await select_category(
                    s, browser_state, browser_state.selected_category_id, user_id
                )
            render()
            page.update()
        except Exception as exc:
            page.open(ft.SnackBar(content=ft.Text(f"Erro: {exc}")))

    def _select_category(cat_id: int | None):
        nonlocal browser_state
        async def _inner():
            nonlocal browser_state
            async with ctx.open_session() as s:
                browser_state = await select_category(
                    s, browser_state, cat_id, user_id
                )
            search_field.value = ""
            render()
            _refresh_tree_panel()
            page.update()
        asyncio.create_task(_inner())  # noqa: RUF006

    async def _do_search():
        nonlocal browser_state
        async with ctx.open_session() as s:
            browser_state = await search(
                s, browser_state, search_field.value or "", user_id
            )
        render()
        page.update()

    def _toggle_tag(tag: str):
        nonlocal browser_state
        async def _inner():
            nonlocal browser_state
            async with ctx.open_session() as s:
                browser_state = await toggle_tag(
                    s, browser_state, tag, user_id
                )
            render()
            _refresh_drawer_content()
            if is_mobile:
                tag_drawer_container.visible = False
                body_row.controls = _build_body_controls()
                page.close_bottom_sheet()
            page.update()
        asyncio.create_task(_inner())  # noqa: RUF006

    def _clear_tags():
        nonlocal browser_state
        async def _inner():
            nonlocal browser_state
            async with ctx.open_session() as s:
                browser_state = await clear_tags(s, browser_state, user_id)
            render()
            tag_drawer_container.visible = False
            body_row.controls = _build_body_controls()
            page.update()
        asyncio.create_task(_inner())  # noqa: RUF006

    def _toggle_tags_drawer():
        if is_mobile:
            _show_mobile_tag_sheet()
            return
        tag_drawer_container.visible = not tag_drawer_container.visible
        _refresh_drawer_content()
        body_row.controls = _build_body_controls()
        page.update()

    def _show_mobile_tag_sheet():
        sheet_controls: list[ft.Control] = []
        if not browser_state.tag_counts:
            sheet_controls.append(ft.Text("Nenhuma tag", size=14, color=ft.Colors.GREY))
        else:
            sheet_controls.extend(
                _build_tag_drawer_content(
                    browser_state.tag_counts,
                    browser_state.selected_tags,
                    _toggle_tag,
                    _clear_tags,
                )
            )
        sheet = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column(
                    controls=sheet_controls,
                    scroll=ft.ScrollMode.AUTO,
                    spacing=2,
                ),
                padding=ft.Padding.all(16),
            ),
            open=True,
        )
        page.open(sheet)

    search_field.on_submit = lambda e: asyncio.create_task(_do_search())
    tag_button.on_click = lambda _: _toggle_tags_drawer()

    mobile_menu = _build_mobile_menu()

    render()

    return ft.View(
        route="/",
        controls=[
            ft.AppBar(
                leading=mobile_menu,
                title=search_field,
                bgcolor=ft.Colors.CYAN_50,
                actions=[
                    tag_badge,
                    tag_button,
                    ft.IconButton(
                        ft.Icons.REFRESH,
                        on_click=lambda _: asyncio.create_task(_refresh_entries()),
                    ),
                ],
            ),
            body_row,
        ],
    )
