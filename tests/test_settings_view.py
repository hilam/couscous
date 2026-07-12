from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.context import PageContext
from app.state import State
from app.views.settings_view import settings_view


@pytest.mark.asyncio
async def test_settings_view_renders(page_context):
    page_context.state.user = MagicMock()
    page_context.state.user.id = 1
    with patch("app.views.settings_view.get_settings", AsyncMock(return_value=MagicMock())):
        view = await settings_view(page_context)
    assert view.route == "/about"
