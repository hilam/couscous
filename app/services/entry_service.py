from sqlmodel import desc, select

from app.services.category_service import _collect_descendant_ids
from database.models.couscous import Entry, EntryTag, Feed


async def list_recent(  # noqa: PLR0913
    session,
    user_id: int,
    *,
    category_id: int | None = None,
    tags: list[str] | None = None,
    limit: int = 50,
    include_subcategories: bool = False,
):
    """List recent entries across all feeds for a user.

    Supports optional category and tag filters.
    When include_subcategories is True, entries from descendant categories
    are also included.
    """
    query = select(Entry).where(Entry.user_id == user_id)

    if category_id is not None:
        if include_subcategories:
            cat_ids = await _collect_descendant_ids(session, user_id, category_id)
            feed_ids = select(Feed.url).where(
                Feed.user_id == user_id, Feed.category_id.in_(cat_ids)  # type: ignore[attr-defined]
            )
        else:
            feed_ids = select(Feed.url).where(
                Feed.user_id == user_id, Feed.category_id == category_id
            )
        query = query.where(Entry.feed.in_(feed_ids))  # type: ignore[attr-defined]

    if tags:
        for tag in tags:
            query = query.where(
                Entry.id.in_(  # type: ignore[attr-defined,union-attr]
                    select(EntryTag.entry_id).where(
                        EntryTag.tag == tag.strip().lower(),
                        EntryTag.user_id == user_id,
                    )
                )
            )

    query = query.order_by(desc(Entry.published)).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


async def list_entries(  # noqa: PLR0913
    session,
    feed_url: str,
    *,
    user_id: int | None = None,
    unread_only: bool = False,
    important_only: bool = False,
    tag: str | None = None,
):
    query = select(Entry).where(Entry.feed == feed_url)
    if user_id is not None:
        query = query.where(Entry.user_id == user_id)
    if unread_only:
        query = query.where(Entry.read == 0)
    if important_only:
        query = query.where(Entry.important == 1)
    if tag:
        query = query.where(
            Entry.id.in_(  # type: ignore[attr-defined,union-attr]
                select(EntryTag.entry_id).where(
                    EntryTag.tag == tag.strip().lower(),
                    EntryTag.user_id == user_id,
                )
            )
        )
    query = query.order_by(desc(Entry.published))
    result = await session.execute(query)
    return result.scalars().all()


async def get_entry(session, entry_id: int):
    result = await session.execute(select(Entry).where(Entry.id == entry_id))
    return result.scalar_one_or_none()


async def mark_read(session, entry_id: int, user_id: int, *, read: bool = True):
    entry = (
        await session.execute(
            select(Entry).where(Entry.id == entry_id, Entry.user_id == user_id)
        )
    ).scalar_one_or_none()
    if entry:
        entry.read = 1 if read else 0
        await session.commit()


async def mark_important(
    session, entry_id: int, user_id: int, *, important: bool = True
):
    entry = (
        await session.execute(
            select(Entry).where(Entry.id == entry_id, Entry.user_id == user_id)
        )
    ).scalar_one_or_none()
    if entry:
        entry.important = 1 if important else 0
        await session.commit()


async def get_unread_count(session, user_id: int) -> int:
    result = await session.execute(
        select(Entry).where(Entry.user_id == user_id, Entry.read == 0)
    )
    return len(result.scalars().all())
