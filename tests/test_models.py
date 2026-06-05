from datetime import datetime, timezone

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import select

from database.models.couscous import Entry, Feed, FeedMetadata, FeedTag, User
from tests.test_factory import make_user


@pytest.mark.asyncio
async def test_user_create(db_session):
    user = User(name="alice", password="secret")
    db_session.add(user)
    await db_session.commit()
    assert user.id is not None


@pytest.mark.asyncio
async def test_user_duplicate_name_raises(db_session):
    user1 = User(name="bob", password="pass1")
    db_session.add(user1)
    await db_session.commit()

    user2 = User(name="bob", password="pass2")
    db_session.add(user2)
    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_feed_create(db_session):
    user = await make_user(db_session)
    feed = Feed(url="https://example.com/rss", user_id=user.id)
    db_session.add(feed)
    await db_session.commit()

    assert feed.stale == 0
    assert feed.updates_enabled == 1
    assert feed.added is not None


@pytest.mark.asyncio
async def test_feed_duplicate_url_raises(db_session):
    user = await make_user(db_session)
    feed1 = Feed(url="https://example.com/dup", user_id=user.id)
    db_session.add(feed1)
    await db_session.commit()

    feed2 = Feed(url="https://example.com/dup", user_id=user.id)
    db_session.add(feed2)
    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_feed_invalid_user_id_raises(db_session):
    feed = Feed(url="https://example.com/rss", user_id=99999)
    db_session.add(feed)
    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_entry_create(db_session):
    user = await make_user(db_session)
    feed = Feed(url="https://example.com/rss", user_id=user.id)
    db_session.add(feed)
    await db_session.commit()
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    entry = Entry(
        feed=feed.url,
        user_id=user.id,
        title="Test",
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
    assert entry.id is not None
    assert entry.read == 0
    assert entry.important == 0


@pytest.mark.asyncio
async def test_entry_invalid_feed_raises(db_session):
    user = await make_user(db_session)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    entry = Entry(
        feed="https://example.com/nonexistent",
        user_id=user.id,
        title="Test",
        link="https://example.com/a1",
        published=now,
        last_updated=now,
        first_updated=now,
        first_updated_epoch=now,
        added_by="test",
        feed_order=0,
    )
    db_session.add(entry)
    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_feed_entry_relationship(db_session):
    user = await make_user(db_session)
    feed = Feed(url="https://example.com/rss", user_id=user.id)
    db_session.add(feed)
    await db_session.commit()
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    for i in range(2):
        entry = Entry(
            feed=feed.url,
            user_id=user.id,
            title=f"Article {i}",
            link=f"https://example.com/a{i}",
            published=now,
            last_updated=now,
            first_updated=now,
            first_updated_epoch=now,
            added_by="test",
            feed_order=i,
        )
        db_session.add(entry)
    await db_session.commit()

    result = await db_session.execute(
        select(Feed).where(Feed.url == feed.url).options(selectinload(Feed.entries))
    )
    feed_loaded = result.scalar_one()
    assert len(feed_loaded.entries) == 2

    entry = feed_loaded.entries[0]
    assert entry.url_feed is not None
    assert entry.url_feed.url == feed.url


@pytest.mark.asyncio
async def test_feed_metadata_create(db_session):
    user = await make_user(db_session)
    feed = Feed(url="https://example.com/rss", user_id=user.id)
    db_session.add(feed)
    await db_session.commit()

    md = FeedMetadata(feed=feed.url, key="language", value="en")
    db_session.add(md)
    await db_session.commit()

    result = await db_session.execute(
        select(FeedMetadata).where(
            FeedMetadata.feed == feed.url, FeedMetadata.key == "language"
        )
    )
    found = result.scalar_one()
    assert found.value == "en"





@pytest.mark.asyncio
async def test_feed_metadata_duplicate_raises(db_session):
    user = await make_user(db_session)
    feed = Feed(url="https://example.com/rss", user_id=user.id)
    db_session.add(feed)
    await db_session.commit()

    md1 = FeedMetadata(feed=feed.url, key="lang", value="en")
    db_session.add(md1)
    await db_session.commit()

    md2 = FeedMetadata(feed=feed.url, key="lang", value="fr")
    db_session.add(md2)
    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_feed_tag_create(db_session):
    user = await make_user(db_session)
    feed = Feed(url="https://example.com/rss", user_id=user.id)
    db_session.add(feed)
    await db_session.commit()

    tag = FeedTag(feed=feed.url, tag="technology")
    db_session.add(tag)
    await db_session.commit()

    result = await db_session.execute(select(FeedTag).where(FeedTag.feed == feed.url))
    tags = result.scalars().all()
    assert len(tags) == 1
    assert tags[0].tag == "technology"


@pytest.mark.asyncio
async def test_feed_tag_duplicate_raises(db_session):
    user = await make_user(db_session)
    feed = Feed(url="https://example.com/rss", user_id=user.id)
    db_session.add(feed)
    await db_session.commit()

    tag1 = FeedTag(feed=feed.url, tag="tech")
    db_session.add(tag1)
    await db_session.commit()

    tag2 = FeedTag(feed=feed.url, tag="tech")
    db_session.add(tag2)
    with pytest.raises(IntegrityError):
        await db_session.commit()
