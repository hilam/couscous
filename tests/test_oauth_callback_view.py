import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import flet as ft
import httpx
import pytest
from authlib.oauth2 import OAuth2Error

from app.views.oauth_callback_view import oauth_callback_view

_GENERIC_MSG = "Falha ao concluir o login com o provedor"


def _walk(ctrl):
    yield ctrl
    for child in getattr(ctrl, "controls", None) or []:
        yield from _walk(child)


def _text_values(view):
    return [c.value for c in _walk(view) if isinstance(c, ft.Text)]


def _find_button(view, label):
    for c in _walk(view):
        if isinstance(c, ft.Button) and getattr(c, "content", None) == label:
            return c
    return None


@pytest.fixture
def oauth_ctx(page_context):
    page_context.page.route = "/oauth/callback?code=c1&state=s1"
    page_context.page.push_route = AsyncMock()
    return page_context


async def _error_view_for(oauth_ctx, exc):
    with patch(
        "app.views.oauth_callback_view.oauth_service.handle_callback",
        AsyncMock(side_effect=exc),
    ):
        return await oauth_callback_view(oauth_ctx)


@pytest.mark.asyncio
async def test_value_error_keeps_friendly_message(oauth_ctx):
    view = await _error_view_for(oauth_ctx, ValueError("Sessão OAuth inválida"))
    assert isinstance(view, ft.View)
    assert "Sessão OAuth inválida" in _text_values(view)


@pytest.mark.asyncio
async def test_connect_error_returns_error_view(oauth_ctx):
    view = await _error_view_for(oauth_ctx, httpx.ConnectError("provider offline"))
    assert isinstance(view, ft.View)
    assert _GENERIC_MSG in _text_values(view)


@pytest.mark.asyncio
async def test_http_status_error_returns_error_view(oauth_ctx):
    request = MagicMock()
    response = MagicMock(status_code=500)
    view = await _error_view_for(
        oauth_ctx, httpx.HTTPStatusError("boom", request=request, response=response)
    )
    assert isinstance(view, ft.View)
    assert _GENERIC_MSG in _text_values(view)


@pytest.mark.asyncio
async def test_oauth2_error_returns_error_view(oauth_ctx):
    view = await _error_view_for(oauth_ctx, OAuth2Error("invalid_grant"))
    assert isinstance(view, ft.View)
    assert _GENERIC_MSG in _text_values(view)


@pytest.mark.asyncio
async def test_key_error_returns_error_view(oauth_ctx):
    view = await _error_view_for(oauth_ctx, KeyError("access_token"))
    assert isinstance(view, ft.View)
    assert _GENERIC_MSG in _text_values(view)


@pytest.mark.asyncio
async def test_back_to_login_button_awaited_push_route(oauth_ctx):
    view = await _error_view_for(oauth_ctx, ValueError("qualquer"))
    button = _find_button(view, "Voltar ao login")
    assert button is not None
    button.on_click(MagicMock())
    await asyncio.sleep(0)
    oauth_ctx.page.push_route.assert_awaited_with("/login")
