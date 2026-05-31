import asyncio

import flet as ft

from app.db import get_db_session
from app.services.entry_service import get_entry, mark_important, mark_read
from app.state import State


async def entry_view(page: ft.Page, state: State, entry_id: int) -> ft.View:
    async with get_db_session() as session:
        entry = await get_entry(session, entry_id)

    if not entry:
        return ft.View(
            route=f"/entry/{entry_id}",
            controls=[
                ft.AppBar(title=ft.Text("Artigo não encontrado")),
                ft.Container(
                    content=ft.Text("Artigo não encontrado"),
                    alignment=ft.Alignment.CENTER,
                    padding=ft.Padding.all(40),
                ),
            ],
        )

    async with get_db_session() as session:
        await mark_read(session, entry_id)

    content = entry.content or entry.summary or "Sem conteúdo disponível."

    return ft.View(
        route=f"/entry/{entry_id}",
        scroll=ft.ScrollMode.AUTO,
        navigation_bar=ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=ft.Icons.HOME, label="Início"),
                ft.NavigationDestination(icon=ft.Icons.RSS_FEED, label="Feeds"),
                ft.NavigationDestination(icon=ft.Icons.INFO, label="Sobre"),
            ],
            on_change=lambda e: asyncio.create_task(
                page.push_route(
                    ["/feeds", "/feeds", "/about"][e.control.selected_index]
                )
            ),
        ),
        controls=[
            ft.AppBar(
                title=ft.Text(entry.title or "Artigo"),
                bgcolor=ft.Colors.CYAN_50,
                actions=[
                    ft.Text(state.user.name if state.user else "", size=14),
                    ft.IconButton(
                        ft.Icons.STAR_BORDER,
                        on_click=lambda e: toggle_important(page, entry_id),
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
                        ft.Markdown(
                            content,
                            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                        ),
                        ft.Container(
                            content=ft.FilledButton(
                                "Ver original",
                                icon=ft.Icons.OPEN_IN_NEW,
                                on_click=lambda _: page.launch_url(entry.link or ""),
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


async def toggle_important(page: ft.Page, entry_id: int):
    async with get_db_session() as session:
        entry = await get_entry(session, entry_id)
        if entry:
            await mark_important(session, entry_id, important=not entry.important)
    page.update()
