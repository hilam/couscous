from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import flet as ft
import pytest

from app.state import State
from app.views.entry_view import entry_view


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


def _make_entry(**overrides):
    now = datetime.now()
    entry = MagicMock()
    entry.id = 1
    entry.feed = "https://example.com/rss"
    entry.title = "Test Article"
    entry.link = "https://example.com/article1"
    entry.summary = "Test summary"
    entry.content = "<p>Test content</p>"
    entry.author = "Test Author"
    entry.published = now
    entry.important = 0
    entry.read = 0
    for k, v in overrides.items():
        setattr(entry, k, v)
    return entry


def _auth_state():
    state = State()
    state.user = MagicMock()
    state.user.id = 1
    state.user.name = "testuser"
    return state


@pytest.mark.asyncio
async def test_entry_view_route():
    page = MagicMock()
    state = _auth_state()
    entry = _make_entry()

    mock_session = AsyncMock()
    cm = AsyncMock()
    cm.__aenter__.return_value = mock_session
    cm.__aexit__.return_value = None

    with (
        patch("app.views.entry_view.get_db_session", return_value=cm),
        patch("app.views.entry_view.get_entry", AsyncMock(return_value=entry)),
        patch("app.views.entry_view.mark_read", AsyncMock()),
        patch("app.views.entry_view._get_content_renderer", return_value=ft.Text("rendered")),
    ):
        view = await entry_view(page, state, entry_id=1)

    assert view.route == "/entry/1"


@pytest.mark.asyncio
async def test_entry_view_displays_title():
    page = MagicMock()
    state = _auth_state()
    entry = _make_entry(title="My Article Title")

    mock_session = AsyncMock()
    cm = AsyncMock()
    cm.__aenter__.return_value = mock_session
    cm.__aexit__.return_value = None

    with (
        patch("app.views.entry_view.get_db_session", return_value=cm),
        patch("app.views.entry_view.get_entry", AsyncMock(return_value=entry)),
        patch("app.views.entry_view.mark_read", AsyncMock()),
        patch("app.views.entry_view._get_content_renderer", return_value=ft.Text("rendered")),
    ):
        view = await entry_view(page, state, entry_id=1)

    texts = _find_controls(view, ft.Text)
    titles = [t for t in texts if "My Article Title" in (t.value or "")]
    assert len(titles) >= 1


@pytest.mark.asyncio
async def test_entry_view_contains_star_button():
    page = MagicMock()
    state = _auth_state()
    entry = _make_entry(important=0)

    mock_session = AsyncMock()
    cm = AsyncMock()
    cm.__aenter__.return_value = mock_session
    cm.__aexit__.return_value = None

    with (
        patch("app.views.entry_view.get_db_session", return_value=cm),
        patch("app.views.entry_view.get_entry", AsyncMock(return_value=entry)),
        patch("app.views.entry_view.mark_read", AsyncMock()),
        patch("app.views.entry_view._get_content_renderer", return_value=ft.Text("rendered")),
    ):
        view = await entry_view(page, state, entry_id=1)

    app_bars = _find_controls(view, ft.AppBar)
    assert len(app_bars) >= 1
    app_bar = app_bars[0]
    star_buttons = [b for b in (app_bar.actions or []) if isinstance(b, ft.IconButton) and b.icon == ft.Icons.STAR_BORDER]
    assert len(star_buttons) >= 1


@pytest.mark.asyncio
async def test_entry_view_not_found():
    page = MagicMock()
    state = _auth_state()

    mock_session = AsyncMock()
    cm = AsyncMock()
    cm.__aenter__.return_value = mock_session
    cm.__aexit__.return_value = None

    with (
        patch("app.views.entry_view.get_db_session", return_value=cm),
        patch("app.views.entry_view.get_entry", AsyncMock(return_value=None)),
    ):
        view = await entry_view(page, state, entry_id=999)

    assert view.route == "/entry/999"
    texts = _find_controls(view, ft.Text)
    assert any("Artigo não encontrado" in (t.value or "") for t in texts)


@pytest.mark.asyncio
async def test_entry_view_contains_open_original_button():
    page = MagicMock()
    state = _auth_state()
    entry = _make_entry(link="https://example.com/original")

    mock_session = AsyncMock()
    cm = AsyncMock()
    cm.__aenter__.return_value = mock_session
    cm.__aexit__.return_value = None

    with (
        patch("app.views.entry_view.get_db_session", return_value=cm),
        patch("app.views.entry_view.get_entry", AsyncMock(return_value=entry)),
        patch("app.views.entry_view.mark_read", AsyncMock()),
        patch("app.views.entry_view._get_content_renderer", return_value=ft.Text("rendered")),
    ):
        view = await entry_view(page, state, entry_id=1)

    buttons = _find_controls(view, ft.FilledButton)
    assert any("Ver original" in str(getattr(b, "content", "")) for b in buttons)
