import flet as ft

from app.context import PageContext
from app.controls.nav_bar import set_navbar
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
from database.service.database import get_db_session, init_async_db


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
            ctx = PageContext(page=page, state=state, _session_factory=get_db_session)
            v = await login_view(ctx)
        elif route in {"/feeds", "/"}:
            async with get_db_session() as session:
                ctx = PageContext(
                    page=page,
                    state=state,
                    session=session,
                    _session_factory=get_db_session,
                )
                v = await feed_list_view(ctx)
        elif route.startswith("/feed/"):
            state.active_feed_url = route[len("/feed/") :]
            async with get_db_session() as session:
                ctx = PageContext(
                    page=page,
                    state=state,
                    session=session,
                    _session_factory=get_db_session,
                )
                v = await entry_list_view(ctx)
        elif route.startswith("/entry/"):
            entry_id = int(route[len("/entry/") :])
            async with get_db_session() as session:
                ctx = PageContext(
                    page=page,
                    state=state,
                    session=session,
                    _session_factory=get_db_session,
                )
                v = await entry_view(ctx, entry_id)
        elif route.startswith("/oauth/callback"):
            async with get_db_session() as session:
                ctx = PageContext(
                    page=page,
                    state=state,
                    session=session,
                    _session_factory=get_db_session,
                )
                v = await oauth_callback_view(ctx)
        elif route == "/register":
            ctx = PageContext(page=page, state=state, _session_factory=get_db_session)
            v = await register_view(ctx)
        elif route == "/categories":
            async with get_db_session() as session:
                ctx = PageContext(
                    page=page,
                    state=state,
                    session=session,
                    _session_factory=get_db_session,
                )
                v = await category_list_view(ctx)
        elif route == "/about":
            ctx = PageContext(page=page, state=state)
            v = await about_view(ctx)
        else:
            ctx = PageContext(page=page, state=state)
            v = await home_view(ctx)

        page.views.append(v)
        if route not in {"/login", "/register"} and not route.startswith(
            "/oauth/callback"
        ):
            set_navbar(page)
        page.update()

    page.on_route_change = on_route_change
    await page.push_route("/login")
