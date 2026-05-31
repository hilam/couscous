from datetime import datetime

import pytest

from app.services.entry_service import (
    list_entries,
    get_entry,
    mark_read,
    mark_important,
)
from database.models.couscous import Feed, Entry


@pytest.mark.asyncio
async def test_list_entries_empty(db_session):
    entries = await list_entries(db_session, "https://example.com/rss")
    assert entries == []


@pytest.mark.asyncio
async def test_list_entries(db_session):
    feed = Feed(url="https://example.com/rss")
    db_session.add(feed)
    await db_session.commit()

    entry = Entry(
        feed="https://example.com/rss",
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

    entries = await list_entries(db_session, "https://example.com/rss")
    assert len(entries) == 1
    assert entries[0].title == "Test Article"


@pytest.mark.asyncio
async def test_get_entry(db_session):
    feed = Feed(url="https://example.com/rss")
    db_session.add(feed)
    await db_session.commit()

    entry = Entry(
        feed="https://example.com/rss",
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

    assert entry.id is not None
    found = await get_entry(db_session, entry.id)
    assert found is not None
    assert found.title == "Test Article"


@pytest.mark.asyncio
async def test_mark_read(db_session):
    feed = Feed(url="https://example.com/rss")
    db_session.add(feed)
    await db_session.commit()

    entry = Entry(
        feed="https://example.com/rss",
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

    assert entry.id is not None
    await mark_read(db_session, entry.id)
    await db_session.refresh(entry)
    assert entry.read == 1


@pytest.mark.asyncio
async def test_mark_important(db_session):
    feed = Feed(url="https://example.com/rss")
    db_session.add(feed)
    await db_session.commit()

    entry = Entry(
        feed="https://example.com/rss",
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

    assert entry.id is not None
    await mark_important(db_session, entry.id)
    await db_session.refresh(entry)
    assert entry.important == 1
