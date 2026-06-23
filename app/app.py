from collections.abc import Awaitable, Callable
from dataclasses import dataclass

import flet as ft

from app.context import PageContext
from app.controls.nav_bar import set_navbar
from app.state import State
from app.views.home_view import home_view
from app.views.login_view import login_view
from database.service.database import get_db_session, init_async_db


@dataclass
class _Route:
    prefix: str
    handler_name: str
    requires_session: bool
    is_public: bool = False


# NOTE: order matters — specific prefixes (/feed/, /entry/) must come before
# generic ones (/) so prefix-based matching is correct.
_ROUTES: list[_Route] = [
    _Route("/login", "login_view", requires_session=False, is_public=True),
    _Route("/register", "register_view", requires_session=False, is_public=True),
    _Route(
        "/oauth/callback",
        "oauth_callback_view",
        requires_session=True,
        is_public=True,
    ),
    _Route("/about", "about_view", requires_session=False, is_public=True),
    _Route("/feeds", "feed_list_view", requires_session=True),
    _Route("/feed/", "entry_list_view", requires_session=True),
    _Route("/entry/", "entry_view", requires_session=True),
    _Route("/categories", "category_list_view", requires_session=True),
    _Route("/", "feed_list_view", requires_session=True),
]

_FALLBACK_HANDLER = home_view


def _match_route(route: str) -> _Route | None:
    for r in _ROUTES:
        if r.prefix.endswith("/"):
            if route.startswith(r.prefix):
                return r
        elif route == r.prefix:
            return r
    return None


def _resolve_handler(name: str) -> Callable[..., Awaitable[ft.View]]:
    return globals()[name]


async def _invoke_handler(route_def: _Route, route: str, ctx: PageContext) -> ft.View:
    handler = _resolve_handler(route_def.handler_name)
    if route_def.prefix == "/feed/":
        ctx.state.active_feed_url = route[len("/feed/") :]
        return await handler(ctx)
    if route_def.prefix == "/entry/":
        entry_id = int(route[len("/entry/") :])
        return await handler(ctx, entry_id)  # type: ignore[call-arg]
    return await handler(ctx)


async def _build_and_invoke(
    route_def: _Route, route: str, page: ft.Page, state: State
) -> ft.View:
    if route_def.requires_session:
        async with get_db_session() as session:
            ctx = PageContext(
                page=page,
                state=state,
                session=session,
                _session_factory=get_db_session,
            )
            return await _invoke_handler(route_def, route, ctx)
    ctx = PageContext(page=page, state=state, _session_factory=get_db_session)
    return await _invoke_handler(route_def, route, ctx)


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

        matched = _match_route(route)

        if route == "/login" or (
            not state.user and (matched is None or not matched.is_public)
        ):
            ctx = PageContext(page=page, state=state, _session_factory=get_db_session)
            v = await login_view(ctx)
        elif matched is not None:
            v = await _build_and_invoke(matched, route, page, state)
        else:
            ctx = PageContext(page=page, state=state)
            v = await _FALLBACK_HANDLER(ctx)

        page.views.append(v)
        if route not in {"/login", "/register"} and not route.startswith(
            "/oauth/callback"
        ):
            set_navbar(page)
        page.update()

    page.on_route_change = on_route_change
    await page.push_route("/login")
