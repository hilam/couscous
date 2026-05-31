import asyncio
import datetime as _dt

import feedparser
import httpx
from sqlmodel import select

from database.models.couscous import Entry, Feed


async def refresh_all_feeds(session):
    result = await session.execute(select(Feed))
    feeds = result.scalars().all()

    for feed in feeds:
        await refresh_single_feed(session, feed)


async def refresh_single_feed(session, feed: Feed):
    try:
        response = await asyncio.to_thread(httpx.get, feed.url, timeout=30)
        response.raise_for_status()

        parsed = await asyncio.to_thread(feedparser.parse, response.text)

        feed.title = parsed.feed.get("title", feed.title)
        feed.link = parsed.feed.get("link", feed.link)
        feed.updated = _dt.datetime.now(_dt.UTC).replace(tzinfo=None)
        feed.last_exception = None

        for entry_data in parsed.entries:
            entry_id = entry_data.get("id") or entry_data.get("link")
            if not entry_id:
                continue

            existing = (
                await session.execute(
                    select(Entry).where(
                        Entry.feed == feed.url, Entry.link == entry_data.get("link")
                    )
                )
            ).scalar_one_or_none()

            if existing:
                continue

            published = None
            if hasattr(entry_data, "published_parsed") and entry_data.published_parsed:
                from time import mktime

                published = _dt.datetime.fromtimestamp(
                    mktime(entry_data.published_parsed), tz=_dt.UTC
                ).replace(tzinfo=None)

            entry = Entry(
                feed=feed.url,
                title=entry_data.get("title"),
                link=entry_data.get("link"),
                summary=entry_data.get("summary"),
                content=entry_data.get("content", [{}])[0].get("value")
                if entry_data.get("content")
                else None,
                author=entry_data.get("author"),
                published=published,
                last_updated=_dt.datetime.now(_dt.UTC).replace(tzinfo=None),
                first_updated=_dt.datetime.now(_dt.UTC).replace(tzinfo=None),
                first_updated_epoch=_dt.datetime.now(_dt.UTC).replace(tzinfo=None),
                added_by="system",
                feed_order=0,
            )
            session.add(entry)

        await session.commit()

    except Exception as e:
        feed.last_exception = str(e)
        await session.commit()
