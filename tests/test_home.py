from unittest.mock import MagicMock

import flet as ft
import pytest

from app.state import State
from app.views.home_view import home_view


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
async def test_home_view_route():
    page = MagicMock()
    state = State()
    view = await home_view(page, state)

    assert view.route == "/"


@pytest.mark.asyncio
async def test_home_view_contains_navigation_bar():
    page = MagicMock()
    state = State()
    await home_view(page, state)

    assert page.navigation_bar is not None


@pytest.mark.asyncio
async def test_home_view_contains_rss_feed_button():
    page = MagicMock()
    state = State()
    view = await home_view(page, state)

    buttons = _find_controls(view, ft.FilledButton)
    assert any("Ver meus feeds" in str(getattr(b, "content", "")) for b in buttons)
