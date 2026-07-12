import pytest

from app.views.register_view import register_view


@pytest.mark.asyncio
async def test_register_view_renders(page_context):
    view = await register_view(page_context)
    assert view.route == "/register"
