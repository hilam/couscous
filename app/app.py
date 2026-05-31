import flet as ft

from app.state import State
from app.views.about_view import about_view
from app.views.entry_list_view import entry_list_view
from app.views.entry_view import entry_view
from app.views.feed_list_view import feed_list_view
from app.views.home_view import home_view
from app.views.login_view import login_view


async def app_run(page: ft.Page):
    page.title = "CousCous - Leitor de RSS"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.CYAN_400,
            secondary=ft.Colors.BLUE_400,
        ),
    )
    page.padding = 0

    state = State()
    page.session.store.set("state", state)

    async def on_route_change(e: ft.RouteChangeEvent):
        page.views.clear()
        route = e.route

        if route == "/login" or (not state.user and route != "/about"):
            v = await login_view(page, state)
        elif route in {"/feeds", "/"}:
            v = await feed_list_view(page, state)
        elif route.startswith("/feed/"):
            state.active_feed_url = route[len("/feed/") :]
            v = await entry_list_view(page, state)
        elif route.startswith("/entry/"):
            entry_id = int(route[len("/entry/") :])
            v = await entry_view(page, state, entry_id)
        elif route == "/about":
            v = await about_view(page, state)
        else:
            v = await home_view(page, state)

        page.views.append(v)
        page.update()

    page.on_route_change = on_route_change
    page.go("/login")
