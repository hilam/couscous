from datetime import datetime, timezone

import pytest

from app.services.tag_service import (
    assign_tag,
    delete_tag,
    get_distinct_tags,
    get_distinct_tags_for_feed,
    get_tags_for_entry,
    remove_tag,
)
from database.models.couscous import Entry, Feed
from tests.test_factory import make_user


async def _make_feed_and_entry(db_session, user_id, url="https://example.com/rss"):
    feed = Feed(url=url, user_id=user_id)
    db_session.add(feed)
    await db_session.commit()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    entry = Entry(
        feed=url,
        user_id=user_id,
        title="Test Article",
        link="https://example.com/a1",
        published=now,
        last_updated=now,
        first_updated=now,
        first_updated_epoch=now,
        added_by="test",
        feed_order=0,
    )
    db_session.add(entry)
    await db_session.commit()
    return entry


@pytest.mark.asyncio
async def test_assign_tag(db_session):
    user = await make_user(db_session)
    entry = await _make_feed_and_entry(db_session, user.id)

    await assign_tag(db_session, entry.id, "python", user.id)

    tags = await get_tags_for_entry(db_session, entry.id)
    assert tags == ["python"]


@pytest.mark.asyncio
async def test_assign_tag_duplicate_ignored(db_session):
    user = await make_user(db_session)
    entry = await _make_feed_and_entry(db_session, user.id)

    await assign_tag(db_session, entry.id, "python", user.id)
    await assign_tag(db_session, entry.id, "python", user.id)

    tags = await get_tags_for_entry(db_session, entry.id)
    assert tags == ["python"]


@pytest.mark.asyncio
async def test_assign_tag_trims_and_lowercases(db_session):
    user = await make_user(db_session)
    entry = await _make_feed_and_entry(db_session, user.id)

    await assign_tag(db_session, entry.id, "  Python  ", user.id)

    tags = await get_tags_for_entry(db_session, entry.id)
    assert tags == ["python"]


@pytest.mark.asyncio
async def test_assign_tag_empty_ignored(db_session):
    user = await make_user(db_session)
    entry = await _make_feed_and_entry(db_session, user.id)

    await assign_tag(db_session, entry.id, "   ", user.id)

    tags = await get_tags_for_entry(db_session, entry.id)
    assert tags == []


@pytest.mark.asyncio
async def test_remove_tag(db_session):
    user = await make_user(db_session)
    entry = await _make_feed_and_entry(db_session, user.id)

    await assign_tag(db_session, entry.id, "python", user.id)
    await remove_tag(db_session, entry.id, "python", user.id)

    tags = await get_tags_for_entry(db_session, entry.id)
    assert tags == []


@pytest.mark.asyncio
async def test_remove_nonexistent_tag_no_error(db_session):
    user = await make_user(db_session)
    entry = await _make_feed_and_entry(db_session, user.id)

    await remove_tag(db_session, entry.id, "python", user.id)

    tags = await get_tags_for_entry(db_session, entry.id)
    assert tags == []


@pytest.mark.asyncio
async def test_get_tags_for_entry_multiple(db_session):
    user = await make_user(db_session)
    entry = await _make_feed_and_entry(db_session, user.id)

    await assign_tag(db_session, entry.id, "python", user.id)
    await assign_tag(db_session, entry.id, "django", user.id)
    await assign_tag(db_session, entry.id, "asgi", user.id)

    tags = await get_tags_for_entry(db_session, entry.id)
    assert tags == ["asgi", "django", "python"]


@pytest.mark.asyncio
async def test_get_tags_for_entry_empty(db_session):
    user = await make_user(db_session)
    entry = await _make_feed_and_entry(db_session, user.id)

    tags = await get_tags_for_entry(db_session, entry.id)
    assert tags == []


@pytest.mark.asyncio
async def test_get_distinct_tags(db_session):
    user = await make_user(db_session)
    entry1 = await _make_feed_and_entry(db_session, user.id)
    entry2 = await _make_feed_and_entry(
        db_session, user.id, url="https://example.com/rss2"
    )

    await assign_tag(db_session, entry1.id, "python", user.id)
    await assign_tag(db_session, entry1.id, "django", user.id)
    await assign_tag(db_session, entry2.id, "python", user.id)

    tags = await get_distinct_tags(db_session, user.id)
    assert tags == ["django", "python"]


@pytest.mark.asyncio
async def test_get_distinct_tags_empty(db_session):
    user = await make_user(db_session)

    tags = await get_distinct_tags(db_session, user.id)
    assert tags == []


@pytest.mark.asyncio
async def test_delete_tag(db_session):
    user = await make_user(db_session)
    entry1 = await _make_feed_and_entry(db_session, user.id)
    entry2 = await _make_feed_and_entry(
        db_session, user.id, url="https://example.com/rss2"
    )

    await assign_tag(db_session, entry1.id, "python", user.id)
    await assign_tag(db_session, entry2.id, "python", user.id)

    await delete_tag(db_session, "python", user.id)

    tags1 = await get_tags_for_entry(db_session, entry1.id)
    tags2 = await get_tags_for_entry(db_session, entry2.id)
    assert tags1 == []
    assert tags2 == []


@pytest.mark.asyncio
async def test_user_isolation(db_session):
    user1 = await make_user(db_session, "user1", "pass1")
    user2 = await make_user(db_session, "user2", "pass2")

    entry1 = await _make_feed_and_entry(db_session, user1.id)
    entry2 = await _make_feed_and_entry(
        db_session, user2.id, url="https://example.com/rss2"
    )

    await assign_tag(db_session, entry1.id, "python", user1.id)
    await assign_tag(db_session, entry2.id, "python", user2.id)

    tags1 = await get_distinct_tags(db_session, user1.id)
    tags2 = await get_distinct_tags(db_session, user2.id)
    assert tags1 == ["python"]
    assert tags2 == ["python"]

    await delete_tag(db_session, "python", user1.id)
    tags1_after = await get_distinct_tags(db_session, user1.id)
    tags2_after = await get_distinct_tags(db_session, user2.id)
    assert tags1_after == []
    assert tags2_after == ["python"]


@pytest.mark.asyncio
async def test_get_distinct_tags_for_feed(db_session):
    user = await make_user(db_session)
    entry1 = await _make_feed_and_entry(db_session, user.id, url="https://example.com/feed1")
    entry2 = await _make_feed_and_entry(db_session, user.id, url="https://example.com/feed2")

    await assign_tag(db_session, entry1.id, "python", user.id)
    await assign_tag(db_session, entry1.id, "django", user.id)
    await assign_tag(db_session, entry2.id, "rust", user.id)

    tags_feed1 = await get_distinct_tags_for_feed(
        db_session, "https://example.com/feed1", user.id
    )
    tags_feed2 = await get_distinct_tags_for_feed(
        db_session, "https://example.com/feed2", user.id
    )
    assert set(tags_feed1) == {"django", "python"}
    assert tags_feed2 == ["rust"]


@pytest.mark.asyncio
async def test_get_distinct_tags_for_feed_empty(db_session):
    user = await make_user(db_session)
    await _make_feed_and_entry(db_session, user.id, url="https://example.com/feed1")

    tags = await get_distinct_tags_for_feed(
        db_session, "https://example.com/feed1", user.id
    )
    assert tags == []
