from datetime import datetime

import pytest

from app.services.entry_service import (
    list_entries,
    get_entry,
    list_recent,
    mark_read,
    mark_important,
    get_unread_count,
)
from app.services.category_service import create_category
from app.services.feed_service import update_feed_category
from app.services.tag_service import assign_tag
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


@pytest.mark.asyncio
async def test_list_entries_tag_filter(db_session):
    user = await _make_user(db_session)
    _, e1 = await _create_feed_and_entry(db_session, user.id)
    _, e2 = await _create_feed_and_entry(
        db_session, user.id, url="https://example.com/rss2"
    )

    assert e1.id is not None
    assert e2.id is not None
    await assign_tag(db_session, e1.id, "python", user.id)
    await assign_tag(db_session, e2.id, "django", user.id)

    tagged = await list_entries(
        db_session, "https://example.com/rss", user_id=user.id, tag="python"
    )
    assert len(tagged) == 1
    assert tagged[0].id == e1.id


@pytest.mark.asyncio
async def test_list_entries_tag_none_shows_all(db_session):
    user = await _make_user(db_session)
    e1_fe, e1 = await _create_feed_and_entry(db_session, user.id)
    _, e2 = await _create_feed_and_entry(
        db_session, user.id, url="https://example.com/rss2"
    )

    assert e1.id is not None
    assert e2.id is not None
    await assign_tag(db_session, e1.id, "python", user.id)

    all_entries = await list_entries(
        db_session, "https://example.com/rss", user_id=user.id, tag=None
    )
    assert len(all_entries) == 1


@pytest.mark.asyncio
async def test_list_entries_tag_with_other_filters(db_session):
    user = await _make_user(db_session)
    _, e1 = await _create_feed_and_entry(db_session, user.id)
    _, e2 = await _create_feed_and_entry(
        db_session, user.id, url="https://example.com/rss2"
    )

    assert e1.id is not None
    assert e2.id is not None
    await assign_tag(db_session, e1.id, "python", user.id)
    await assign_tag(db_session, e2.id, "python", user.id)
    await mark_important(db_session, e2.id, user.id)
    await mark_read(db_session, e1.id, user.id)

    result = await list_entries(
        db_session,
        "https://example.com/rss",
        user_id=user.id,
        tag="python",
        unread_only=False,
        important_only=False,
    )
    assert len(result) == 1

    result = await list_entries(
        db_session,
        "https://example.com/rss",
        user_id=user.id,
        tag="python",
        unread_only=True,
        important_only=True,
    )
    assert len(result) == 0

    result = await list_entries(
        db_session,
        "https://example.com/rss2",
        user_id=user.id,
        tag="python",
        important_only=True,
    )
    assert len(result) == 1
    assert result[0].id == e2.id


@pytest.mark.asyncio
async def test_list_entries_tag_no_match(db_session):
    user = await _make_user(db_session)
    await _create_feed_and_entry(db_session, user.id)

    result = await list_entries(
        db_session, "https://example.com/rss", user_id=user.id, tag="rust"
    )
    assert result == []


@pytest.mark.asyncio
async def test_list_recent_all_feeds(db_session):
    user = await _make_user(db_session)
    _, e1 = await _create_feed_and_entry(db_session, user.id)
    _, e2 = await _create_feed_and_entry(
        db_session, user.id, url="https://example.com/rss2"
    )

    recent = await list_recent(db_session, user.id)
    assert len(recent) == 2


@pytest.mark.asyncio
async def test_list_recent_empty(db_session):
    user = await _make_user(db_session)
    recent = await list_recent(db_session, user.id)
    assert recent == []


@pytest.mark.asyncio
async def test_list_recent_by_category(db_session):
    user = await _make_user(db_session)
    _, e1 = await _create_feed_and_entry(db_session, user.id)
    _, e2 = await _create_feed_and_entry(
        db_session, user.id, url="https://example.com/rss2"
    )

    cat = await create_category(db_session, user.id, "Tech")
    await update_feed_category(db_session, user.id, "https://example.com/rss", cat.id)

    recent = await list_recent(db_session, user.id, category_id=cat.id)
    assert len(recent) == 1
    assert recent[0].id == e1.id


@pytest.mark.asyncio
async def test_list_recent_by_tag(db_session):
    user = await _make_user(db_session)
    _, e1 = await _create_feed_and_entry(db_session, user.id)
    _, e2 = await _create_feed_and_entry(
        db_session, user.id, url="https://example.com/rss2"
    )

    assert e1.id is not None
    await assign_tag(db_session, e1.id, "python", user.id)

    recent = await list_recent(db_session, user.id, tags=["python"])
    assert len(recent) == 1
    assert recent[0].id == e1.id


@pytest.mark.asyncio
async def test_list_recent_by_category_and_tag(db_session):
    user = await _make_user(db_session)
    _, e1 = await _create_feed_and_entry(db_session, user.id)
    _, e2 = await _create_feed_and_entry(
        db_session, user.id, url="https://example.com/rss2"
    )
    _, e3 = await _create_feed_and_entry(
        db_session, user.id, url="https://example.com/rss3"
    )

    cat = await create_category(db_session, user.id, "Tech")
    await update_feed_category(db_session, user.id, "https://example.com/rss", cat.id)

    assert e1.id is not None
    assert e2.id is not None
    assert e3.id is not None
    await assign_tag(db_session, e1.id, "python", user.id)
    await assign_tag(db_session, e2.id, "python", user.id)

    recent = await list_recent(db_session, user.id, category_id=cat.id, tags=["python"])
    assert len(recent) == 1
    assert recent[0].id == e1.id


@pytest.mark.asyncio
async def test_list_recent_limit(db_session):
    user = await _make_user(db_session)
    for i in range(5):
        await _create_feed_and_entry(
            db_session, user.id, url=f"https://example.com/rss{i}"
        )

    recent = await list_recent(db_session, user.id, limit=3)
    assert len(recent) == 3
