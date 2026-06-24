import asyncio
import contextlib

import flet as ft
from fletify import FletifyHTML

from app.controls.tag_chip import TagChip
from app.services.entry_service import get_entry, mark_important, mark_read
from app.services.tag_service import (
    assign_tag,
    get_distinct_tags,
    get_tags_for_entry,
    remove_tag,
)


async def _open_original_url(e: ft.ControlEvent):
    await ft.UrlLauncher().launch_url(e.control.data)


def _get_content_renderer(content: str) -> ft.Control:
    if not content:
        return ft.Text("Sem conte\u00fado dispon\u00edvel.")

    with contextlib.suppress(Exception):
        result = FletifyHTML(content).get_flet()
        if result.content is not None:
            return result

    return ft.Markdown(
        content,
        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
    )


async def entry_view(ctx, entry_id: int) -> ft.View:  # noqa: C901, PLR0915
    page = ctx.page
    state = ctx.state
    session = ctx.session
    user_id: int = (state.user.id or 0) if state.user else 0

    entry = await get_entry(session, entry_id)

    if not entry:
        return ft.View(
            route=f"/entry/{entry_id}",
            controls=[
                ft.AppBar(title=ft.Text("Artigo n\u00e3o encontrado")),
                ft.Container(
                    content=ft.Text("Artigo n\u00e3o encontrado"),
                    alignment=ft.Alignment.CENTER,
                    padding=ft.Padding.all(40),
                ),
            ],
        )

    await mark_read(session, entry_id, user_id)

    content = entry.content or entry.summary or "Sem conte\u00fado dispon\u00edvel."

    tag_list = await get_tags_for_entry(session, entry_id)
    tags_row = ft.Row(
        controls=[],
        spacing=4,
        wrap=True,
    )

    def build_tag_chips():
        tags_row.controls.clear()
        for t in tag_list:
            tags_row.controls.append(
                TagChip(
                    t,
                    on_delete=lambda tag=t: asyncio.create_task(handle_remove_tag(tag)),
                )
            )

    build_tag_chips()

    async def handle_toggle_important(e):
        async with ctx.new_session() as s:
            entry_data = await get_entry(s, entry_id)
            if entry_data:
                new_val = not entry_data.important
                await mark_important(s, entry_id, user_id, important=new_val)
                e.control.icon = ft.Icons.STAR if new_val else ft.Icons.STAR_BORDER
                e.control.update()

    async def handle_remove_tag(tag: str):
        async with ctx.new_session() as s:
            await remove_tag(s, entry_id, tag, user_id)
        tag_list[:] = [t for t in tag_list if t != tag]
        build_tag_chips()
        page.update()

    async def handle_add_tag_dialog(e):
        dlg_ref: list[ft.AlertDialog] = []

        async def submit_new_tag(ev):
            new_tag = (tag_field.value or "").strip()
            if not new_tag:
                return
            async with ctx.new_session() as s:
                await assign_tag(s, entry_id, new_tag, user_id)
            if new_tag not in tag_list:
                tag_list.append(new_tag)
                tag_list.sort()
            build_tag_chips()
            if dlg_ref:
                dlg_ref[0].open = False
            page.update()

        tag_field = ft.TextField(
            label="Nova etiqueta",
            hint_text="Digite o nome e pressione Enter",
            autofocus=True,
            on_submit=lambda ev: asyncio.create_task(submit_new_tag(ev)),
        )

        existing_tags = await get_distinct_tags(session, user_id)

        existing_col = ft.Column(spacing=2)

        async def submit_existing_tag(tag: str):
            async with ctx.new_session() as s:
                await assign_tag(s, entry_id, tag, user_id)
            if tag not in tag_list:
                tag_list.append(tag)
                tag_list.sort()
            build_tag_chips()
            if dlg_ref:
                dlg_ref[0].open = False
            page.update()

        for t in existing_tags:
            if t not in tag_list:
                existing_col.controls.append(
                    ft.TextButton(
                        t,
                        on_click=lambda _, tag=t: asyncio.create_task(
                            submit_existing_tag(tag)
                        ),
                    )
                )

        dlg = ft.AlertDialog(
            title=ft.Text("Adicionar etiqueta"),
            content=ft.Column(
                controls=[
                    tag_field,
                    ft.Text("Etiquetas existentes:", size=12, color=ft.Colors.GREY)
                    if existing_tags
                    else ft.Text(),
                    existing_col,
                ],
                tight=True,
                spacing=8,
                scroll=ft.ScrollMode.AUTO,
                height=300,
            ),
        )
        dlg_ref.append(dlg)
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    return ft.View(
        route=f"/entry/{entry_id}",
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.AppBar(
                leading=ft.IconButton(
                    ft.Icons.ARROW_BACK,
                    on_click=lambda _: asyncio.create_task(
                        page.push_route(f"/feed/{entry.feed}")
                    ),
                ),
                title=ft.Text(entry.title or "Artigo"),
                bgcolor=ft.Colors.CYAN_50,
                actions=[
                    ft.Text(state.user.name if state.user else "", size=14),
                    ft.IconButton(
                        ft.Icons.STAR if entry.important else ft.Icons.STAR_BORDER,
                        on_click=handle_toggle_important,
                    ),
                ],
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            entry.title,
                            theme_style=ft.TextThemeStyle.HEADLINE_SMALL,
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    entry.author or "",
                                    theme_style=ft.TextThemeStyle.BODY_SMALL,
                                ),
                                ft.Text(
                                    entry.published.strftime("%d/%m/%Y")
                                    if entry.published
                                    else "",
                                    theme_style=ft.TextThemeStyle.BODY_SMALL,
                                ),
                            ],
                        ),
                        ft.Divider(),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    "Etiquetas:",
                                    theme_style=ft.TextThemeStyle.BODY_SMALL,
                                    color=ft.Colors.GREY,
                                ),
                                tags_row,
                                ft.IconButton(
                                    ft.Icons.ADD,
                                    icon_size=18,
                                    tooltip="Adicionar etiqueta",
                                    on_click=handle_add_tag_dialog,
                                ),
                            ],
                            spacing=4,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Divider(),
                        _get_content_renderer(content),
                        ft.Container(
                            content=(
                                ft.FilledButton(
                                    "Ver original",
                                    icon=ft.Icons.OPEN_IN_NEW,
                                    data=entry.link or "",
                                    on_click=_open_original_url,  # type: ignore[arg-type]
                                )
                            )
                            if entry.link
                            else None,
                            alignment=ft.Alignment.CENTER,
                            padding=ft.Padding.all(20),
                        ),
                    ],
                    spacing=10,
                ),
                padding=20,
            ),
        ],
    )
