from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.context import PageContext
from app.state import State
from app.views.entry_view import entry_view


@pytest.mark.asyncio
async def test_entry_view_renders():
    state = State()
    state.user = MagicMock()
    state.user.id = 1
    state.user.name = "testuser"
    ctx = PageContext(page=MagicMock(), state=state, session=AsyncMock())

    with patch("app.views.entry_view.get_entry", AsyncMock(return_value=None)), \
         patch("app.views.entry_view.mark_read", AsyncMock()):
        view = await entry_view(ctx, 1)

    assert "/entry/1" in view.route
