import flet as ft
import pytest

from app.views.home_view import home_view


@pytest.mark.asyncio
async def test_home_view_renders(page_context):
    """Smoke test: view renders without error and has correct route."""
    view = await home_view(page_context)
    assert view.route == "/"
