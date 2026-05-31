import asyncio
from datetime import datetime

import feedparser
import httpx
from sqlmodel import select

from database.models.couscous import Feed, Entry


async def refresh_all_feeds(session):
    from sqlmodel import select

    result = session.execute(select(Feed))
    feeds = result.scalars().all()

    for feed in feeds:
        await asyncio.to_thread(refresh_single_feed, session, feed)


def refresh_single_feed(session, feed: Feed):
    try:
        response = httpx.get(feed.url, timeout=30)
        response.raise_for_status()

        parsed = feedparser.parse(response.text)

        feed.title = parsed.feed.get("title", feed.title)
        feed.link = parsed.feed.get("link", feed.link)
        feed.updated = datetime.now()
        feed.last_exception = None

        for entry_data in parsed.entries:
            entry_id = entry_data.get("id") or entry_data.get("link")
            if not entry_id:
                continue

            existing = session.execute(
                select(Entry).where(
                    Entry.feed == feed.url, Entry.link == entry_data.get("link")
                )
            ).scalar_one_or_none()

            if existing:
                continue

            published = None
            if hasattr(entry_data, "published_parsed") and entry_data.published_parsed:
                from time import mktime

                published = datetime.fromtimestamp(mktime(entry_data.published_parsed))

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
                last_updated=datetime.now(),
                first_updated=datetime.now(),
                first_updated_epoch=datetime.now(),
                added_by="system",
                feed_order=0,
            )
            session.add(entry)

        session.commit()

    except Exception as e:
        feed.last_exception = str(e)
        session.commit()
