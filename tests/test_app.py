from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.app import app_run


@pytest.fixture
def mock_page():
    page = MagicMock()
    page.session.store = MagicMock()
    page.views = []
    page.push_route = AsyncMock()
    return page


@pytest.mark.asyncio
async def test_app_run_configures_page_title(mock_page):
    mock_page.theme = MagicMock()
    with patch("app.app.init_async_db", AsyncMock()):
        await app_run(mock_page)

    assert mock_page.title == "CousCous - Leitor de RSS"
    assert mock_page.theme_mode is not None
    assert mock_page.padding == 0


@pytest.mark.asyncio
async def test_app_run_stores_state(mock_page):
    mock_page.theme = MagicMock()
    with patch("app.app.init_async_db", AsyncMock()):
        await app_run(mock_page)

    mock_page.session.store.set.assert_called_once()
    args, _ = mock_page.session.store.set.call_args
    assert args[0] == "state"


@pytest.mark.asyncio
async def test_app_run_pushes_initial_login_route(mock_page):
    mock_page.theme = MagicMock()
    with patch("app.app.init_async_db", AsyncMock()):
        await app_run(mock_page)

    mock_page.push_route.assert_called_once_with("/login")


@pytest.mark.asyncio
async def test_app_run_sets_on_route_change(mock_page):
    mock_page.theme = MagicMock()
    with patch("app.app.init_async_db", AsyncMock()):
        await app_run(mock_page)

    assert callable(mock_page.on_route_change)


@pytest.mark.asyncio
async def test_route_dispatch_login(mock_page):
    mock_page.theme = MagicMock()
    view_mock = MagicMock()
    mock_login_view = AsyncMock(return_value=view_mock)
    mock_page.push_route = AsyncMock()

    with (
        patch("app.app.init_async_db", AsyncMock()),
        patch("app.app.login_view", mock_login_view),
        patch("app.app.feed_list_view"),
        patch("app.app.entry_list_view"),
        patch("app.app.entry_view"),
        patch("app.app.register_view"),
        patch("app.app.about_view"),
        patch("app.app.home_view"),
        patch("app.app.get_db_session"),
    ):
        await app_run(mock_page)
        event = MagicMock()
        event.route = "/login"
        await mock_page.on_route_change(event)
        mock_login_view.assert_awaited_once()
        assert view_mock in mock_page.views


@pytest.mark.asyncio
async def test_route_dispatch_feed_list_when_authenticated(mock_page):
    mock_page.theme = MagicMock()
    view_mock = MagicMock()

    with (
        patch("app.app.init_async_db", AsyncMock()),
        patch("app.app.State") as MockState,
    ):
        mock_state = MagicMock()
        mock_state.user = MagicMock()
        mock_state.user.id = 1
        mock_state.user.name = "testuser"
        mock_state.active_feed_url = None
        MockState.return_value = mock_state

        mock_feed_list_view = AsyncMock(return_value=view_mock)

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = AsyncMock()
        mock_cm.__aexit__.return_value = None

        with (
            patch("app.app.feed_list_view", mock_feed_list_view),
            patch("app.app.login_view", AsyncMock()),
            patch("app.app.entry_list_view"),
            patch("app.app.entry_view"),
            patch("app.app.register_view"),
            patch("app.app.about_view"),
            patch("app.app.home_view"),
            patch("app.app.get_db_session", return_value=mock_cm),
        ):
            await app_run(mock_page)
            event = MagicMock()
            event.route = "/feeds"
            await mock_page.on_route_change(event)
            mock_feed_list_view.assert_awaited_once()
            assert view_mock in mock_page.views


@pytest.mark.asyncio
async def test_route_dispatch_entry_list_sets_active_url(mock_page):
    mock_page.theme = MagicMock()

    with (
        patch("app.app.init_async_db", AsyncMock()),
        patch("app.app.State") as MockState,
    ):
        mock_state = MagicMock()
        mock_state.user = MagicMock()
        mock_state.user.id = 1
        MockState.return_value = mock_state
        view_mock = MagicMock()
        mock_entry_list_view = AsyncMock(return_value=view_mock)

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = AsyncMock()
        mock_cm.__aexit__.return_value = None

        with (
            patch("app.app.entry_list_view", mock_entry_list_view),
            patch("app.app.login_view", AsyncMock()),
            patch("app.app.feed_list_view"),
            patch("app.app.entry_view"),
            patch("app.app.register_view"),
            patch("app.app.about_view"),
            patch("app.app.home_view"),
            patch("app.app.get_db_session", return_value=mock_cm),
        ):
            await app_run(mock_page)
            event = MagicMock()
            event.route = "/feed/https://example.com/rss"
            await mock_page.on_route_change(event)
            assert mock_state.active_feed_url == "https://example.com/rss"
            mock_entry_list_view.assert_awaited_once()


@pytest.mark.asyncio
async def test_route_dispatch_entry_view(mock_page):
    mock_page.theme = MagicMock()

    with (
        patch("app.app.init_async_db", AsyncMock()),
        patch("app.app.State") as MockState,
    ):
        mock_state = MagicMock()
        mock_state.user = MagicMock()
        mock_state.user.id = 1
        MockState.return_value = mock_state
        view_mock = MagicMock()
        mock_entry_view = AsyncMock(return_value=view_mock)

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = AsyncMock()
        mock_cm.__aexit__.return_value = None

        with (
            patch("app.app.entry_view", mock_entry_view),
            patch("app.app.login_view", AsyncMock()),
            patch("app.app.feed_list_view"),
            patch("app.app.entry_list_view"),
            patch("app.app.register_view"),
            patch("app.app.about_view"),
            patch("app.app.home_view"),
            patch("app.app.get_db_session", return_value=mock_cm),
        ):
            await app_run(mock_page)
            event = MagicMock()
            event.route = "/entry/42"
            await mock_page.on_route_change(event)
            mock_entry_view.assert_awaited_once()
            args, _ = mock_entry_view.await_args
            assert args[1] == 42


@pytest.mark.asyncio
async def test_unauthenticated_redirects_to_login(mock_page):
    mock_page.theme = MagicMock()
    view_mock = MagicMock()
    mock_login_view = AsyncMock(return_value=view_mock)

    with (
        patch("app.app.init_async_db", AsyncMock()),
        patch("app.app.login_view", mock_login_view),
        patch("app.app.feed_list_view"),
        patch("app.app.entry_list_view"),
        patch("app.app.entry_view"),
        patch("app.app.register_view"),
        patch("app.app.about_view"),
        patch("app.app.home_view"),
        patch("app.app.get_db_session"),
    ):
        await app_run(mock_page)
        event = MagicMock()
        event.route = "/feeds"
        await mock_page.on_route_change(event)
        mock_login_view.assert_awaited_once()


@pytest.mark.asyncio
async def test_public_routes_allowed_without_auth(mock_page):
    mock_page.theme = MagicMock()

    for public_route, view_name in [
        ("/about", "about_view"),
        ("/register", "register_view"),
    ]:
        page = MagicMock()
        page.session.store = MagicMock()
        page.views = []
        page.theme = MagicMock()
        page.push_route = AsyncMock()
        view_mock = MagicMock()
        mock_view_func = AsyncMock(return_value=view_mock)

        view_patches = {
            "login_view": AsyncMock(),
            "feed_list_view": AsyncMock(),
            "entry_list_view": AsyncMock(),
            "entry_view": AsyncMock(),
            "register_view": AsyncMock(),
            "about_view": AsyncMock(),
            "home_view": AsyncMock(),
        }
        view_patches[view_name] = mock_view_func

        with (
            patch("app.app.init_async_db", AsyncMock()),
            patch(f"app.app.{view_name}", mock_view_func),
            patch("app.app.login_view", view_patches["login_view"]),
            patch("app.app.feed_list_view", view_patches["feed_list_view"]),
            patch("app.app.entry_list_view", view_patches["entry_list_view"]),
            patch("app.app.entry_view", view_patches["entry_view"]),
            patch("app.app.register_view", view_patches["register_view"]),
            patch("app.app.about_view", view_patches["about_view"]),
            patch("app.app.home_view", view_patches["home_view"]),
            patch("app.app.get_db_session"),
        ):
            await app_run(page)
            event = MagicMock()
            event.route = public_route
            await page.on_route_change(event)
            mock_view_func.assert_awaited_once()
            assert view_mock in page.views
