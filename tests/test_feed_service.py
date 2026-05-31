import pytest

from app.services.feed_service import list_feeds, add_feed, remove_feed


@pytest.mark.asyncio
async def test_list_feeds_empty(db_session):
    feeds = await list_feeds(db_session)
    assert feeds == []


@pytest.mark.asyncio
async def test_add_feed(db_session):
    feed = await add_feed(db_session, "https://example.com/rss")
    assert feed.url == "https://example.com/rss"


@pytest.mark.asyncio
async def test_add_duplicate_feed_raises(db_session):
    await add_feed(db_session, "https://example.com/rss")
    with pytest.raises(ValueError, match="Feed já cadastrado"):
        await add_feed(db_session, "https://example.com/rss")


@pytest.mark.asyncio
async def test_list_feeds_after_add(db_session):
    await add_feed(db_session, "https://example.com/rss")
    feeds = await list_feeds(db_session)
    assert len(feeds) == 1
    assert feeds[0].url == "https://example.com/rss"


@pytest.mark.asyncio
async def test_remove_feed(db_session):
    await add_feed(db_session, "https://example.com/rss")
    await remove_feed(db_session, "https://example.com/rss")
    feeds = await list_feeds(db_session)
    assert feeds == []
