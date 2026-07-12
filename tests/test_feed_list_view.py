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
