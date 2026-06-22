from datetime import datetime

import pytest

from app.services.feed_fetcher import FeedFetcher, FeedFetchResult, ParsedEntry
from app.services.refresh_service import refresh_all_feeds, refresh_single_feed
from database.models.couscous import Entry
from tests.test_factory import make_entry, make_feed, make_user


class FakeFeedFetcher(FeedFetcher):
    def __init__(self, result: FeedFetchResult):
        self.result = result

    async def fetch(self, url: str) -> FeedFetchResult:
        return self.result


def make_result(title="Test RSS Feed", link="https://example.com", num_entries=3):
    entries = []
    for i in range(1, num_entries + 1):
        entries.append(
            ParsedEntry(
                id=f"https://example.com/article{i}",
                link=f"https://example.com/article{i}",
                title=f"Article {i}",
                author=f"Author {i}",
                summary=f"Summary {i}",
                content=f"<p>Content {i}</p>",
                published=datetime(2024, 1, i),
            )
        )
    return FeedFetchResult(title=title, link=link, entries=entries)


@pytest.mark.asyncio
async def test_refresh_single_feed_rss(db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    fetcher = FakeFeedFetcher(make_result(title="Test RSS Feed"))

    await refresh_single_feed(db_session, feed, fetcher=fetcher)

    await db_session.refresh(feed)
    assert feed.title == "Test RSS Feed"
    assert feed.link == "https://example.com"
    assert feed.last_exception is None

    from sqlmodel import select

    result = await db_session.execute(select(Entry).where(Entry.feed == feed.url))
    entries = result.scalars().all()
    assert len(entries) == 3


@pytest.mark.asyncio
async def test_refresh_single_feed_atom(db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    fetcher = FakeFeedFetcher(
        FeedFetchResult(
            title="Atom Feed",
            link="https://example.com/atom",
            entries=[
                ParsedEntry(
                    id="https://example.com/atom1",
                    link="https://example.com/atom1",
                    title="Atom Article 1",
                ),
            ],
        )
    )

    await refresh_single_feed(db_session, feed, fetcher=fetcher)

    await db_session.refresh(feed)
    assert feed.last_exception is None

    from sqlmodel import select

    result = await db_session.execute(select(Entry).where(Entry.feed == feed.url))
    entries = result.scalars().all()
    assert len(entries) == 1
    assert entries[0].title == "Atom Article 1"


@pytest.mark.asyncio
async def test_refresh_skips_duplicate_entries(db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    await make_entry(
        db_session,
        feed_url=feed.url,
        user_id=user.id,
        link="https://example.com/article1",
    )

    fetcher = FakeFeedFetcher(make_result())
    await refresh_single_feed(db_session, feed, fetcher=fetcher)

    await db_session.refresh(feed)
    assert feed.last_exception is None

    from sqlmodel import select

    result = await db_session.execute(select(Entry).where(Entry.feed == feed.url))
    entries = result.scalars().all()
    assert len(entries) == 3


@pytest.mark.asyncio
async def test_refresh_http_404(db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    fetcher = FakeFeedFetcher(FeedFetchResult(error="404 Client Error"))

    await refresh_single_feed(db_session, feed, fetcher=fetcher)

    await db_session.refresh(feed)
    assert feed.last_exception is not None
    assert "404" in feed.last_exception


@pytest.mark.asyncio
async def test_refresh_timeout(db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    fetcher = FakeFeedFetcher(FeedFetchResult(error="Request timed out"))

    await refresh_single_feed(db_session, feed, fetcher=fetcher)

    await db_session.refresh(feed)
    assert feed.last_exception is not None
    assert "timed out" in feed.last_exception.lower()


@pytest.mark.asyncio
async def test_refresh_empty_response(db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    fetcher = FakeFeedFetcher(FeedFetchResult(entries=[]))

    await refresh_single_feed(db_session, feed, fetcher=fetcher)

    await db_session.refresh(feed)
    assert feed.last_exception is None

    from sqlmodel import select

    result = await db_session.execute(select(Entry).where(Entry.feed == feed.url))
    entries = result.scalars().all()
    assert len(entries) == 0


@pytest.mark.asyncio
async def test_refresh_malformed_xml(db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    fetcher = FakeFeedFetcher(FeedFetchResult(entries=[]))

    await refresh_single_feed(db_session, feed, fetcher=fetcher)

    await db_session.refresh(feed)
    assert feed.last_exception is None


@pytest.mark.asyncio
async def test_refresh_skips_malformed_entries(db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)

    entries = [
        ParsedEntry(
            id=f"https://example.com/valid{i}",
            link=f"https://example.com/valid{i}",
            title=f"Valid Article {i}",
            author=f"Author {i}",
            summary=f"Valid Summary {i}",
            published=datetime(2024, 1, i),
        )
        for i in range(1, 3)
    ]
    fetcher = FakeFeedFetcher(FeedFetchResult(entries=entries))

    await refresh_single_feed(db_session, feed, fetcher=fetcher)

    await db_session.refresh(feed)
    assert feed.last_exception is None

    from sqlmodel import select

    result = await db_session.execute(select(Entry).where(Entry.feed == feed.url))
    entries = result.scalars().all()
    assert len(entries) == 2


@pytest.mark.asyncio
async def test_refresh_entry_metadata(db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    fetcher = FakeFeedFetcher(make_result(num_entries=1))

    await refresh_single_feed(db_session, feed, fetcher=fetcher)

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
async def test_refresh_entry_metadata_no_content(db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    fetcher = FakeFeedFetcher(
        FeedFetchResult(
            title="Test Feed",
            link="https://example.com",
            entries=[
                ParsedEntry(
                    id="https://example.com/article1",
                    link="https://example.com/article1",
                    title="Article 1",
                    author="Author 1",
                    summary="Summary 1",
                    content=None,
                    published=datetime(2024, 1, 1),
                ),
            ],
        )
    )

    await refresh_single_feed(db_session, feed, fetcher=fetcher)

    from sqlmodel import select

    result = await db_session.execute(select(Entry).where(Entry.feed == feed.url))
    entries = result.scalars().all()
    assert entries[0].content is None


@pytest.mark.asyncio
async def test_refresh_all_feeds(db_session):
    user = await make_user(db_session)
    feed1 = await make_feed(
        db_session, url="https://example.com/feed1", user_id=user.id
    )
    feed2 = await make_feed(
        db_session, url="https://example.com/feed2", user_id=user.id
    )
    feed3 = await make_feed(
        db_session, url="https://example.com/feed3", user_id=user.id
    )

    fetcher = FakeFeedFetcher(make_result(num_entries=1))

    await refresh_all_feeds(db_session, user.id, fetcher=fetcher)

    from sqlmodel import select

    result = await db_session.execute(select(Entry).where(Entry.user_id == user.id))
    entries = result.scalars().all()
    assert len(entries) == 3
