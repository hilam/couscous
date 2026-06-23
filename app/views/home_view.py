import asyncio

import flet as ft


async def home_view(ctx) -> ft.View:
    return ft.View(
        route="/",
        scroll=ft.ScrollMode.AUTO,
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
                        "Adicione feeds e acompanhe suas not\u00edcias "
                        "em um s\u00f3 lugar.",
                        theme_style=ft.TextThemeStyle.BODY_LARGE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.FilledButton(
                        "Ver meus feeds",
                        icon=ft.Icons.RSS_FEED,
                        on_click=lambda _: asyncio.create_task(
                            ctx.page.push_route("/feeds")
                        ),
                    ),
                ],
            )
        ],
    )
