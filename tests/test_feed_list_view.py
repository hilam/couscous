from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.context import PageContext
from app.state import State
from app.views.feed_list_view import feed_list_view


@pytest.mark.asyncio
async def test_feed_list_view_renders():
    state = State()
    state.user = MagicMock()
    state.user.id = 1
    state.user.name = "testuser"
    ctx = PageContext(page=MagicMock(), state=state, session=AsyncMock())

    with patch("app.views.feed_list_view.list_feeds", AsyncMock(return_value=[])), \
         patch("app.views.feed_list_view.list_categories", AsyncMock(return_value=[])):
        view = await feed_list_view(ctx)

    assert view.route == "/feeds"


def _refresh_button(view):
    app_bar = view.controls[0]
    return app_bar.actions[1]


@pytest.mark.asyncio
async def test_refresh_guard_blocks_reentrancy():
    """(d) segundo disparo com state.loading=True não chama refresh_all_feeds."""
    state = State()
    state.user = MagicMock()
    state.user.id = 1
    state.user.name = "testuser"
    ctx = PageContext(page=MagicMock(), state=state, session=AsyncMock())

    with patch("app.views.feed_list_view.list_feeds", AsyncMock(return_value=[])), \
         patch("app.views.feed_list_view.list_categories", AsyncMock(return_value=[])):
        view = await feed_list_view(ctx)

    btn = _refresh_button(view)
    state.loading = True
    refresh_mock = AsyncMock()
    with patch("app.views.feed_list_view.refresh_all_feeds", refresh_mock):
        await btn.on_click(MagicMock())

    refresh_mock.assert_not_awaited()
    assert state.loading is True


@pytest.mark.asyncio
async def test_refresh_button_disabled_while_loading():
    state = State()
    state.user = MagicMock()
    state.user.id = 1
    state.user.name = "testuser"
    state.loading = True
    ctx = PageContext(page=MagicMock(), state=state, session=AsyncMock())

    with patch("app.views.feed_list_view.list_feeds", AsyncMock(return_value=[])), \
         patch("app.views.feed_list_view.list_categories", AsyncMock(return_value=[])):
        view = await feed_list_view(ctx)

    assert _refresh_button(view).disabled is True
