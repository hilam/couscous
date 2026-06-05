import pytest

from app.services.category_service import create_category
from app.services.feed_service import add_feed, list_feeds, remove_feed, update_feed_category
from app.services.user_service import register


@pytest.mark.asyncio
async def test_list_feeds_empty(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    feeds = await list_feeds(db_session, user.id)
    assert feeds == []


@pytest.mark.asyncio
async def test_add_feed(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    feed = await add_feed(db_session, user.id, "https://example.com/rss")
    assert feed.url == "https://example.com/rss"
    assert feed.user_id == user.id


@pytest.mark.asyncio
async def test_add_duplicate_feed_raises(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    await add_feed(db_session, user.id, "https://example.com/rss")
    with pytest.raises(ValueError, match="Feed já cadastrado"):
        await add_feed(db_session, user.id, "https://example.com/rss")


@pytest.mark.asyncio
async def test_list_feeds_after_add(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    await add_feed(db_session, user.id, "https://example.com/rss")
    feeds = await list_feeds(db_session, user.id)
    assert len(feeds) == 1
    assert feeds[0].url == "https://example.com/rss"


@pytest.mark.asyncio
async def test_remove_feed(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    await add_feed(db_session, user.id, "https://example.com/rss")
    await remove_feed(db_session, user.id, "https://example.com/rss")
    feeds = await list_feeds(db_session, user.id)
    assert feeds == []


@pytest.mark.asyncio
async def test_feeds_scoped_by_user(db_session):
    user1 = await register(db_session, "user1", "pass")
    user2 = await register(db_session, "user2", "pass")
    assert user1.id is not None
    assert user2.id is not None
    await add_feed(db_session, user1.id, "https://example.com/rss")
    feeds1 = await list_feeds(db_session, user1.id)
    feeds2 = await list_feeds(db_session, user2.id)
    assert len(feeds1) == 1
    assert len(feeds2) == 0


@pytest.mark.asyncio
async def test_add_feed_with_category(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    cat = await create_category(db_session, user.id, "Tech")
    feed = await add_feed(db_session, user.id, "https://example.com/rss", category_id=cat.id)
    assert feed.category_id == cat.id


@pytest.mark.asyncio
async def test_add_feed_without_category(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    feed = await add_feed(db_session, user.id, "https://example.com/rss")
    assert feed.category_id is None


@pytest.mark.asyncio
async def test_update_feed_category(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    cat = await create_category(db_session, user.id, "Tech")
    feed = await add_feed(db_session, user.id, "https://example.com/rss")
    assert feed.category_id is None
    updated = await update_feed_category(db_session, user.id, feed.url, cat.id)
    assert updated.category_id == cat.id


@pytest.mark.asyncio
async def test_update_feed_category_remove(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    cat = await create_category(db_session, user.id, "Tech")
    feed = await add_feed(db_session, user.id, "https://example.com/rss", category_id=cat.id)
    assert feed.category_id == cat.id
    updated = await update_feed_category(db_session, user.id, feed.url, None)
    assert updated.category_id is None
