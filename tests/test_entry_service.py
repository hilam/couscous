from datetime import datetime, timedelta

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
from tests.test_factory import (
    make_user,
    create_feed_and_entry,
    make_entry,
    make_feed,
)


@pytest.mark.asyncio
async def test_list_entries_empty(db_session):
    user = await make_user(db_session)
    entries = await list_entries(db_session, "https://example.com/rss", user_id=user.id)
    assert entries == []


@pytest.mark.asyncio
async def test_list_entries(db_session):
    user = await make_user(db_session)
    await create_feed_and_entry(db_session, user.id)

    entries = await list_entries(db_session, "https://example.com/rss", user_id=user.id)
    assert len(entries) == 1
    assert entries[0].title == "Test Article"


@pytest.mark.asyncio
async def test_get_entry(db_session):
    user = await make_user(db_session)
    _, entry = await create_feed_and_entry(db_session, user.id)

    assert entry.id is not None
    found = await get_entry(db_session, entry.id, user.id)
    assert found is not None
    assert found.title == "Test Article"


@pytest.mark.asyncio
async def test_get_entry_scoped_by_user(db_session):
    user_a = await make_user(db_session, "usera", "passa")
    user_b = await make_user(db_session, "userb", "passb")
    _, entry_a = await create_feed_and_entry(db_session, user_a.id)

    assert entry_a.id is not None
    found = await get_entry(db_session, entry_a.id, user_a.id)
    assert found is not None
    assert found.title == "Test Article"

    leaked = await get_entry(db_session, entry_a.id, user_b.id)
    assert leaked is None


@pytest.mark.asyncio
async def test_mark_read(db_session):
    user = await make_user(db_session)
    _, entry = await create_feed_and_entry(db_session, user.id)

    assert entry.id is not None
    await mark_read(db_session, entry.id, user.id)
    await db_session.refresh(entry)
    assert entry.read == 1


@pytest.mark.asyncio
async def test_mark_important(db_session):
    user = await make_user(db_session)
    _, entry = await create_feed_and_entry(db_session, user.id)

    assert entry.id is not None
    await mark_important(db_session, entry.id, user.id)
    await db_session.refresh(entry)
    assert entry.important == 1


@pytest.mark.asyncio
async def test_list_entries_unread_only(db_session):
    user = await make_user(db_session)
    _, e1 = await create_feed_and_entry(db_session, user.id)
    await create_feed_and_entry(db_session, user.id, url="https://example.com/rss2")

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
    user = await make_user(db_session)
    _, e1 = await create_feed_and_entry(db_session, user.id)
    await create_feed_and_entry(db_session, user.id, url="https://example.com/rss2")

    assert e1.id is not None
    await mark_important(db_session, e1.id, user.id)

    important = await list_entries(
        db_session, "https://example.com/rss", user_id=user.id, important_only=True
    )
    assert len(important) == 1


@pytest.mark.asyncio
async def test_get_unread_count(db_session):
    user = await make_user(db_session)
    _, e1 = await create_feed_and_entry(db_session, user.id)
    await create_feed_and_entry(db_session, user.id, url="https://example.com/rss2")

    count = await get_unread_count(db_session, user.id)
    assert count == 2

    assert e1.id is not None
    await mark_read(db_session, e1.id, user.id)

    count = await get_unread_count(db_session, user.id)
    assert count == 1


@pytest.mark.asyncio
async def test_list_entries_tag_filter(db_session):
    user = await make_user(db_session)
    _, e1 = await create_feed_and_entry(db_session, user.id)
    _, e2 = await create_feed_and_entry(
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
    user = await make_user(db_session)
    e1_fe, e1 = await create_feed_and_entry(db_session, user.id)
    _, e2 = await create_feed_and_entry(
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
    user = await make_user(db_session)
    _, e1 = await create_feed_and_entry(db_session, user.id)
    _, e2 = await create_feed_and_entry(
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
    user = await make_user(db_session)
    await create_feed_and_entry(db_session, user.id)

    result = await list_entries(
        db_session, "https://example.com/rss", user_id=user.id, tag="rust"
    )
    assert result == []


async def _make_60_entries(db_session, user_id, url="https://example.com/pag"):
    feed = await make_feed(db_session, url=url, user_id=user_id)
    base = datetime(2024, 1, 1)
    for i in range(60):
        await make_entry(
            db_session,
            feed_url=url,
            user_id=user_id,
            link=f"{url}/article{i}",
            title=f"Article {i}",
            author=f"Author {i}",
            published=base + timedelta(minutes=i),
        )
    return feed


@pytest.mark.asyncio
async def test_list_entries_keyset_first_page(db_session):
    user = await make_user(db_session)
    feed = await _make_60_entries(db_session, user.id)

    page1 = await list_entries(db_session, feed.url, user_id=user.id)
    assert len(page1) == 50
    assert page1[0].published == datetime(2024, 1, 1) + timedelta(minutes=59)


@pytest.mark.asyncio
async def test_list_entries_keyset_second_page_no_overlap(db_session):
    user = await make_user(db_session)
    feed = await _make_60_entries(db_session, user.id)

    page1 = await list_entries(db_session, feed.url, user_id=user.id)
    last = page1[-1]
    page2 = await list_entries(
        db_session,
        feed.url,
        user_id=user.id,
        before=last.published,
        before_id=last.id,
    )
    assert len(page2) == 10
    page1_ids = {row.id for row in page1}
    page2_ids = {row.id for row in page2}
    assert page1_ids.isdisjoint(page2_ids)
    full_ids = {
        row.id
        for row in await list_entries(
            db_session, feed.url, user_id=user.id, limit=100
        )
    }
    assert page1_ids | page2_ids == full_ids


@pytest.mark.asyncio
async def test_list_entries_keyset_empty_feed_with_cursor(db_session):
    user = await make_user(db_session)
    await create_feed_and_entry(db_session, user.id)

    result = await list_entries(
        db_session,
        "https://example.com/empty",
        user_id=user.id,
        before=datetime(2024, 1, 1),
        before_id=1,
    )
    assert result == []


@pytest.mark.asyncio
async def test_list_entries_keyset_unread_filter_preserved(db_session):
    user = await make_user(db_session)
    feed = await _make_60_entries(db_session, user.id)

    page1 = await list_entries(db_session, feed.url, user_id=user.id)
    # marca os 5 mais novos como lidos
    for row in page1[:5]:
        await mark_read(db_session, row.id, user.id)

    unread_page1 = await list_entries(
        db_session, feed.url, user_id=user.id, unread_only=True
    )
    assert len(unread_page1) == 50
    assert all(row.read == 0 for row in unread_page1)

    last_unread = unread_page1[-1]
    unread_page2 = await list_entries(
        db_session,
        feed.url,
        user_id=user.id,
        unread_only=True,
        before=last_unread.published,
        before_id=last_unread.id,
    )
    assert len(unread_page2) == 5
    assert all(row.read == 0 for row in unread_page2)


@pytest.mark.asyncio
async def test_list_entries_projection_excludes_content(db_session):
    user = await make_user(db_session)
    await _make_60_entries(db_session, user.id)

    page = await list_entries(
        db_session, "https://example.com/pag", user_id=user.id
    )
    row = page[0]
    assert not hasattr(row, "content")
    assert not hasattr(row, "important")
    assert row.title is not None
    assert row.author is not None


@pytest.mark.asyncio
async def test_list_recent_all_feeds(db_session):
    user = await make_user(db_session)
    _, e1 = await create_feed_and_entry(db_session, user.id)
    _, e2 = await create_feed_and_entry(
        db_session, user.id, url="https://example.com/rss2"
    )

    recent = await list_recent(db_session, user.id)
    assert len(recent) == 2


@pytest.mark.asyncio
async def test_list_recent_empty(db_session):
    user = await make_user(db_session)
    recent = await list_recent(db_session, user.id)
    assert recent == []


@pytest.mark.asyncio
async def test_list_recent_by_category(db_session):
    user = await make_user(db_session)
    _, e1 = await create_feed_and_entry(db_session, user.id)
    _, e2 = await create_feed_and_entry(
        db_session, user.id, url="https://example.com/rss2"
    )

    cat = await create_category(db_session, user.id, "Tech")
    await update_feed_category(db_session, user.id, "https://example.com/rss", cat.id)

    recent = await list_recent(db_session, user.id, category_id=cat.id)
    assert len(recent) == 1
    assert recent[0].id == e1.id


@pytest.mark.asyncio
async def test_list_recent_by_tag(db_session):
    user = await make_user(db_session)
    _, e1 = await create_feed_and_entry(db_session, user.id)
    _, e2 = await create_feed_and_entry(
        db_session, user.id, url="https://example.com/rss2"
    )

    assert e1.id is not None
    await assign_tag(db_session, e1.id, "python", user.id)

    recent = await list_recent(db_session, user.id, tags=["python"])
    assert len(recent) == 1
    assert recent[0].id == e1.id


@pytest.mark.asyncio
async def test_list_recent_by_category_and_tag(db_session):
    user = await make_user(db_session)
    _, e1 = await create_feed_and_entry(db_session, user.id)
    _, e2 = await create_feed_and_entry(
        db_session, user.id, url="https://example.com/rss2"
    )
    _, e3 = await create_feed_and_entry(
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
    user = await make_user(db_session)
    for i in range(5):
        await create_feed_and_entry(
            db_session, user.id, url=f"https://example.com/rss{i}"
        )

    recent = await list_recent(db_session, user.id, limit=3)
    assert len(recent) == 3
