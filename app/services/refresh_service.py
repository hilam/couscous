from datetime import UTC, datetime

from sqlmodel import select

from app.services.feed_fetcher import FeedFetcher, HttpFeedFetcher
from database.models.couscous import Entry, Feed


async def refresh_all_feeds(session, user_id: int, fetcher: FeedFetcher | None = None):
    result = await session.execute(select(Feed).where(Feed.user_id == user_id))
    feeds = result.scalars().all()

    for feed in feeds:
        await refresh_single_feed(session, feed, fetcher=fetcher)


async def refresh_single_feed(session, feed: Feed, fetcher: FeedFetcher | None = None):
    if fetcher is None:
        fetcher = HttpFeedFetcher()

    result = await fetcher.fetch(feed.url)

    feed.last_exception = None

    if result.error:
        feed.last_exception = result.error
        await session.commit()
        return

    feed.title = result.title or feed.title
    feed.link = result.link or feed.link
    feed.updated = datetime.now(UTC).replace(tzinfo=None)
    await session.commit()

    if not result.entries:
        await session.commit()
        return

    for entry_data in result.entries:
        try:
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

        except Exception as e:
            print(f"Skipped entry in {feed.url}: {e}")

    await session.commit()
