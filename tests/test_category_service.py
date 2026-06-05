import pytest

from app.services.category_service import (
    create_category,
    delete_category,
    get_category_tree,
    list_categories,
    rename_category,
)
from app.services.feed_service import add_feed
from app.services.user_service import register


@pytest.mark.asyncio
async def test_create_root_category(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    cat = await create_category(db_session, user.id, "Tech")
    assert cat.name == "Tech"
    assert cat.parent_id is None
    assert cat.user_id == user.id


@pytest.mark.asyncio
async def test_create_child_category(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    parent = await create_category(db_session, user.id, "Tech")
    child = await create_category(db_session, user.id, "Python", parent_id=parent.id)
    assert child.name == "Python"
    assert child.parent_id == parent.id


@pytest.mark.asyncio
async def test_create_duplicate_raises(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    await create_category(db_session, user.id, "Tech")
    with pytest.raises(ValueError, match="Categoria j\u00e1 existe neste n\u00edvel"):
        await create_category(db_session, user.id, "Tech")


@pytest.mark.asyncio
async def test_list_categories(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    await create_category(db_session, user.id, "Tech")
    await create_category(db_session, user.id, "News")
    cats = await list_categories(db_session, user.id)
    assert len(cats) == 2


@pytest.mark.asyncio
async def test_get_category_tree_flat(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    await create_category(db_session, user.id, "Tech")
    await create_category(db_session, user.id, "News")
    tree = await get_category_tree(db_session, user.id)
    assert len(tree) == 2
    assert tree[0]["name"] == "News"
    assert tree[1]["name"] == "Tech"


@pytest.mark.asyncio
async def test_get_category_tree_nested(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    parent = await create_category(db_session, user.id, "Tech")
    await create_category(db_session, user.id, "Python", parent_id=parent.id)
    tree = await get_category_tree(db_session, user.id)
    assert len(tree) == 1
    assert tree[0]["name"] == "Tech"
    assert len(tree[0]["children"]) == 1
    assert tree[0]["children"][0]["name"] == "Python"


@pytest.mark.asyncio
async def test_rename_category(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    cat = await create_category(db_session, user.id, "Tech")
    renamed = await rename_category(db_session, user.id, cat.id, "Technology")
    assert renamed.name == "Technology"


@pytest.mark.asyncio
async def test_rename_duplicate_raises(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    await create_category(db_session, user.id, "Tech")
    cat2 = await create_category(db_session, user.id, "News")
    with pytest.raises(ValueError, match="Categoria j\u00e1 existe neste n\u00edvel"):
        await rename_category(db_session, user.id, cat2.id, "Tech")


@pytest.mark.asyncio
async def test_delete_category(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    cat = await create_category(db_session, user.id, "Tech")
    await delete_category(db_session, user.id, cat.id)
    cats = await list_categories(db_session, user.id)
    assert cats == []


@pytest.mark.asyncio
async def test_delete_category_promotes_children(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    parent = await create_category(db_session, user.id, "Tech")
    child = await create_category(db_session, user.id, "Python", parent_id=parent.id)
    await delete_category(db_session, user.id, parent.id)
    cats = await list_categories(db_session, user.id)
    assert len(cats) == 1
    assert cats[0].name == "Python"
    assert cats[0].parent_id is None


@pytest.mark.asyncio
async def test_delete_category_unlinks_feeds(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    cat = await create_category(db_session, user.id, "Tech")
    feed = await add_feed(db_session, user.id, "https://example.com/rss", category_id=cat.id)
    assert feed.category_id == cat.id
    await delete_category(db_session, user.id, cat.id)
    from app.services.feed_service import list_feeds
    feeds = await list_feeds(db_session, user.id)
    assert len(feeds) == 1
    assert feeds[0].category_id is None
