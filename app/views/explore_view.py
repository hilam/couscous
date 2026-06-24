import asyncio
from collections import defaultdict

import flet as ft
from sqlmodel import select

from app.controls.article_card import ArticleCard
from app.services.category_service import get_category_tree
from app.services.entry_service import list_recent
from app.services.search_service import search_entries
from app.services.tag_service import get_distinct_tags_with_counts
from database.models.couscous import Entry, EntryTag

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
    entry: Entry, page: ft.Page, tags: list[str] | None = None
) -> ArticleCard:
    return ArticleCard(
        entry=entry,
        tags=tags,
        on_click=lambda _, eid=entry.id: asyncio.create_task(
            page.push_route(f"/entry/{eid}")
        ),
    )


async def _load_entry_tags(session, entries: list[Entry]) -> dict[int, list[str]]:
    if not entries:
        return {}
    entry_ids = [e.id for e in entries if e.id is not None]
    if not entry_ids:
        return {}
    result = await session.execute(
        select(EntryTag).where(EntryTag.entry_id.in_(entry_ids))  # type: ignore[attr-defined]
    )
    tag_map: dict[int, list[str]] = defaultdict(list)
    for et in result.scalars().all():
        tag_map[et.entry_id].append(et.tag)
    return tag_map


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


def _build_tag_drawer_content(tags, selected_tags, on_toggle_tag, on_clear):
    rows: list[ft.Control] = []
    for tag, count in tags:
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

    selected_category_id: int | None = None
    expanded_ids: set[int] = set()
    selected_tags: set[str] = set()
    is_searching = False

    tree = await get_category_tree(session, user_id)

    def _find_node(nodes, target_id: int):
        for node in nodes:
            if node["id"] == target_id:
                return node
            if node.get("children"):
                found = _find_node(node["children"], target_id)
                if found:
                    return found
        return None

    tag_counts = await get_distinct_tags_with_counts(session, user_id)

    entries = await list_recent(session, user_id, limit=50)
    tag_map = await _load_entry_tags(session, entries)

    entry_list = ft.ListView(spacing=8, padding=10, expand=True)

    search_field = ft.TextField(
        hint_text="Pesquisar...",
        prefix_icon=ft.Icons.SEARCH,
        dense=True,
        border_color=ft.Colors.TRANSPARENT,
        focused_border_color=ft.Colors.CYAN_300,
        content_padding=ft.Padding(left=8, top=8, right=8, bottom=8),
        on_submit=lambda e: asyncio.create_task(_do_search()),
    )

    tag_button = ft.IconButton(
        icon=ft.Icons.LABEL,
        tooltip="Filtrar por tags",
        on_click=lambda _: toggle_tags_drawer(),
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

    is_mobile = (page.width or 9999) < MOBILE_BREAKPOINT

    def _update_tag_badge():
        tag_badge.value = str(len(selected_tags)) if selected_tags else ""

    def _refresh_drawer_content():
        drawer_col.controls.clear()
        if not tag_counts:
            drawer_col.controls.append(
                ft.Text("Nenhuma tag", size=13, color=ft.Colors.GREY)
            )
        else:
            drawer_col.controls.extend(
                _build_tag_drawer_content(
                    tag_counts, selected_tags, toggle_tag, clear_tags
                )
            )

    body_row = ft.Row(spacing=0, expand=True)

    def _populate_entry_list(entries_to_show, tag_map_data):
        entry_list.controls.clear()
        for entry in entries_to_show:
            t = tag_map_data.get(entry.id, []) if entry.id else None
            entry_list.controls.append(_build_article_card(entry, page, t))
        if not entries_to_show:
            if is_searching:
                msg = f"Nenhum resultado para '{search_field.value}'"
                entry_list.controls.append(_empty_state(msg))
            elif selected_category_id:
                entry_list.controls.append(
                    _empty_state("Nenhum artigo nesta categoria")
                )
            else:
                entry_list.controls.append(_empty_state())

    _populate_entry_list(entries, tag_map)

    def _build_tree_panel():
        if is_mobile:
            return None
        return ft.Container(
            content=_build_category_tree(
                tree, select_category, selected_category_id, expanded_ids
            ),
            width=TREE_WIDTH,
            bgcolor=ft.Colors.GREY_50,
            border=ft.Border(right=ft.border.BorderSide(1, ft.Colors.GREY_200)),
        )

    def _build_mobile_menu():
        if not is_mobile:
            return None
        items = [
            ft.PopupMenuItem(  # type: ignore[call-arg]
                text=RECENTES_LABEL,
                on_click=lambda _: select_category(None),
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
                        on_click=lambda _, nid=node["id"]: select_category(nid),
                    )
                )
                if node.get("children"):
                    add_nodes(node["children"], depth + 1)

        add_nodes(tree)
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

    async def refresh_entries():
        try:
            async with ctx.new_session() as s:
                fresh = await list_recent(
                    s,
                    user_id,
                    category_id=selected_category_id,
                    tags=list(selected_tags) if selected_tags else None,
                    limit=50,
                    include_subcategories=True,
                )
                tm = await _load_entry_tags(s, fresh)
            _populate_entry_list(fresh, tm)
            page.update()
        except Exception as exc:
            page.open(ft.SnackBar(content=ft.Text(f"Erro: {exc}")))

    def select_category(cat_id: int | None):
        nonlocal selected_category_id, is_searching

        if cat_id is None:
            selected_category_id = None
            is_searching = False
            search_field.value = ""
            asyncio.create_task(refresh_entries())  # noqa: RUF006
            return

        node = _find_node(tree, cat_id)
        if node is None:
            return

        has_children = bool(node.get("children"))
        has_feeds = node.get("total_feed_count", 0) > 0

        if has_children:
            if cat_id in expanded_ids:
                expanded_ids.discard(cat_id)
            else:
                expanded_ids.add(cat_id)

        if has_feeds:
            selected_category_id = cat_id
            is_searching = False
            search_field.value = ""
            asyncio.create_task(refresh_entries())  # noqa: RUF006

        body_row.controls = _build_body_controls()
        page.update()

    async def _do_search():
        nonlocal is_searching
        query = search_field.value.strip()
        if not query:
            is_searching = False
            await refresh_entries()
            return
        is_searching = True
        try:
            tag_filter = next(iter(selected_tags)) if len(selected_tags) == 1 else None
            async with ctx.new_session() as s:
                results = await search_entries(
                    s,
                    query,
                    user_id,
                    category_id=selected_category_id,
                    tag=tag_filter,
                    limit=50,
                )
                tm = await _load_entry_tags(s, results)
            _populate_entry_list(results, tm)
            page.update()
        except Exception as exc:
            page.open(ft.SnackBar(content=ft.Text(f"Erro na busca: {exc}")))

    def toggle_tag(tag: str):
        if tag in selected_tags:
            selected_tags.discard(tag)
        else:
            selected_tags.add(tag)
        _update_tag_badge()
        _refresh_drawer_content()
        if is_mobile:
            tag_drawer_container.visible = False
            body_row.controls = _build_body_controls()
            page.close_bottom_sheet()
        asyncio.create_task(refresh_entries())  # noqa: RUF006

    def clear_tags():
        selected_tags.clear()
        _update_tag_badge()
        _refresh_drawer_content()
        tag_drawer_container.visible = False
        body_row.controls = _build_body_controls()
        asyncio.create_task(refresh_entries())  # noqa: RUF006

    def toggle_tags_drawer():
        if is_mobile:
            _show_mobile_tag_sheet()
            return
        tag_drawer_container.visible = not tag_drawer_container.visible
        _refresh_drawer_content()
        body_row.controls = _build_body_controls()
        page.update()

    def _show_mobile_tag_sheet():
        sheet_controls: list[ft.Control] = []
        if not tag_counts:
            sheet_controls.append(ft.Text("Nenhuma tag", size=14, color=ft.Colors.GREY))
        else:
            sheet_controls.extend(
                _build_tag_drawer_content(
                    tag_counts, selected_tags, toggle_tag, clear_tags
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

    mobile_menu = _build_mobile_menu()

    _update_tag_badge()
    _refresh_drawer_content()
    body_row.controls = _build_body_controls()

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
                        on_click=lambda _: asyncio.create_task(refresh_entries()),
                    ),
                ],
            ),
            body_row,
        ],
    )
