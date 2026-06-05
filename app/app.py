import flet as ft

from app.state import State
from app.views.about_view import about_view
from app.views.category_list_view import category_list_view
from app.views.entry_list_view import entry_list_view
from app.views.entry_view import entry_view
from app.views.feed_list_view import feed_list_view
from app.views.home_view import home_view
from app.views.login_view import login_view
from app.views.oauth_callback_view import oauth_callback_view
from app.views.register_view import register_view
from database.service.database import init_async_db


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

    await init_async_db()

    state = State()
    page.session.store.set("state", state)

    async def on_route_change(e: ft.RouteChangeEvent):
        page.views.clear()
        route = e.route

        is_public = route in {"/about", "/register"} or route.startswith(
            "/oauth/callback"
        )
        if route == "/login" or (not state.user and not is_public):
            v = await login_view(page, state)
        elif route in {"/feeds", "/"}:
            v = await feed_list_view(page, state)
        elif route.startswith("/feed/"):
            state.active_feed_url = route[len("/feed/") :]
            v = await entry_list_view(page, state)
        elif route.startswith("/entry/"):
            entry_id = int(route[len("/entry/") :])
            v = await entry_view(page, state, entry_id)
        elif route.startswith("/oauth/callback"):
            v = await oauth_callback_view(page, state)
        elif route == "/register":
            v = await register_view(page, state)
        elif route == "/categories":
            v = await category_list_view(page, state)
        elif route == "/about":
            v = await about_view(page, state)
        else:
            v = await home_view(page, state)

        page.views.append(v)
        page.update()

    page.on_route_change = on_route_change
    await page.push_route("/login")
