import flet as ft
import pytest

from unittest.mock import AsyncMock, MagicMock

from app.views.settings_view import settings_view


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


def _mock_session(page_context):
    """Configure session mock to return no stored settings (defaults)."""
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    page_context.session.execute = AsyncMock(return_value=result_mock)


@pytest.mark.asyncio
async def test_settings_view_route(page_context):
    page_context.state.user = MagicMock(id=1)
    _mock_session(page_context)
    view = await settings_view(page_context)

    assert view.route == "/about"


@pytest.mark.asyncio
async def test_settings_view_contains_navigation_bar(page_context):
    page_context.state.user = MagicMock(id=1)
    _mock_session(page_context)
    await settings_view(page_context)

    assert page_context.page.navigation_bar is not None
