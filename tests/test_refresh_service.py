from datetime import datetime
from unittest.mock import patch

import httpx
import pytest

from app.services.refresh_service import refresh_all_feeds, refresh_single_feed
from database.models.couscous import Entry
from tests.test_factory import (
    atom_feed_xml,
    make_entry,
    make_feed,
    make_user,
    rss_feed_xml,
    rss_feed_xml_no_content,
    rss_xml_missing_items,
)


def _mock_response(text="", status_code=200):
    request = httpx.Request("GET", "http://test.com")
    resp = httpx.Response(status_code=status_code, text=text, request=request)
    return resp


@pytest.mark.asyncio
@patch("app.services.refresh_service.httpx.get")
async def test_refresh_single_feed_rss(mock_get, db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    mock_get.return_value = _mock_response(rss_feed_xml())

    await refresh_single_feed(db_session, feed)

    await db_session.refresh(feed)
    assert feed.title == "Test RSS Feed"
    assert feed.link == "https://example.com"
    assert feed.last_exception is None

    from sqlmodel import select
    result = await db_session.execute(select(Entry).where(Entry.feed == feed.url))
    entries = result.scalars().all()
    assert len(entries) == 3


@pytest.mark.asyncio
@patch("app.services.refresh_service.httpx.get")
async def test_refresh_single_feed_atom(mock_get, db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    mock_get.return_value = _mock_response(atom_feed_xml())

    await refresh_single_feed(db_session, feed)

    await db_session.refresh(feed)
    assert feed.last_exception is None

    from sqlmodel import select
    result = await db_session.execute(select(Entry).where(Entry.feed == feed.url))
    entries = result.scalars().all()
    assert len(entries) == 1
    assert entries[0].title == "Atom Article 1"


@pytest.mark.asyncio
@patch("app.services.refresh_service.httpx.get")
async def test_refresh_skips_duplicate_entries(mock_get, db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    await make_entry(db_session, feed_url=feed.url, user_id=user.id,
                     link="https://example.com/article1")

    mock_get.return_value = _mock_response(rss_feed_xml())

    await refresh_single_feed(db_session, feed)
    await db_session.refresh(feed)
    assert feed.last_exception is None

    from sqlmodel import select
    result = await db_session.execute(select(Entry).where(Entry.feed == feed.url))
    entries = result.scalars().all()
    assert len(entries) == 3


@pytest.mark.asyncio
@patch("app.services.refresh_service.httpx.get")
async def test_refresh_http_404(mock_get, db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    resp = httpx.Response(404, request=httpx.Request("GET", feed.url))
    mock_get.return_value = resp

    await refresh_single_feed(db_session, feed)

    await db_session.refresh(feed)
    assert feed.last_exception is not None
    assert "404" in feed.last_exception

    from sqlmodel import select
    result = await db_session.execute(select(Entry).where(Entry.feed == feed.url))
    entries = result.scalars().all()
    assert len(entries) == 0


@pytest.mark.asyncio
@patch("app.services.refresh_service.httpx.get")
async def test_refresh_timeout(mock_get, db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    mock_get.side_effect = httpx.TimeoutException("Request timed out")

    await refresh_single_feed(db_session, feed)

    await db_session.refresh(feed)
    assert feed.last_exception is not None
    assert "timed out" in feed.last_exception.lower()


@pytest.mark.asyncio
@patch("app.services.refresh_service.httpx.get")
async def test_refresh_empty_response(mock_get, db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    mock_get.return_value = _mock_response("")

    await refresh_single_feed(db_session, feed)

    await db_session.refresh(feed)
    assert feed.last_exception is None

    from sqlmodel import select
    result = await db_session.execute(select(Entry).where(Entry.feed == feed.url))
    entries = result.scalars().all()
    assert len(entries) == 0


@pytest.mark.asyncio
@patch("app.services.refresh_service.httpx.get")
async def test_refresh_malformed_xml(mock_get, db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    mock_get.return_value = _mock_response("<html><body>Not RSS</body></html>")

    await refresh_single_feed(db_session, feed)

    await db_session.refresh(feed)
    assert feed.last_exception is None


@pytest.mark.asyncio
@patch("app.services.refresh_service.httpx.get")
async def test_refresh_skips_malformed_entries(mock_get, db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    mock_get.return_value = _mock_response(rss_xml_missing_items())

    await refresh_single_feed(db_session, feed)

    await db_session.refresh(feed)
    assert feed.last_exception is None

    from sqlmodel import select
    result = await db_session.execute(select(Entry).where(Entry.feed == feed.url))
    entries = result.scalars().all()
    assert len(entries) == 2


@pytest.mark.asyncio
@patch("app.services.refresh_service.httpx.get")
async def test_refresh_entry_metadata(mock_get, db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    mock_get.return_value = _mock_response(rss_feed_xml())

    await refresh_single_feed(db_session, feed)

    from sqlmodel import select
    result = await db_session.execute(select(Entry).where(Entry.feed == feed.url))
    entries = result.scalars().all()
    entry = entries[0]

    assert entry.title == "Article 1"
    assert entry.link == "https://example.com/article1"
    assert entry.author == "Author 1"
    assert entry.summary == "Summary 1"
    assert "<p>Content 1</p>" in (entry.content or "")
    assert entry.added_by == "system"
    assert entry.published is not None
    assert entry.last_updated is not None
    assert entry.first_updated is not None
    assert isinstance(entry.published, datetime)


@pytest.mark.asyncio
@patch("app.services.refresh_service.httpx.get")
async def test_refresh_entry_metadata_no_content(mock_get, db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    mock_get.return_value = _mock_response(rss_feed_xml_no_content())

    await refresh_single_feed(db_session, feed)

    from sqlmodel import select
    result = await db_session.execute(select(Entry).where(Entry.feed == feed.url))
    entries = result.scalars().all()
    assert entries[0].content is None


@pytest.mark.asyncio
@patch("app.services.refresh_service.httpx.get")
async def test_refresh_all_feeds(mock_get, db_session):
    user = await make_user(db_session)
    feed1 = await make_feed(db_session, url="https://example.com/feed1", user_id=user.id)
    feed2 = await make_feed(db_session, url="https://example.com/feed2", user_id=user.id)
    feed3 = await make_feed(db_session, url="https://example.com/feed3", user_id=user.id)

    mock_get.return_value = _mock_response(rss_feed_xml(title="Multi Feed", num_entries=1))

    await refresh_all_feeds(db_session, user.id)

    from sqlmodel import select
    result = await db_session.execute(select(Entry).where(Entry.user_id == user.id))
    entries = result.scalars().all()
    assert len(entries) == 3
