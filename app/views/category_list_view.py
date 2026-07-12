import asyncio

import flet as ft

from app.controls.category_dialogs import CreateCategoryDialog, RenameCategoryDialog
from app.controls.confirm_dialog import ConfirmDialog
from app.services.category_service import (
    build_category_tree,
    delete_category,
    get_categories_with_counts,
)


def _build_tree_controls(tree, on_rename, on_delete, level=0):
    controls = []
    for node in tree:
        indent = ft.Container(width=level * 24)
        tile = ft.ListTile(
            leading=ft.Icon(ft.Icons.FOLDER, color=ft.Colors.CYAN_400),
            title=ft.Text(node["name"]),
        )
        row = ft.Row(
            controls=[
                indent,
                tile,
                ft.IconButton(
                    ft.Icons.EDIT,
                    icon_size=18,
                    on_click=lambda _, n=node: asyncio.create_task(on_rename(n)),
                ),
                ft.IconButton(
                    ft.Icons.DELETE_OUTLINE,
                    icon_size=18,
                    icon_color=ft.Colors.RED_300,
                    on_click=lambda _, n=node: on_delete(n),
                ),
            ],
        )
        controls.append(row)
        if node["children"]:
            controls.extend(
                _build_tree_controls(node["children"], on_rename, on_delete, level + 1)
            )
    return controls


async def category_list_view(ctx) -> ft.View:
    page = ctx.page
    state = ctx.state
    session = ctx.session
    user_id: int = (state.user.id or 0) if state.user else 0

    tree_view = ft.Column(spacing=2, scroll=ft.ScrollMode.AUTO)

    async def refresh_tree():
        tree_view.controls.clear()
        async with ctx.open_session() as s:
            cats, feed_counts, unread_counts = await get_categories_with_counts(
                s, user_id
            )
            tree = build_category_tree(cats, feed_counts, unread_counts)
        if not tree:
            tree_view.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(
                                ft.Icons.FOLDER_OPEN, size=60, color=ft.Colors.GREY_400
                            ),
                            ft.Text(
                                "Nenhuma categoria",
                                theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                                color=ft.Colors.GREY,
                            ),
                            ft.Text(
                                "Crie pastas para organizar seus feeds",
                                color=ft.Colors.GREY_400,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    alignment=ft.Alignment.CENTER,
                    padding=ft.Padding.all(40),
                )
            )
        else:
            controls = _build_tree_controls(
                tree, _open_rename_dialog, _delete_category_cb
            )
            tree_view.controls.extend(controls)
        page.update()

    async def _open_rename_dialog(node):
        dlg = RenameCategoryDialog(node, page, refresh_tree, ctx)
        page.show_dialog(dlg)
        page.update()

    def _delete_category_cb(node):
        msg = (
            f'Excluir "{node["name"]}"? '
            "Filhos ser\u00e3o movidos para a raiz. Feeds ficar\u00e3o sem categoria."
        )
        dlg = ConfirmDialog(
            title="Excluir categoria",
            message=msg,
            on_confirm=lambda e: asyncio.create_task(_delete_confirmed(node)),
        )
        page.show_dialog(dlg)
        page.update()

    async def _delete_confirmed(node):
        async with ctx.open_session() as s:
            await delete_category(s, user_id, node["id"])
        await refresh_tree()

    async def open_new_dialog(e):
        create_dlg = CreateCategoryDialog(page, refresh_tree, ctx)
        page.overlay.append(create_dlg)
        create_dlg.open = True
        await create_dlg.load_parents()
        page.update()

    cats, feed_counts, unread_counts = await get_categories_with_counts(
        session, user_id
    )
    initial_tree = build_category_tree(cats, feed_counts, unread_counts) if cats else []
    if not initial_tree:
        tree_view.controls.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            ft.Icons.FOLDER_OPEN, size=60, color=ft.Colors.GREY_400
                        ),
                        ft.Text(
                            "Nenhuma categoria",
                            theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                            color=ft.Colors.GREY,
                        ),
                        ft.Text(
                            "Crie pastas para organizar seus feeds",
                            color=ft.Colors.GREY_400,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.Alignment.CENTER,
                padding=ft.Padding.all(40),
            )
        )
    else:
        controls = _build_tree_controls(
            initial_tree, _open_rename_dialog, _delete_category_cb
        )
        tree_view.controls.extend(controls)

    return ft.View(
        route="/categories",
        controls=[
            ft.AppBar(
                title=ft.Text("Categorias"),
                bgcolor=ft.Colors.CYAN_50,
                actions=[
                    ft.Text(state.user.name if state.user else "", size=14),
                    ft.IconButton(ft.Icons.ADD, on_click=open_new_dialog),
                ],
            ),
            ft.Stack(
                controls=[tree_view],
                expand=True,
            ),
        ],
    )


def _flatten_tree_for_dropdown(tree, options, level):
    for node in tree:
        prefix = "  " * level + "\u2514 " if level > 0 else ""
        options.append(ft.dropdown.Option(str(node["id"]), f"{prefix}{node['name']}"))
        if node["children"]:
            _flatten_tree_for_dropdown(node["children"], options, level + 1)
