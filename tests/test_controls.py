from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import flet as ft
import pytest

from app.controls.add_feed_dialog import AddFeedDialog
from app.controls.article_card import ArticleCard
from app.controls.confirm_dialog import ConfirmDialog
from app.controls.feed_card import FeedCard
from database.models.couscous import Entry, Feed


def _make_entry(read=0, important=0):
    return Entry(
        feed="https://example.com/rss",
        user_id=1,
        title="Test Article",
        link="https://example.com/a1",
        summary="This is a test summary for the article card.",
        author="Test Author",
        published=datetime(2024, 1, 1),
        last_updated=datetime.now(),
        first_updated=datetime.now(),
        first_updated_epoch=datetime.now(),
        added_by="test",
        feed_order=0,
        read=read,
        important=important,
    )


class TestFeedCard:
    def test_renders_title_and_link(self):
        feed = Feed(url="https://example.com/rss", user_id=1, title="My Blog",
                    link="https://example.com")
        card = FeedCard(feed=feed, on_click=lambda e: None, on_delete=lambda e: None)

        assert card.content.content.title.value == "My Blog"
        assert card.content.content.subtitle.value == "https://example.com"

    def test_falls_back_to_url_when_no_title(self):
        feed = Feed(url="https://example.com/rss", user_id=1)
        card = FeedCard(feed=feed, on_click=lambda e: None, on_delete=lambda e: None)

        assert card.content.content.title.value == "https://example.com/rss"

    def test_click_callback_wired(self):
        feed = Feed(url="https://example.com/rss", user_id=1, title="Test")
        callback = MagicMock()
        card = FeedCard(feed=feed, on_click=callback, on_delete=lambda e: None)

        card._click(None)
        callback.assert_called_once()

    def test_delete_callback_wired(self):
        feed = Feed(url="https://example.com/rss", user_id=1, title="Test")
        callback = MagicMock()
        card = FeedCard(feed=feed, on_click=lambda e: None, on_delete=callback)

        card._delete(None)
        callback.assert_called_once()


class TestArticleCard:
    def test_renders_title_and_metadata(self):
        entry = _make_entry()
        card = ArticleCard(entry=entry, on_click=lambda e: None)

        assert "Test Article" in card.content.content.title.value
        subtitle_col = card.content.content.subtitle
        assert subtitle_col.controls[0].value is not None
        assert "Test Author" in subtitle_col.controls[0].value
        assert "01/01/2024" in subtitle_col.controls[0].value
        assert "test summary" in subtitle_col.controls[1].value

    def test_unread_uses_bold_and_blue(self):
        entry = _make_entry(read=0)
        card = ArticleCard(entry=entry, on_click=lambda e: None)

        assert card.content.content.title.weight == ft.FontWeight.BOLD
        assert card.content.content.leading.color == ft.Colors.BLUE_400

    def test_read_uses_normal_and_grey(self):
        entry = _make_entry(read=1)
        card = ArticleCard(entry=entry, on_click=lambda e: None)

        assert card.content.content.title.weight == ft.FontWeight.NORMAL
        assert card.content.content.leading.color == ft.Colors.GREY_400

    def test_click_callback_wired(self):
        entry = _make_entry()
        callback = MagicMock()
        card = ArticleCard(entry=entry, on_click=callback)

        card._click()
        callback.assert_called_once()


class TestAddFeedDialog:
    def test_dialog_structure(self):
        dlg = AddFeedDialog(on_submit=lambda url, cat_id=None: None, user_id=0)
        assert dlg.title == "Adicionar Feed"
        assert dlg.url_field.label == "URL do Feed RSS"
        assert dlg.category_dropdown.label == "Categoria (opcional)"
        assert len(dlg.actions) == 3

    @pytest.mark.asyncio
    async def test_submit_with_valid_url(self):
        callback = AsyncMock()
        dlg = AddFeedDialog(on_submit=callback, user_id=0)
        dlg.url_field.value = "https://example.com/feed.xml"
        dlg.category_dropdown.value = ""

        with patch.object(dlg, "update"):
            dlg._submit(None)

        assert dlg.open is False
        assert dlg.url_field.value == ""
        callback.assert_called_once_with("https://example.com/feed.xml", None)

    def test_cancel_clears_and_closes(self):
        callback = MagicMock()
        dlg = AddFeedDialog(on_submit=callback, user_id=0)
        dlg.url_field.value = "https://example.com/feed.xml"
        dlg.category_dropdown.value = ""
        dlg.open = True

        with patch.object(dlg, "update"):
            dlg._cancel(None)

        assert dlg.open is False
        assert dlg.url_field.value == ""
        callback.assert_not_called()

    def test_empty_url_does_not_submit(self):
        callback = MagicMock()
        dlg = AddFeedDialog(on_submit=callback, user_id=0)
        dlg.url_field.value = "   "

        dlg._submit(None)

        callback.assert_not_called()

    @pytest.mark.asyncio
    async def test_submit_another_with_valid_url(self):
        callback = AsyncMock()
        dlg = AddFeedDialog(
            on_submit=lambda url, cid=None: None,
            on_submit_another=callback,
            user_id=0,
        )
        dlg.url_field.value = "https://example.com/feed.xml"
        dlg.category_dropdown.value = ""

        with patch.object(dlg, "update"), patch.object(
            dlg.url_field, "update"
        ), patch.object(dlg.url_field, "focus"):
            await dlg._submit_another(None)

        callback.assert_called_once_with("https://example.com/feed.xml", None)
        assert dlg.url_field.value == ""

    @pytest.mark.asyncio
    async def test_submit_another_duplicate_keeps_url(self):
        callback = AsyncMock(return_value=False)
        dlg = AddFeedDialog(
            on_submit=lambda url, cid=None: None,
            on_submit_another=callback,
            user_id=0,
        )
        dlg.url_field.value = "https://example.com/feed.xml"
        dlg.category_dropdown.value = ""

        with patch.object(dlg, "update"):
            await dlg._submit_another(None)

        callback.assert_called_once_with("https://example.com/feed.xml", None)
        assert dlg.url_field.value == "https://example.com/feed.xml"

    @pytest.mark.asyncio
    async def test_submit_another_empty_url(self):
        callback = AsyncMock()
        dlg = AddFeedDialog(
            on_submit=lambda url, cid=None: None,
            on_submit_another=callback,
            user_id=0,
        )
        dlg.url_field.value = "   "

        with patch.object(dlg, "update"):
            await dlg._submit_another(None)

        callback.assert_not_called()


class TestConfirmDialog:
    def test_renders_title_and_message(self):
        dlg = ConfirmDialog(title="Remove Feed", message="Are you sure?",
                            on_confirm=lambda e: None)
        assert dlg.title == "Remove Feed"
        assert dlg.content.value == "Are you sure?"
        assert len(dlg.actions) == 2

    @pytest.mark.asyncio
    async def test_confirm_fires_callback(self):
        callback = AsyncMock()
        dlg = ConfirmDialog(title="Test", message="Test?", on_confirm=callback)

        with patch.object(dlg, "update"):
            dlg._confirm(None)

        assert dlg.open is False
        callback.assert_called_once()

    def test_cancel_closes_without_confirmation(self):
        callback = MagicMock()
        dlg = ConfirmDialog(title="Test", message="Test?", on_confirm=callback)
        dlg.open = True

        with patch.object(dlg, "update"):
            dlg._cancel(None)

        assert dlg.open is False
        callback.assert_not_called()
