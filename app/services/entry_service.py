from datetime import datetime

from sqlalchemy import and_, or_
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
    before: datetime | None = None,
    before_id: int | None = None,
):
    """List recent entries across all feeds for a user.

    Supports optional category and tag filters.
    When include_subcategories is True, entries from descendant categories
    are also included.

    Returns projected rows (id, title, link, summary, published, read,
    author) — `content` is NOT loaded. Supports keyset pagination via
    (before, before_id); entries with published IS NULL are excluded once
    a cursor is applied.
    """
    query = select(  # type: ignore[call-overload,misc]
        Entry.id,
        Entry.title,
        Entry.link,
        Entry.summary,
        Entry.published,
        Entry.read,
        Entry.author,
    ).where(Entry.user_id == user_id)

    if category_id is not None:
        if include_subcategories:
            cat_ids = await _collect_descendant_ids(session, user_id, category_id)
            feed_ids = select(Feed.url).where(
                Feed.user_id == user_id,
                Feed.category_id.in_(cat_ids),  # type: ignore[union-attr]
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

    if before is not None:
        query = query.where(
            or_(
                Entry.published < before,  # type: ignore[operator,arg-type]
                and_(  # type: ignore[arg-type]
                    Entry.published == before,  # type: ignore[arg-type]
                    Entry.id < before_id,  # type: ignore[operator,arg-type]
                ),
            )
        )

    query = query.order_by(desc(Entry.published), desc(Entry.id)).limit(limit)
    result = await session.execute(query)
    return result.all()


async def list_entries(  # noqa: PLR0913
    session,
    feed_url: str,
    *,
    user_id: int,
    unread_only: bool = False,
    important_only: bool = False,
    tag: str | None = None,
    before: datetime | None = None,
    before_id: int | None = None,
    limit: int = 50,
):
    """Keyset-paginated list of entries for a feed, scoped to the user.

    Returns projected rows (id, title, link, summary, published, read,
    author) — `content` and `important` are NOT loaded, so full ORM
    entities are avoided in list paths. Use get_entry for the full entity.

    Cursor: pass (before, before_id) from the last row of the previous
    page. Limitation: entries with published IS NULL are excluded once a
    cursor is applied, since the comparison against NULL never matches.
    """
    query = select(  # type: ignore[call-overload,misc]
        Entry.id,
        Entry.title,
        Entry.link,
        Entry.summary,
        Entry.published,
        Entry.read,
        Entry.author,
    ).where(Entry.feed == feed_url, Entry.user_id == user_id)
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
    if before is not None:
        query = query.where(
            or_(
                Entry.published < before,  # type: ignore[operator,arg-type]
                and_(  # type: ignore[arg-type]
                    Entry.published == before,  # type: ignore[arg-type]
                    Entry.id < before_id,  # type: ignore[operator,arg-type]
                ),
            )
        )
    query = query.order_by(desc(Entry.published), desc(Entry.id)).limit(limit)
    result = await session.execute(query)
    return result.all()


async def get_entry(session, entry_id: int, user_id: int):
    return (
        await session.execute(
            select(Entry).where(Entry.id == entry_id, Entry.user_id == user_id)
        )
    ).scalar_one_or_none()


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
