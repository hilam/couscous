from collections.abc import Awaitable, Callable
from dataclasses import dataclass

import asyncio

import flet as ft

from app.context import PageContext
from app.controls.nav_bar import set_navbar
from app.services.cleanup_service import purge_older_than
from app.services.settings_service import get_settings
from app.state import State
from app.views.category_list_view import category_list_view
from app.views.entry_list_view import entry_list_view
from app.views.entry_view import entry_view
from app.views.explore_view import explore_view
from app.views.feed_list_view import feed_list_view
from app.views.home_view import home_view
from app.views.login_view import login_view
from app.views.oauth_callback_view import oauth_callback_view
from app.views.register_view import register_view
from app.views.settings_view import settings_view
from database.service.database import get_db_session, init_async_db


@dataclass
class _Route:
    prefix: str
    handler: Callable[..., Awaitable[ft.View]]
    is_public: bool = False


# NOTE: order matters — specific prefixes (/feed/, /entry/) must come before
# generic ones (/) so prefix-based matching is correct.
_ROUTES: list[_Route] = [
    _Route("/login", login_view, is_public=True),
    _Route("/register", register_view, is_public=True),
    _Route("/oauth/callback", oauth_callback_view, is_public=True),
    _Route("/about", settings_view),
    _Route("/feeds", feed_list_view),
    _Route("/feed/", entry_list_view),
    _Route("/entry/", entry_view),
    _Route("/categories", category_list_view),
    _Route("/", explore_view),
]

_FALLBACK_HANDLER = home_view


async def _auto_cleanup(page: ft.Page, user_id: int) -> None:
    """Run automatic cleanup on startup if the user has auto_cleanup_days set."""
    async with get_db_session() as session:
        settings = await get_settings(session, user_id)
        days = settings.auto_cleanup_days
        if days is None:
            return
        removed = await purge_older_than(session, user_id, days)

    if removed > 0:
        page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(f"\U0001f9f9 Limpeza autom\u00e1tica: {removed} {'artigo' if removed == 1 else 'artigos'} antigo{'s' if removed != 1 else ''} removido{'s' if removed != 1 else ''}."),
                bgcolor=ft.Colors.GREEN_400,
            )
        )
        page.update()


def _match_route(route: str) -> _Route | None:
    for r in _ROUTES:
        if r.prefix.endswith("/"):
            if route.startswith(r.prefix):
                return r
        elif route == r.prefix:
            return r
    return None


async def _invoke_handler(route_def: _Route, route: str, ctx: PageContext) -> ft.View:
    handler = route_def.handler
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
    async with get_db_session() as session:
        ctx = PageContext(
            page=page,
            state=state,
            session=session,
            _session_factory=get_db_session,
        )
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
            async with get_db_session() as session:
                ctx = PageContext(
                    page=page,
                    state=state,
                    session=session,
                    _session_factory=get_db_session,
                )
                v = await login_view(ctx)
        elif matched is not None:
            v = await _build_and_invoke(matched, route, page, state)
        else:
            async with get_db_session() as session:
                ctx = PageContext(page=page, state=state, session=session)
                v = await _FALLBACK_HANDLER(ctx)

        page.views.append(v)
        if route not in {"/login", "/register"} and not route.startswith(
            "/oauth/callback"
        ):
            set_navbar(page)
        page.update()

        # Start auto-cleanup once after login
        if state.user and not state._cleanup_triggered and state.user.id:
            state._cleanup_triggered = True
            asyncio.create_task(_auto_cleanup(page, int(state.user.id)))

    page.on_route_change = on_route_change
    await page.push_route("/login")
