import asyncio

import flet as ft

from app.state import State


async def about_view(page: ft.Page, state: State) -> ft.View:
    return ft.View(
        route="/about",
        navigation_bar=ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=ft.Icons.HOME, label="Início"),
                ft.NavigationDestination(icon=ft.Icons.RSS_FEED, label="Feeds"),
                ft.NavigationDestination(icon=ft.Icons.INFO, label="Sobre"),
            ],
            selected_index=2,
            on_change=lambda e: asyncio.create_task(page.push_route(
                ["/feeds", "/feeds", "/about"][e.control.selected_index]
            )),
        ),
        controls=[
            ft.AppBar(title=ft.Text("Sobre"), bgcolor=ft.Colors.CYAN_50),
            ft.Column(
                controls=[
                    ft.Icon(ft.Icons.RSS_FEED, size=60, color=ft.Colors.CYAN_400),
                    ft.Text("CousCous", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                    ft.Text("Versão 0.1.0"),
                    ft.Divider(),
                    ft.Text(
                        "CousCous é um leitor de feeds RSS "
                        "construído com Python e Flet."
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
