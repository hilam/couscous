import pytest

from app.views.login_view import login_view


@pytest.mark.asyncio
async def test_login_view_renders(page_context):
    view = await login_view(page_context)
    assert view.route == "/login"
