from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import UTC, datetime
from time import mktime
from typing import TYPE_CHECKING

import feedparser
import httpx
from sqlmodel import select

from database.models.couscous import Entry, Feed

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class ParsedEntry:
    id: str
    link: str
    title: str | None = None
    summary: str | None = None
    content: str | None = None
    author: str | None = None
    published: datetime | None = None


@dataclass
class FeedFetchResult:
    title: str | None = None
    link: str | None = None
    entries: list[ParsedEntry] | None = field(default_factory=list)
    error: str | None = None


async def refresh_all_feeds(
    session: AsyncSession,
    user_id: int,
    client: httpx.AsyncClient | None = None,
) -> None:
    result = await session.execute(select(Feed).where(Feed.user_id == user_id))
    feeds = result.scalars().all()

    for feed in feeds:
        await refresh_single_feed(session, feed, client=client)


async def refresh_single_feed(
    session: AsyncSession,
    feed: Feed,
    client: httpx.AsyncClient | None = None,
) -> None:
    result = await _fetch_feed(feed.url, client)

    feed.last_exception = None

    if result.error:
        feed.last_exception = result.error
        await session.commit()
        return

    feed.title = result.title or feed.title
    feed.link = result.link or feed.link
    feed.updated = datetime.now(UTC).replace(tzinfo=None)
    await session.commit()

    for entry_data in result.entries or []:
        existing = (
            await session.execute(
                select(Entry).where(
                    Entry.feed == feed.url,
                    Entry.link == entry_data.link,
                )
            )
        ).scalar_one_or_none()

        if existing:
            continue

        now = datetime.now(UTC).replace(tzinfo=None)
        entry = Entry(
            feed=feed.url,
            user_id=feed.user_id,
            title=entry_data.title,
            link=entry_data.link,
            summary=entry_data.summary,
            content=entry_data.content,
            author=entry_data.author,
            published=entry_data.published or now,
            last_updated=now,
            first_updated=now,
            first_updated_epoch=now,
            added_by="system",
            feed_order=0,
        )
        session.add(entry)

    await session.commit()


async def _fetch_feed(
    url: str, client: httpx.AsyncClient | None = None
) -> FeedFetchResult:
    close_client = False
    if client is None:
        client = httpx.AsyncClient(timeout=30)
        close_client = True

    try:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()

        text = response.text
        parsed = await asyncio.to_thread(feedparser.parse, text)

        if parsed.bozo and not parsed.entries:
            return FeedFetchResult(error="Failed to parse feed")

        title = parsed.feed.get("title")
        link = parsed.feed.get("link")
        entries = [
            e for e in (_parse_entry(e) for e in parsed.entries) if e is not None
        ]

        return FeedFetchResult(title=title, link=link, entries=entries)

    except Exception as e:
        return FeedFetchResult(error=str(e))
    finally:
        if close_client:
            await client.aclose()


def _parse_entry(entry_data) -> ParsedEntry | None:
    try:
        entry_id = entry_data.get("id") or entry_data.get("link")
        if not entry_id:
            return None

        published = None
        if hasattr(entry_data, "published_parsed") and entry_data.published_parsed:
            published = datetime.fromtimestamp(
                mktime(entry_data.published_parsed), tz=UTC
            ).replace(tzinfo=None)

        content = None
        if entry_data.get("content"):
            content = entry_data["content"][0].get("value")

        return ParsedEntry(
            id=entry_id,
            link=entry_data.get("link"),
            title=entry_data.get("title"),
            summary=entry_data.get("summary"),
            content=content,
            author=entry_data.get("author"),
            published=published,
        )

    except Exception:
        return None
