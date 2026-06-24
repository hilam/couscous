from sqlalchemy import text

from database.models.couscous import Entry


async def search_entries(  # noqa: PLR0913
    session,
    query: str,
    user_id: int,
    *,
    category_id: int | None = None,
    tag: str | None = None,
    limit: int = 50,
) -> list[Entry]:
    """Full-text search across all user entries using PostgreSQL tsvector/tsquery.

    Uses 'simple' configuration for multilingual support (no stemming).
    Results are ranked by ts_rank and include highlighted snippets via ts_headline.
    """
    if not query.strip():
        return []

    conditions = ["e.user_id = :user_id", "e.search_vector @@ q"]
    params: dict = {"user_id": user_id, "query": query.strip(), "limit": limit}

    if category_id is not None:
        conditions.append("f.category_id = :category_id")
        params["category_id"] = category_id

    if tag is not None and tag.strip():
        conditions.append(
            "EXISTS ("
            "SELECT 1 FROM entry_tags et "
            "WHERE et.entry_id = e.id AND et.tag = :tag"
            ")"
        )
        params["tag"] = tag.strip().lower()

    where_clause = " AND ".join(conditions)

    sql = text(  # nosec B608
        "SELECT e.id, e.feed, e.user_id, e.title, e.link, e.updated, e.author, "
        "e.published, e.summary, e.content, e.enclosures, e.original_feed, "
        "e.data_hash, e.data_hash_changed, e.read, e.read_modified, "
        "e.important, e.important_modified, e.added_by, e.last_updated, "
        "e.first_updated, e.first_updated_epoch, e.feed_order, "
        "ts_rank(e.search_vector, q) AS rank, "
        "ts_headline('simple', coalesce(e.summary, e.content, ''), "
        "q, 'MaxWords=40, MinWords=20, StartSel=<b>, StopSel=</b>'"
        ") AS snippet "
        "FROM entries e "
        "LEFT JOIN feeds f ON e.feed = f.url, "
        "plainto_tsquery('simple', :query) AS q "
        "WHERE " + where_clause + " "
        "ORDER BY rank DESC "
        "LIMIT :limit"
    )

    result = await session.execute(sql, params)
    rows = result.fetchall()

    entries = []
    for row in rows:
        entry = Entry(
            id=row.id,
            feed=row.feed,
            user_id=row.user_id,
            title=row.title,
            link=row.link,
            updated=row.updated,
            author=row.author,
            published=row.published,
            summary=row.summary,
            content=row.content,
            enclosures=row.enclosures,
            original_feed=row.original_feed,
            data_hash=row.data_hash,
            data_hash_changed=row.data_hash_changed,
            read=row.read,
            read_modified=row.read_modified,
            important=row.important,
            important_modified=row.important_modified,
            added_by=row.added_by,
            last_updated=row.last_updated,
            first_updated=row.first_updated,
            first_updated_epoch=row.first_updated_epoch,
            feed_order=row.feed_order,
        )
        if hasattr(row, "snippet"):  # noqa: SIM102
            if row.snippet:
                entry.summary = row.snippet
        entries.append(entry)

    return entries
