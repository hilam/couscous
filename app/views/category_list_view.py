import asyncio

import flet as ft

from app.controls.confirm_dialog import ConfirmDialog
from app.services.category_service import (
    create_category,
    delete_category,
    get_category_tree,
    rename_category,
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
        async with ctx.new_session() as s:
            tree = await get_category_tree(s, user_id)
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
        dlg = _build_rename_dialog(node, page, refresh_tree, ctx)
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
        async with ctx.new_session() as s:
            await delete_category(s, user_id, node["id"])
        await refresh_tree()

    async def open_new_dialog(e):
        create_dlg = _build_create_dialog(page, refresh_tree, ctx)
        page.overlay.append(create_dlg)
        create_dlg.open = True
        page.update()

    initial_tree = await get_category_tree(session, user_id)
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


def _build_create_dialog(page, refresh_cb, ctx):  # noqa: C901
    name_field = ft.TextField(label="Nome da categoria", autofocus=True, expand=True)
    parent_dropdown = ft.Dropdown(label="Categoria pai", expand=True)

    async def _load_parent_dropdown():
        async with ctx.new_session() as s:
            tree = await get_category_tree(s, ctx.state.user.id)
        options = [ft.dropdown.Option("0", "Nenhuma (raiz)")]
        _flatten_tree_for_dropdown(tree, options, 0)
        parent_dropdown.options = options
        parent_dropdown.value = "0"
        page.update()

    _task_ref = asyncio.create_task(_load_parent_dropdown())  # noqa: RUF006 - keep task alive

    async def _do_create():
        name = name_field.value.strip()
        if not name:
            return False
        raw = parent_dropdown.value
        parent_id = int(raw) if raw and raw != "0" else None
        async with ctx.new_session() as s:
            try:
                await create_category(s, ctx.state.user.id, name, parent_id)
            except ValueError:
                snack = ft.SnackBar(
                    content=ft.Text("Categoria j\u00e1 existe neste n\u00edvel")
                )
                page.overlay.append(snack)
                snack.open = True
                page.update()
                return False
            else:
                return True

    async def _submit_and_close(e):
        dlg.open = False
        dlg.update()
        if await _do_create():
            await refresh_cb()

    async def _submit_and_continue(e):
        if not await _do_create():
            return
        name_field.value = ""
        name_field.update()
        await _load_parent_dropdown()
        await refresh_cb()
        await name_field.focus()

    name_field.on_submit = lambda e: asyncio.create_task(parent_dropdown.focus())

    def _cancel(e):
        dlg.open = False
        dlg.update()

    dlg = ft.AlertDialog(
        title=ft.Text("Nova Categoria"),
        content=ft.Column(
            controls=[name_field, parent_dropdown],
            width=350,
            tight=True,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=_cancel),
            ft.FilledButton("Criar outro", on_click=_submit_and_continue),
            ft.FilledButton("Criar", on_click=_submit_and_close),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    return dlg


def _build_rename_dialog(node, page, refresh_cb, ctx):
    name_field = ft.TextField(
        label="Novo nome", value=node["name"], autofocus=True, expand=True
    )

    async def _submit(e):
        new_name = name_field.value.strip()
        if not new_name:
            return
        dlg.open = False
        dlg.update()
        async with ctx.new_session() as s:
            try:
                await rename_category(s, ctx.state.user.id, node["id"], new_name)
            except ValueError:
                snack = ft.SnackBar(
                    content=ft.Text("Categoria j\u00e1 existe neste n\u00edvel")
                )
                page.overlay.append(snack)
                snack.open = True
                page.update()
                return
        await refresh_cb()

    def _cancel(e):
        dlg.open = False
        dlg.update()

    dlg = ft.AlertDialog(
        title=ft.Text("Renomear Categoria"),
        content=ft.Column(
            controls=[name_field],
            width=300,
            tight=True,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=_cancel),
            ft.FilledButton("Renomear", on_click=_submit),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    return dlg


def _flatten_tree_for_dropdown(tree, options, level):
    for node in tree:
        prefix = "  " * level + "\u2514 " if level > 0 else ""
        options.append(ft.dropdown.Option(str(node["id"]), f"{prefix}{node['name']}"))
        if node["children"]:
            _flatten_tree_for_dropdown(node["children"], options, level + 1)
