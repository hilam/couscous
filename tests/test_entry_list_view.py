from unittest.mock import AsyncMock, MagicMock, patch

import flet as ft
import pytest

from app.context import PageContext
from app.state import State
from app.views.entry_list_view import entry_list_view


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


def _auth_state(feed_url="https://example.com/rss"):
    state = State()
    state.user = MagicMock()
    state.user.id = 1
    state.user.name = "testuser"
    state.active_feed_url = feed_url
    return state


def _mock_context(page, state, feed_mock):
    session = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = feed_mock
    session.execute.return_value = result_mock
    return PageContext(page=page, state=state, session=session)


@pytest.mark.asyncio
async def test_entry_list_view_route():
    page = MagicMock()
    state = _auth_state()

    mock_feed = MagicMock()
    mock_feed.title = "Test Feed"
    ctx = _mock_context(page, state, mock_feed)

    with patch("app.views.entry_list_view.list_entries", AsyncMock(return_value=[])):
        view = await entry_list_view(ctx)

    assert "/feed/https://example.com/rss" in view.route


@pytest.mark.asyncio
async def test_entry_list_view_contains_appbar():
    page = MagicMock()
    state = _auth_state()

    mock_feed = MagicMock()
    mock_feed.title = "Test Feed Title"
    ctx = _mock_context(page, state, mock_feed)

    with patch("app.views.entry_list_view.list_entries", AsyncMock(return_value=[])):
        view = await entry_list_view(ctx)

    app_bars = _find_controls(view, ft.AppBar)
    assert len(app_bars) >= 1
    assert any("Test Feed Title" in (b.title.value or "") for b in app_bars)


@pytest.mark.asyncio
async def test_entry_list_view_empty_state():
    page = MagicMock()
    state = _auth_state()

    mock_feed = MagicMock()
    mock_feed.title = "Test Feed"
    ctx = _mock_context(page, state, mock_feed)

    with patch("app.views.entry_list_view.list_entries", AsyncMock(return_value=[])):
        view = await entry_list_view(ctx)

    containers = _find_controls(view, ft.Container)
    texts = [c for c in _find_controls(view, ft.Text)]
    empty_texts = [t for t in texts if "Nenhum artigo" in (t.value or "")]
    assert len(empty_texts) >= 1
