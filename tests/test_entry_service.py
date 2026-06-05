from datetime import datetime

import pytest

from app.services.entry_service import (
    list_entries,
    get_entry,
    mark_read,
    mark_important,
    get_unread_count,
)
from app.services.user_service import register
from database.models.couscous import Feed, Entry


async def _make_user(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    return user


async def _create_feed_and_entry(db_session, user_id, url="https://example.com/rss"):
    feed = Feed(url=url, user_id=user_id)
    db_session.add(feed)
    await db_session.commit()

    entry = Entry(
        feed=url,
        user_id=user_id,
        title="Test Article",
        link="https://example.com/article1",
        published=datetime.now(),
        last_updated=datetime.now(),
        first_updated=datetime.now(),
        first_updated_epoch=datetime.now(),
        added_by="test",
        feed_order=0,
    )
    db_session.add(entry)
    await db_session.commit()
    return feed, entry


@pytest.mark.asyncio
async def test_list_entries_empty(db_session):
    user = await _make_user(db_session)
    entries = await list_entries(db_session, "https://example.com/rss", user_id=user.id)
    assert entries == []


@pytest.mark.asyncio
async def test_list_entries(db_session):
    user = await _make_user(db_session)
    await _create_feed_and_entry(db_session, user.id)

    entries = await list_entries(db_session, "https://example.com/rss", user_id=user.id)
    assert len(entries) == 1
    assert entries[0].title == "Test Article"


@pytest.mark.asyncio
async def test_get_entry(db_session):
    user = await _make_user(db_session)
    _, entry = await _create_feed_and_entry(db_session, user.id)

    assert entry.id is not None
    found = await get_entry(db_session, entry.id)
    assert found is not None
    assert found.title == "Test Article"


@pytest.mark.asyncio
async def test_mark_read(db_session):
    user = await _make_user(db_session)
    _, entry = await _create_feed_and_entry(db_session, user.id)

    assert entry.id is not None
    await mark_read(db_session, entry.id, user.id)
    await db_session.refresh(entry)
    assert entry.read == 1


@pytest.mark.asyncio
async def test_mark_important(db_session):
    user = await _make_user(db_session)
    _, entry = await _create_feed_and_entry(db_session, user.id)

    assert entry.id is not None
    await mark_important(db_session, entry.id, user.id)
    await db_session.refresh(entry)
    assert entry.important == 1


@pytest.mark.asyncio
async def test_list_entries_unread_only(db_session):
    user = await _make_user(db_session)
    _, e1 = await _create_feed_and_entry(db_session, user.id)
    await _create_feed_and_entry(db_session, user.id, url="https://example.com/rss2")

    assert e1.id is not None
    await mark_read(db_session, e1.id, user.id)

    unread = await list_entries(
        db_session, "https://example.com/rss", user_id=user.id, unread_only=True
    )
    assert len(unread) == 0

    all_entries = await list_entries(
        db_session, "https://example.com/rss", user_id=user.id
    )
    assert len(all_entries) == 1


@pytest.mark.asyncio
async def test_list_entries_important_only(db_session):
    user = await _make_user(db_session)
    _, e1 = await _create_feed_and_entry(db_session, user.id)
    await _create_feed_and_entry(db_session, user.id, url="https://example.com/rss2")

    assert e1.id is not None
    await mark_important(db_session, e1.id, user.id)

    important = await list_entries(
        db_session, "https://example.com/rss", user_id=user.id, important_only=True
    )
    assert len(important) == 1


@pytest.mark.asyncio
async def test_get_unread_count(db_session):
    user = await _make_user(db_session)
    _, e1 = await _create_feed_and_entry(db_session, user.id)
    await _create_feed_and_entry(db_session, user.id, url="https://example.com/rss2")

    count = await get_unread_count(db_session, user.id)
    assert count == 2

    assert e1.id is not None
    await mark_read(db_session, e1.id, user.id)

    count = await get_unread_count(db_session, user.id)
    assert count == 1
