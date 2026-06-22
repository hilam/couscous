from unittest.mock import AsyncMock, MagicMock, patch

import flet as ft
import pytest

from app.context import PageContext
from app.state import State
from app.views.login_view import login_view


@pytest.mark.asyncio
async def test_login_view_route():
    page = MagicMock()
    state = State()
    ctx = PageContext(page=page, state=state)
    view = await login_view(ctx)

    assert view.route == "/login"


@pytest.mark.asyncio
async def test_login_view_contains_username_password_fields():
    page = MagicMock()
    state = State()
    ctx = PageContext(page=page, state=state)
    view = await login_view(ctx)

    textfields = _find_controls(view, ft.TextField)
    assert len(textfields) >= 2
    labels = [tf.label for tf in textfields if hasattr(tf, "label")]
    assert any("Nome de usuário" in l for l in labels if l)
    assert any("Senha" in l for l in labels if l)


@pytest.mark.asyncio
async def test_login_view_contains_login_button():
    page = MagicMock()
    state = State()
    ctx = PageContext(page=page, state=state)
    view = await login_view(ctx)

    buttons = _find_controls(view, ft.FilledButton)
    assert len(buttons) >= 1
    assert any("Entrar" in str(getattr(b, "content", "")) for b in buttons)


@pytest.mark.asyncio
async def test_login_view_register_link():
    page = MagicMock()
    state = State()
    ctx = PageContext(page=page, state=state)
    view = await login_view(ctx)

    text_buttons = _find_controls(view, ft.TextButton)
    assert any("Criar conta" in str(getattr(b, "content", "")) for b in text_buttons)


def _find_controls(control, control_type):
    result = []
    if isinstance(control, control_type):
        result.append(control)
    if hasattr(control, "controls") and control.controls:
        for c in control.controls:
            result.extend(_find_controls(c, control_type))
    if hasattr(control, "content") and control.content:
        result.extend(_find_controls(control.content, control_type))
    return result
