import asyncio

import flet as ft

from app.state import State


async def home_view(page: ft.Page, state: State) -> ft.View:
    return ft.View(
        route="/",
        scroll=ft.ScrollMode.AUTO,
        navigation_bar=ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Início"),
                ft.NavigationBarDestination(icon=ft.Icons.RSS_FEED, label="Feeds"),
                ft.NavigationBarDestination(icon=ft.Icons.INFO, label="Sobre"),
            ],
            on_change=lambda e: asyncio.create_task(
                page.push_route(
                    ["/feeds", "/feeds", "/about"][e.control.selected_index]
                )
            ),
        ),
        controls=[
            ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.RSS_FEED, size=80, color=ft.Colors.CYAN_400),
                    ft.Text("CousCous", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
                    ft.Text(
                        "Seu leitor de feeds RSS",
                        theme_style=ft.TextThemeStyle.TITLE_LARGE,
                    ),
                    ft.Text(
                        "Adicione feeds e acompanhe suas notícias em um só lugar.",
                        theme_style=ft.TextThemeStyle.BODY_LARGE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.FilledButton(
                        "Ver meus feeds",
                        icon=ft.Icons.RSS_FEED,
                        on_click=lambda _: asyncio.create_task(
                            page.push_route("/feeds")
                        ),
                    ),
                ],
            )
        ],
    )
