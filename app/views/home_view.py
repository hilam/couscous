import flet as ft

from app.state import State


async def home_view(page: ft.Page, state: State) -> ft.View:
    return ft.View(
        route="/",
        scroll=ft.ScrollMode.AUTO,
        navigation_bar=ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=ft.Icons.HOME, label="Início"),
                ft.NavigationDestination(icon=ft.Icons.RSS_FEED, label="Feeds"),
                ft.NavigationDestination(icon=ft.Icons.INFO, label="Sobre"),
            ],
            on_change=lambda e: page.go(
                ["/feeds", "/feeds", "/about"][e.control.selected_index]
            ),
        ),
        controls=[
            ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.RSS_FEED, size=80, color=ft.colors.CYAN_400),
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
                        on_click=lambda _: page.go("/feeds"),
                    ),
                ],
            )
        ],
    )
