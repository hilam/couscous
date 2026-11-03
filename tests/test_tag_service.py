import pytest
from sqlmodel import select

from app.services.tag_service import (
    assign_tag,
    delete_tag,
    get_distinct_tags,
    get_distinct_tags_for_feed,
    get_distinct_tags_with_counts,
    get_tags_for_entries,
    get_tags_for_entry,
    remove_tag,
)
from database.models.couscous import EntryTag
from tests.test_factory import make_user, create_feed_and_entry


@pytest.mark.asyncio
async def test_assign_tag(db_session):
    user = await make_user(db_session)
    _, entry = await create_feed_and_entry(db_session, user.id)

    await assign_tag(db_session, entry.id, "python", user.id)

    tags = await get_tags_for_entry(db_session, entry.id, user.id)
    assert tags == ["python"]


@pytest.mark.asyncio
async def test_assign_tag_duplicate_ignored(db_session):
    user = await make_user(db_session)
    _, entry = await create_feed_and_entry(db_session, user.id)

    await assign_tag(db_session, entry.id, "python", user.id)
    await assign_tag(db_session, entry.id, "python", user.id)

    tags = await get_tags_for_entry(db_session, entry.id, user.id)
    assert tags == ["python"]


@pytest.mark.asyncio
async def test_assign_tag_trims_and_lowercases(db_session):
    user = await make_user(db_session)
    _, entry = await create_feed_and_entry(db_session, user.id)

    await assign_tag(db_session, entry.id, "  Python  ", user.id)

    tags = await get_tags_for_entry(db_session, entry.id, user.id)
    assert tags == ["python"]


@pytest.mark.asyncio
async def test_assign_tag_empty_ignored(db_session):
    user = await make_user(db_session)
    _, entry = await create_feed_and_entry(db_session, user.id)

    await assign_tag(db_session, entry.id, "   ", user.id)

    tags = await get_tags_for_entry(db_session, entry.id, user.id)
    assert tags == []


@pytest.mark.asyncio
async def test_remove_tag(db_session):
    user = await make_user(db_session)
    _, entry = await create_feed_and_entry(db_session, user.id)

    await assign_tag(db_session, entry.id, "python", user.id)
    await remove_tag(db_session, entry.id, "python", user.id)

    tags = await get_tags_for_entry(db_session, entry.id, user.id)
    assert tags == []


@pytest.mark.asyncio
async def test_remove_nonexistent_tag_no_error(db_session):
    user = await make_user(db_session)
    _, entry = await create_feed_and_entry(db_session, user.id)

    await remove_tag(db_session, entry.id, "python", user.id)

    tags = await get_tags_for_entry(db_session, entry.id, user.id)
    assert tags == []


@pytest.mark.asyncio
async def test_get_tags_for_entry_multiple(db_session):
    user = await make_user(db_session)
    _, entry = await create_feed_and_entry(db_session, user.id)

    await assign_tag(db_session, entry.id, "python", user.id)
    await assign_tag(db_session, entry.id, "django", user.id)
    await assign_tag(db_session, entry.id, "asgi", user.id)

    tags = await get_tags_for_entry(db_session, entry.id, user.id)
    assert tags == ["asgi", "django", "python"]


@pytest.mark.asyncio
async def test_get_tags_for_entry_empty(db_session):
    user = await make_user(db_session)
    _, entry = await create_feed_and_entry(db_session, user.id)

    tags = await get_tags_for_entry(db_session, entry.id, user.id)
    assert tags == []


@pytest.mark.asyncio
async def test_get_distinct_tags(db_session):
    user = await make_user(db_session)
    _, entry1 = await create_feed_and_entry(db_session, user.id)
    _, entry2 = await create_feed_and_entry(
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
    _, entry1 = await create_feed_and_entry(db_session, user.id)
    _, entry2 = await create_feed_and_entry(
        db_session, user.id, url="https://example.com/rss2"
    )

    await assign_tag(db_session, entry1.id, "python", user.id)
    await assign_tag(db_session, entry2.id, "python", user.id)

    await delete_tag(db_session, "python", user.id)

    tags1 = await get_tags_for_entry(db_session, entry1.id, user.id)
    tags2 = await get_tags_for_entry(db_session, entry2.id, user.id)
    assert tags1 == []
    assert tags2 == []


@pytest.mark.asyncio
async def test_user_isolation(db_session):
    user1 = await make_user(db_session, "user1", "pass1")
    user2 = await make_user(db_session, "user2", "pass2")

    _, entry1 = await create_feed_and_entry(db_session, user1.id)
    _, entry2 = await create_feed_and_entry(
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
    _, entry1 = await create_feed_and_entry(db_session, user.id, url="https://example.com/feed1")
    _, entry2 = await create_feed_and_entry(db_session, user.id, url="https://example.com/feed2")

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
    _, entry = await create_feed_and_entry(db_session, user.id, url="https://example.com/feed1")

    tags = await get_distinct_tags_for_feed(
        db_session, "https://example.com/feed1", user.id
    )
    assert tags == []


@pytest.mark.asyncio
async def test_get_distinct_tags_with_counts(db_session):
    user = await make_user(db_session)
    _, entry1 = await create_feed_and_entry(db_session, user.id)
    _, entry2 = await create_feed_and_entry(
        db_session, user.id, url="https://example.com/rss2"
    )

    await assign_tag(db_session, entry1.id, "python", user.id)
    await assign_tag(db_session, entry1.id, "django", user.id)
    await assign_tag(db_session, entry2.id, "python", user.id)

    counts = await get_distinct_tags_with_counts(db_session, user.id)
    assert set(counts) == {("django", 1), ("python", 2)}


@pytest.mark.asyncio
async def test_get_distinct_tags_with_counts_empty(db_session):
    user = await make_user(db_session)

    counts = await get_distinct_tags_with_counts(db_session, user.id)
    assert counts == []


@pytest.mark.asyncio
async def test_get_tags_for_entry_scoped_by_user(db_session):
    user_a = await make_user(db_session, "usera", "passa")
    user_b = await make_user(db_session, "userb", "passb")
    _, entry_a = await create_feed_and_entry(db_session, user_a.id)

    await assign_tag(db_session, entry_a.id, "python", user_a.id)

    tags_a = await get_tags_for_entry(db_session, entry_a.id, user_a.id)
    assert tags_a == ["python"]

    tags_b = await get_tags_for_entry(db_session, entry_a.id, user_b.id)
    assert tags_b == []


@pytest.mark.asyncio
async def test_assign_tag_foreign_entry_raises(db_session):
    user_a = await make_user(db_session, "usera", "passa")
    user_b = await make_user(db_session, "userb", "passb")
    _, entry_a = await create_feed_and_entry(db_session, user_a.id)

    with pytest.raises(ValueError):
        await assign_tag(db_session, entry_a.id, "x", user_b.id)

    rows = await session_execute_all_tags(db_session, entry_a.id)
    assert rows == []


async def session_execute_all_tags(session, entry_id: int) -> list[str]:
    result = await session.execute(
        select(EntryTag.tag).where(EntryTag.entry_id == entry_id)
    )
    return list(result.scalars().all())


@pytest.mark.asyncio
async def test_get_tags_for_entries_batch(db_session):
    user = await make_user(db_session, "usera", "passa")
    _, entry1 = await create_feed_and_entry(db_session, user.id)
    _, entry2 = await create_feed_and_entry(
        db_session, user.id, url="https://example.com/rss2"
    )

    await assign_tag(db_session, entry1.id, "python", user.id)
    await assign_tag(db_session, entry1.id, "django", user.id)
    await assign_tag(db_session, entry2.id, "rust", user.id)

    tag_map = await get_tags_for_entries(
        db_session, [entry1.id, entry2.id], user.id
    )
    assert tag_map == {entry1.id: ["django", "python"], entry2.id: ["rust"]}


@pytest.mark.asyncio
async def test_get_tags_for_entries_batch_scoped_by_user(db_session):
    user_a = await make_user(db_session, "usera", "passa")
    user_b = await make_user(db_session, "userb", "passb")
    _, entry_a = await create_feed_and_entry(db_session, user_a.id)
    _, entry_b = await create_feed_and_entry(
        db_session, user_b.id, url="https://example.com/rss2"
    )

    await assign_tag(db_session, entry_a.id, "python", user_a.id)
    await assign_tag(db_session, entry_b.id, "rust", user_b.id)

    tag_map = await get_tags_for_entries(
        db_session, [entry_a.id, entry_b.id], user_a.id
    )
    assert tag_map == {entry_a.id: ["python"]}
    assert entry_b.id not in tag_map


@pytest.mark.asyncio
async def test_get_tags_for_entries_empty(db_session):
    user = await make_user(db_session)
    tag_map = await get_tags_for_entries(db_session, [], user.id)
    assert tag_map == {}


@pytest.mark.asyncio
async def test_assign_tag_cross_user_same_tag_not_suppressed(db_session):
    user_a = await make_user(db_session, "usera", "passa")
    user_b = await make_user(db_session, "userb", "passb")
    _, entry_a = await create_feed_and_entry(db_session, user_a.id)
    _, entry_b = await create_feed_and_entry(
        db_session, user_b.id, url="https://example.com/rss2"
    )

    await assign_tag(db_session, entry_a.id, "python", user_a.id)
    # a tag de user_a não pode suprimir a atribuição de user_b na própria entry
    await assign_tag(db_session, entry_b.id, "python", user_b.id)

    tags_a = await get_tags_for_entry(db_session, entry_a.id, user_a.id)
    tags_b = await get_tags_for_entry(db_session, entry_b.id, user_b.id)
    assert tags_a == ["python"]
    assert tags_b == ["python"]
