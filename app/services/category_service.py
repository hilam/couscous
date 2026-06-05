from sqlmodel import select

from database.models.couscous import Category, Feed


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


async def get_category_tree(session, user_id: int):
    cats = await list_categories(session, user_id)
    cat_map = {
        c.id: {
            "id": c.id, "name": c.name, "parent_id": c.parent_id, "children": []
        }
        for c in cats
    }
    tree = []
    for c in cats:
        node = cat_map[c.id]
        if c.parent_id and c.parent_id in cat_map:
            cat_map[c.parent_id]["children"].append(node)
        else:
            tree.append(node)
    return tree


async def rename_category(
    session, user_id: int, category_id: int, new_name: str
):
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


async def delete_category(
    session, user_id: int, category_id: int
):
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
        await session.execute(
            select(Category).where(
                Category.parent_id == category_id, Category.user_id == user_id
            )
        )
    ).scalars().all()
    for child in children:
        child.parent_id = None
        session.add(child)

    feeds = (
        await session.execute(
            select(Feed).where(
                Feed.category_id == category_id, Feed.user_id == user_id
            )
        )
    ).scalars().all()
    for feed in feeds:
        feed.category_id = None
        session.add(feed)

    await session.delete(cat)
    await session.commit()
