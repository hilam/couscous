from unittest.mock import MagicMock

import flet as ft
import pytest

from app.context import PageContext
from app.services.user_service import login, register
from app.state import State
from app.views.register_view import register_view


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


@pytest.mark.asyncio
async def test_register_view_route():
    page = MagicMock()
    state = State()
    ctx = PageContext(page=page, state=state)
    view = await register_view(ctx)

    assert view.route == "/register"


@pytest.mark.asyncio
async def test_register_view_contains_fields():
    page = MagicMock()
    state = State()
    ctx = PageContext(page=page, state=state)
    view = await register_view(ctx)

    textfields = _find_controls(view, ft.TextField)
    labels = [tf.label for tf in textfields if hasattr(tf, "label")]
    assert any("Nome de usuário" in (l or "") for l in labels)
    assert any("Senha" in (l or "") for l in labels)


@pytest.mark.asyncio
async def test_register_view_contains_register_button():
    page = MagicMock()
    state = State()
    ctx = PageContext(page=page, state=state)
    view = await register_view(ctx)

    buttons = _find_controls(view, ft.FilledButton)
    assert any("Registrar" in str(getattr(b, "content", "")) for b in buttons)


@pytest.mark.asyncio
async def test_registration_then_login_flow(db_session):
    user = await register(db_session, "newuser", "secret123")
    assert user.name == "newuser"

    logged_in = await login(db_session, "newuser", "secret123")
    assert logged_in is not None
    assert logged_in.name == "newuser"


@pytest.mark.asyncio
async def test_register_duplicate_username(db_session):
    await register(db_session, "dupuser", "pass1")
    with pytest.raises(ValueError, match="Nome de usuário já existe"):
        await register(db_session, "dupuser", "pass2")
