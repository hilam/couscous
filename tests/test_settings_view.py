from unittest.mock import AsyncMock, MagicMock, patch

import flet as ft
import pytest

from app.context import PageContext
from app.state import State
from app.views.settings_view import settings_view


@pytest.mark.asyncio
async def test_settings_view_renders(page_context):
    page_context.state.user = MagicMock()
    page_context.state.user.id = 1
    with patch("app.views.settings_view.get_settings", AsyncMock(return_value=MagicMock())):
        view = await settings_view(page_context)
    assert view.route == "/about"


def _walk(ctrl):
    yield ctrl
    for child in getattr(ctrl, "controls", None) or []:
        yield from _walk(child)
    inner = getattr(ctrl, "content", None)
    if isinstance(inner, ft.Control):
        yield from _walk(inner)


@pytest.mark.asyncio
async def test_sobre_dialog_close_button_pops_dialog(page_context):
    """Regression: page.close_dialog não existe no Flet 1.x — o botão
    Fechar do diálogo Sobre deve chamar page.pop_dialog sem AttributeError."""
    page_context.state.user = MagicMock()
    page_context.state.user.id = 1
    settings = MagicMock()
    settings.auto_cleanup_days = None
    settings.theme_mode = "light"
    settings.font_scale = 1.0
    with patch("app.views.settings_view.get_settings", AsyncMock(return_value=settings)):
        view = await settings_view(page_context)

    sobre_btn = next(
        (
            c
            for c in _walk(view)
            if getattr(c, "on_click", None) is not None
            and getattr(c, "content", None) == "Sobre"
        ),
        None,
    )
    assert sobre_btn is not None
    await sobre_btn.on_click(MagicMock())

    page_context.page.show_dialog.assert_called_once()
    dlg = page_context.page.show_dialog.call_args[0][0]
    fechar_btn = next(
        (a for a in dlg.actions if getattr(a, "content", None) == "Fechar"), None
    )
    assert fechar_btn is not None
    fechar_btn.on_click(MagicMock())
    page_context.page.pop_dialog.assert_called_once()
