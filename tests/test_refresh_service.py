from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.services.refresh_service import refresh_all_feeds, refresh_single_feed
from database.models.couscous import Entry
from tests.test_factory import make_entry, make_feed, make_user


def _rss(title="Test RSS Feed", link="https://example.com", num_entries=3):
    items = ""
    for i in range(1, num_entries + 1):
        items += f"""<item>
    <title>Article {i}</title>
    <link>https://example.com/article{i}</link>
    <guid>https://example.com/article{i}</guid>
    <description>Summary {i}</description>
    <content:encoded><![CDATA[<p>Content {i}</p>]]></content:encoded>
    <author>Author {i}</author>
    <pubDate>Mon, 0{i} Jan 2024 00:00:00 +0000</pubDate>
  </item>"""
    return f"""<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>{title}</title>
    <link>{link}</link>
    {items}
  </channel>
</rss>"""


def _atom():
    return """<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Atom Feed</title>
  <link href="https://example.com/atom"/>
  <entry>
    <title>Atom Article 1</title>
    <link href="https://example.com/atom1"/>
    <id>https://example.com/atom1</id>
  </entry>
</feed>"""


def _client(xml: str, status: int = 200) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(
        lambda _: httpx.Response(status, text=xml),
    ))


@pytest.mark.asyncio
async def test_refresh_single_feed_rss(db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    client = _client(_rss(title="Test RSS Feed"))

    await refresh_single_feed(db_session, feed, client=client)

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
    client = _client(_atom())

    await refresh_single_feed(db_session, feed, client=client)

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

    client = _client(_rss())
    await refresh_single_feed(db_session, feed, client=client)

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
    client = _client("Not Found", status=404)

    await refresh_single_feed(db_session, feed, client=client)

    await db_session.refresh(feed)
    assert feed.last_exception is not None
    assert "404" in feed.last_exception


@pytest.mark.asyncio
async def test_refresh_empty_response(db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    xml = _rss(num_entries=0)
    client = _client(xml)

    await refresh_single_feed(db_session, feed, client=client)

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
    client = _client("<not><valid><xml>", status=200)

    await refresh_single_feed(db_session, feed, client=client)

    await db_session.refresh(feed)
    assert feed.last_exception is not None


@pytest.mark.asyncio
async def test_refresh_entry_metadata(db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    client = _client(_rss(num_entries=1))

    await refresh_single_feed(db_session, feed, client=client)

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
async def test_refresh_all_feeds(db_session):
    user = await make_user(db_session)
    await make_feed(db_session, url="https://example.com/feed1", user_id=user.id)
    await make_feed(db_session, url="https://example.com/feed2", user_id=user.id)
    await make_feed(db_session, url="https://example.com/feed3", user_id=user.id)

    client = _client(_rss(num_entries=1))

    await refresh_all_feeds(db_session, user.id, client=client)

    from sqlmodel import select

    result = await db_session.execute(select(Entry).where(Entry.user_id == user.id))
    entries = result.scalars().all()
    assert len(entries) == 3


def _rss_many(num_entries):
    items = ""
    for i in range(1, num_entries + 1):
        day = (i % 28) + 1
        items += f"""<item>
    <title>Article {i}</title>
    <link>https://example.com/big{i}</link>
    <guid>https://example.com/big{i}</guid>
    <description>Summary {i}</description>
    <pubDate>Mon, {day:02d} Jan 2024 00:00:00 +0000</pubDate>
  </item>"""
    return (
        '<rss version="2.0"><channel><title>Big</title>'
        f"<link>https://example.com</link>{items}</channel></rss>"
    )


@pytest.mark.asyncio
async def test_refresh_dedupe_batched_100_entries(db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    from sqlmodel import select

    await refresh_single_feed(db_session, feed, client=_client(_rss_many(100)))

    result = await db_session.execute(select(Entry).where(Entry.feed == feed.url))
    assert len(result.scalars().all()) == 100

    # re-refresh não insere nada novo (dedupe por link em lote)
    await refresh_single_feed(db_session, feed, client=_client(_rss_many(100)))

    result = await db_session.execute(select(Entry).where(Entry.feed == feed.url))
    assert len(result.scalars().all()) == 100


def _no_link_entries(*ids):
    from app.services.refresh_service import FeedFetchResult, ParsedEntry

    return FeedFetchResult(
        title="No Link Feed",
        entries=[ParsedEntry(id=i, link=None, title=f"No Link {i}") for i in ids],
    )


def _patched_fetch(result):
    return patch(
        "app.services.refresh_service._fetch_feed",
        AsyncMock(return_value=result),
    )


@pytest.mark.asyncio
async def test_refresh_entries_without_links_are_not_lost(db_session):
    """(a) entries com link=None e ids externos distintos entram todas."""
    from sqlmodel import select

    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)

    with _patched_fetch(_no_link_entries("urn:example:post1", "urn:example:post2")):
        await refresh_single_feed(db_session, feed)

    result = await db_session.execute(select(Entry).where(Entry.feed == feed.url))
    entries = result.scalars().all()
    assert len(entries) == 2
    assert {e.link for e in entries} == {None}
    assert {e.external_id for e in entries} == {"urn:example:post1", "urn:example:post2"}


@pytest.mark.asyncio
async def test_refresh_dedupe_by_external_id_on_reprocess(db_session):
    """(b) re-refresh com mesmo external_id não insere nada novo."""
    from sqlmodel import select

    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)

    with _patched_fetch(_no_link_entries("urn:example:post1", "urn:example:post2")):
        await refresh_single_feed(db_session, feed)
        await refresh_single_feed(db_session, feed)

    result = await db_session.execute(select(Entry).where(Entry.feed == feed.url))
    assert len(result.scalars().all()) == 2


@pytest.mark.asyncio
async def test_refresh_skips_entry_matching_persisted_external_id(db_session):
    """(c) entry já persistida com external_id é pulada pelo dedupe (sem IntegrityError)."""
    from sqlmodel import select

    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    await make_entry(
        db_session,
        feed_url=feed.url,
        user_id=user.id,
        link=None,
        external_id="urn:example:post1",
    )

    with _patched_fetch(_no_link_entries("urn:example:post1", "urn:example:post2")):
        await refresh_single_feed(db_session, feed)

    result = await db_session.execute(select(Entry).where(Entry.feed == feed.url))
    entries = result.scalars().all()
    assert len(entries) == 2
    assert sum(1 for e in entries if e.external_id == "urn:example:post1") == 1
