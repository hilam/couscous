from unittest.mock import AsyncMock, MagicMock, patch

import flet as ft
import pytest

from app.context import PageContext
from app.state import State
from app.views.feed_list_view import feed_list_view


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


def _auth_state():
    state = State()
    state.user = MagicMock()
    state.user.id = 1
    state.user.name = "testuser"
    return state


@pytest.mark.asyncio
async def test_feed_list_view_route():
    page = MagicMock()
    state = _auth_state()
    ctx = PageContext(page=page, state=state, session=AsyncMock())

    with patch("app.views.feed_list_view.list_feeds", AsyncMock(return_value=[])), \
         patch("app.views.feed_list_view.list_categories", AsyncMock(return_value=[])):
        view = await feed_list_view(ctx)

    assert view.route == "/feeds"


@pytest.mark.asyncio
async def test_feed_list_view_contains_appbar():
    page = MagicMock()
    state = _auth_state()
    ctx = PageContext(page=page, state=state, session=AsyncMock())

    with patch("app.views.feed_list_view.list_feeds", AsyncMock(return_value=[])), \
         patch("app.views.feed_list_view.list_categories", AsyncMock(return_value=[])):
        view = await feed_list_view(ctx)

    app_bars = _find_controls(view, ft.AppBar)
    assert len(app_bars) >= 1
    assert any("Meus Feeds" in (b.title.value or "") for b in app_bars)


@pytest.mark.asyncio
async def test_feed_list_view_contains_navigation_bar():
    page = MagicMock()
    state = _auth_state()
    ctx = PageContext(page=page, state=state, session=AsyncMock())

    with patch("app.views.feed_list_view.list_feeds", AsyncMock(return_value=[])), \
         patch("app.views.feed_list_view.list_categories", AsyncMock(return_value=[])):
        await feed_list_view(ctx)

    assert page.navigation_bar is not None
