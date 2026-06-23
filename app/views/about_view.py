import flet as ft


async def about_view(ctx) -> ft.View:
    return ft.View(
        route="/about",
        controls=[
            ft.AppBar(title=ft.Text("Sobre"), bgcolor=ft.Colors.CYAN_50),
            ft.Column(
                controls=[
                    ft.Icon(ft.Icons.RSS_FEED, size=60, color=ft.Colors.CYAN_400),
                    ft.Text("CousCous", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                    ft.Text("Vers\u00e3o 0.1.0"),
                    ft.Divider(),
                    ft.Text(
                        "CousCous \u00e9 um leitor de feeds RSS "
                        "constru\u00eddo com Python e Flet."
                    ),
                    ft.Text(
                        "Permite adicionar feeds RSS, visualizar artigos, "
                        "e gerenciar sua leitura de forma simples."
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
        ],
    )
