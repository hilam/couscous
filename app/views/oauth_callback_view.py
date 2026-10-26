import asyncio
import logging
from urllib.parse import parse_qs, urlparse

import flet as ft
import httpx
from authlib.oauth2 import OAuth2Error

from app.services import oauth_service, user_service
from app.services.settings_service import apply_settings_to_page, get_settings
from app.views.explore_view import explore_view


async def oauth_callback_view(ctx) -> ft.View:
    page = ctx.page
    parsed = urlparse(page.route)
    params = parse_qs(parsed.query)

    code = params.get("code", [None])[0]
    state_param = params.get("state", [None])[0]

    if not code or not state_param:
        return await _error_view(page, "Par\u00e2metros OAuth inv\u00e1lidos")

    try:
        user_info = await oauth_service.handle_callback(page, code, state_param)
    except ValueError as ex:
        return await _error_view(page, str(ex))
    except (httpx.HTTPError, OAuth2Error, KeyError):
        logging.getLogger(__name__).exception("callback OAuth falhou")
        return await _error_view(
            page, "Falha ao concluir o login com o provedor"
        )

    user = await user_service.get_or_create_oauth_user(
        ctx.session,
        provider=user_info["provider"],
        oauth_id=user_info["oauth_id"],
        name=user_info["name"],
    )
    ctx.state.user = user
    if user.id is None:
        return await _error_view(page, "Erro interno: usuário sem ID")
    settings = await get_settings(ctx.session, user.id)
    ctx.state.theme_mode = settings.theme_mode
    ctx.state.font_scale = settings.font_scale
    apply_settings_to_page(page, settings.theme_mode, settings.font_scale)

    return await explore_view(ctx)


async def _error_view(page: ft.Page, message: str) -> ft.View:
    _task_refs: list = []
    return ft.View(
        route="/oauth/callback",
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=64, color=ft.Colors.RED_400),
                    ft.Text(
                        "Falha na autentica\u00e7\u00e3o",
                        theme_style=ft.TextThemeStyle.HEADLINE_SMALL,
                    ),
                    ft.Text(message, text_align=ft.TextAlign.CENTER),
                    ft.FilledButton(
                        "Voltar ao login",
                        on_click=lambda _: _task_refs.append(
                            asyncio.create_task(page.push_route("/login"))
                        ),
                    ),
                ],
                spacing=16,
            )
        ],
    )
