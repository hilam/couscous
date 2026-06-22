import asyncio

import flet as ft

_DESTINATIONS = [
    ft.NavigationBarDestination(icon=ft.Icons.HOME, label="In\u00edcio"),
    ft.NavigationBarDestination(icon=ft.Icons.RSS_FEED, label="Feeds"),
    ft.NavigationBarDestination(icon=ft.Icons.FOLDER, label="Categorias"),
    ft.NavigationBarDestination(icon=ft.Icons.INFO, label="Sobre"),
]

_ROUTE_INDICES: dict[str, int] = {
    "/": 0,
    "/feeds": 1,
    "/feed/": 1,
    "/entries": 1,
    "/entry/": 1,
    "/categories": 2,
    "/about": 3,
}

_INDEX_ROUTES = ["/feeds", "/feeds", "/categories", "/about"]


def set_navbar(page: ft.Page) -> None:
    selected_index = _resolve_index(page.route)
    page.navigation_bar = ft.NavigationBar(
        destinations=_DESTINATIONS,
        selected_index=selected_index,
        on_change=lambda e: asyncio.create_task(
            page.push_route(_INDEX_ROUTES[e.control.selected_index])
        ),
    )


def _resolve_index(route: str) -> int:
    for prefix, index in _ROUTE_INDICES.items():
        if route.startswith(prefix):
            return index
    return 0
