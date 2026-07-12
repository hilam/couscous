from sqlalchemy import func
from sqlmodel import select

from database.models.couscous import Category, Entry, Feed


async def create_category(
    session, user_id: int, name: str, parent_id: int | None = None
):
    existing = (
        await session.execute(
            select(Category).where(
                Category.user_id == user_id,
                Category.name == name,
                Category.parent_id == parent_id,
            )
        )
    ).scalar_one_or_none()
    if existing:
        msg = "Categoria já existe neste nível"
        raise ValueError(msg)

    cat = Category(user_id=user_id, name=name, parent_id=parent_id)
    session.add(cat)
    await session.commit()
    await session.refresh(cat)
    return cat


async def list_categories(session, user_id: int):
    result = await session.execute(
        select(Category).where(Category.user_id == user_id).order_by(Category.name)
    )
    return result.scalars().all()


async def get_categories_with_counts(
    session, user_id: int
) -> tuple[list[Category], dict[int, int], dict[int, int]]:
    cats = await list_categories(session, user_id)

    feed_result = await session.execute(
        select(Feed.category_id, func.count(Feed.url))  # type: ignore[arg-type]
        .where(Feed.user_id == user_id, Feed.category_id.isnot(None))  # type: ignore[union-attr]
        .group_by(Feed.category_id)  # type: ignore[arg-type]
    )
    feed_counts: dict[int, int] = {
        row[0]: row[1] for row in feed_result if row[0] is not None
    }

    unread_result = await session.execute(
        select(Feed.category_id, func.count(Entry.id))  # type: ignore[arg-type]
        .join(Entry, Entry.feed == Feed.url)  # type: ignore[arg-type]
        .where(
            Feed.user_id == user_id,
            Entry.read == 0,
            Feed.category_id.isnot(None),  # type: ignore[union-attr]
        )
        .group_by(Feed.category_id)  # type: ignore[arg-type]
    )
    unread_counts: dict[int, int] = {
        row[0]: row[1] for row in unread_result if row[0] is not None
    }

    return cats, feed_counts, unread_counts


async def _collect_descendant_ids(session, user_id: int, category_id: int) -> list[int]:
    cats = (
        (await session.execute(select(Category).where(Category.user_id == user_id)))
        .scalars()
        .all()
    )

    children_map: dict[int | None, list[int]] = {}
    for c in cats:
        if c.id is not None:
            children_map.setdefault(c.parent_id, []).append(c.id)

    result: list[int] = []
    stack = [category_id]
    while stack:
        cid = stack.pop()
        result.append(cid)
        stack.extend(children_map.get(cid, []))
    return result


async def rename_category(session, user_id: int, category_id: int, new_name: str):
    cat = (
        await session.execute(
            select(Category).where(
                Category.id == category_id, Category.user_id == user_id
            )
        )
    ).scalar_one_or_none()
    if not cat:
        msg = "Categoria não encontrada"
        raise ValueError(msg)

    duplicate = (
        await session.execute(
            select(Category).where(
                Category.user_id == user_id,
                Category.name == new_name,
                Category.parent_id == cat.parent_id,
                Category.id != category_id,
            )
        )
    ).scalar_one_or_none()
    if duplicate:
        msg = "Categoria já existe neste nível"
        raise ValueError(msg)

    cat.name = new_name
    await session.commit()
    await session.refresh(cat)
    return cat


async def delete_category(session, user_id: int, category_id: int):
    cat = (
        await session.execute(
            select(Category).where(
                Category.id == category_id, Category.user_id == user_id
            )
        )
    ).scalar_one_or_none()
    if not cat:
        msg = "Categoria não encontrada"
        raise ValueError(msg)

    children = (
        (
            await session.execute(
                select(Category).where(
                    Category.parent_id == category_id, Category.user_id == user_id
                )
            )
        )
        .scalars()
        .all()
    )
    for child in children:
        child.parent_id = None
        session.add(child)

    feeds = (
        (
            await session.execute(
                select(Feed).where(
                    Feed.category_id == category_id, Feed.user_id == user_id
                )
            )
        )
        .scalars()
        .all()
    )
    for feed in feeds:
        feed.category_id = None
        session.add(feed)

    await session.delete(cat)
    await session.commit()
