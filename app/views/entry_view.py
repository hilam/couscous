import asyncio
import contextlib

import flet as ft
from fletify import FletifyHTML

from app.controls.nav_bar import set_navbar
from app.services.entry_service import get_entry, mark_important, mark_read


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


async def entry_view(ctx, entry_id: int) -> ft.View:
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

    async def handle_toggle_important(e):
        async with ctx.new_session() as s:
            entry_data = await get_entry(s, entry_id)
            if entry_data:
                new_val = not entry_data.important
                await mark_important(s, entry_id, user_id, important=new_val)
                e.control.icon = ft.Icons.STAR if new_val else ft.Icons.STAR_BORDER
                e.control.update()

    set_navbar(page)
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
                        _get_content_renderer(content),
                        ft.Container(
                            content=ft.FilledButton(
                                "Ver original",
                                icon=ft.Icons.OPEN_IN_NEW,
                                on_click=lambda _: ft.UrlLauncher().launch_url(
                                    entry.link or ""
                                ),
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
