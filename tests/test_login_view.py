import flet as ft
import pytest

from app.views.login_view import login_view


@pytest.mark.asyncio
async def test_login_view_route(page_context):
    view = await login_view(page_context)

    assert view.route == "/login"


@pytest.mark.asyncio
async def test_login_view_contains_username_password_fields(page_context):
    view = await login_view(page_context)

    textfields = _find_controls(view, ft.TextField)
    assert len(textfields) >= 2
    labels = [tf.label for tf in textfields if hasattr(tf, "label")]
    assert any("Nome de usuário" in l for l in labels if l)
    assert any("Senha" in l for l in labels if l)


@pytest.mark.asyncio
async def test_login_view_contains_login_button(page_context):
    view = await login_view(page_context)

    buttons = _find_controls(view, ft.FilledButton)
    assert len(buttons) >= 1
    assert any("Entrar" in str(getattr(b, "content", "")) for b in buttons)


@pytest.mark.asyncio
async def test_login_view_register_link(page_context):
    view = await login_view(page_context)

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
