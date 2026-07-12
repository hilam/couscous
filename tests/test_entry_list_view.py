from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.context import PageContext
from app.state import State
from app.views.entry_list_view import entry_list_view


def _auth_state(feed_url="https://example.com/rss"):
    state = State()
    state.user = MagicMock()
    state.user.id = 1
    state.user.name = "testuser"
    state.active_feed_url = feed_url
    return state


@pytest.mark.asyncio
async def test_entry_list_view_renders():
    state = _auth_state()
    page = MagicMock()

    mock_feed = MagicMock()
    mock_feed.title = "Test Feed"
    session = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = mock_feed
    session.execute.return_value = result_mock
    ctx = PageContext(page=page, state=state, session=session)

    with patch("app.views.entry_list_view.list_entries", AsyncMock(return_value=[])):
        view = await entry_list_view(ctx)

    assert "/feed/https://example.com/rss" in view.route
