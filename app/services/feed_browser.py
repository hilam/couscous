from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from sqlmodel import select

from app.services.category_service import (
    build_category_tree,
    get_categories_with_counts,
)
from app.services.entry_service import list_recent
from app.services.search_service import search_entries
from app.services.tag_service import get_distinct_tags_with_counts
from database.models.couscous import Entry, EntryTag

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class ExploreState:
    selected_category_id: int | None = None
    expanded_ids: set[int] = field(default_factory=set)
    selected_tags: set[str] = field(default_factory=set)
    is_searching: bool = False
    entries: list[Entry] = field(default_factory=list)
    tag_map: dict[int, list[str]] = field(default_factory=dict)
    tree: list[dict] = field(default_factory=list)
    tag_counts: list[tuple[str, int]] = field(default_factory=list)


async def load(session: AsyncSession, user_id: int) -> ExploreState:
    cats, feed_counts, unread_counts = await get_categories_with_counts(
        session, user_id
    )
    tree = build_category_tree(cats, feed_counts, unread_counts)
    tag_counts = await get_distinct_tags_with_counts(session, user_id)
    entries = await list_recent(session, user_id, limit=50)
    tag_map = await _load_entry_tags(session, entries)
    return ExploreState(
        entries=entries, tag_map=tag_map, tree=tree, tag_counts=tag_counts
    )


async def select_category(
    session: AsyncSession, state: ExploreState, cat_id: int | None, user_id: int
) -> ExploreState:
    expanded_ids = set(state.expanded_ids)
    selected_category_id = state.selected_category_id

    if cat_id is None:
        selected_category_id = None
    else:
        node = _find_node(state.tree, cat_id)
        if node:
            if node.get("children"):
                if cat_id in expanded_ids:
                    expanded_ids.discard(cat_id)
                else:
                    expanded_ids.add(cat_id)
            if node.get("total_feed_count", 0) > 0:
                selected_category_id = cat_id

    tags = list(state.selected_tags) if state.selected_tags else None
    entries = await list_recent(
        session,
        user_id,
        category_id=selected_category_id,
        tags=tags,
        limit=50,
        include_subcategories=True,
    )
    tag_map = await _load_entry_tags(session, entries)

    return ExploreState(
        selected_category_id=selected_category_id,
        expanded_ids=expanded_ids,
        selected_tags=state.selected_tags,
        tree=state.tree,
        tag_counts=state.tag_counts,
        entries=entries,
        tag_map=tag_map,
    )


async def toggle_tag(
    session: AsyncSession, state: ExploreState, tag: str, user_id: int
) -> ExploreState:
    selected_tags = set(state.selected_tags)
    if tag in selected_tags:
        selected_tags.discard(tag)
    else:
        selected_tags.add(tag)

    tags = list(selected_tags) if selected_tags else None
    entries = await list_recent(
        session,
        user_id,
        category_id=state.selected_category_id,
        tags=tags,
        limit=50,
        include_subcategories=True,
    )
    tag_map = await _load_entry_tags(session, entries)

    return ExploreState(
        selected_category_id=state.selected_category_id,
        expanded_ids=state.expanded_ids,
        selected_tags=selected_tags,
        tree=state.tree,
        tag_counts=state.tag_counts,
        entries=entries,
        tag_map=tag_map,
        is_searching=state.is_searching,
    )


async def clear_tags(
    session: AsyncSession, state: ExploreState, user_id: int
) -> ExploreState:
    entries = await list_recent(
        session,
        user_id,
        category_id=state.selected_category_id,
        limit=50,
        include_subcategories=True,
    )
    tag_map = await _load_entry_tags(session, entries)

    return ExploreState(
        selected_category_id=state.selected_category_id,
        expanded_ids=state.expanded_ids,
        tree=state.tree,
        tag_counts=state.tag_counts,
        entries=entries,
        tag_map=tag_map,
    )


async def search(
    session: AsyncSession, state: ExploreState, query: str, user_id: int
) -> ExploreState:
    query = query.strip()
    if not query:
        return await select_category(session, state, None, user_id)

    tag_filter = (
        next(iter(state.selected_tags)) if len(state.selected_tags) == 1 else None
    )
    results = await search_entries(
        session,
        query,
        user_id,
        category_id=state.selected_category_id,
        tag=tag_filter,
        limit=50,
    )
    tag_map = await _load_entry_tags(session, results)

    return ExploreState(
        selected_category_id=state.selected_category_id,
        expanded_ids=state.expanded_ids,
        selected_tags=state.selected_tags,
        tree=state.tree,
        tag_counts=state.tag_counts,
        entries=results,
        tag_map=tag_map,
        is_searching=True,
    )


async def _load_entry_tags(
    session: AsyncSession, entries: list[Entry]
) -> dict[int, list[str]]:
    if not entries:
        return {}
    entry_ids = [e.id for e in entries if e.id is not None]
    if not entry_ids:
        return {}
    result = await session.execute(
        select(EntryTag).where(EntryTag.entry_id.in_(entry_ids))  # type: ignore[attr-defined]
    )
    tag_map: dict[int, list[str]] = defaultdict(list)
    for et in result.scalars().all():
        tag_map[et.entry_id].append(et.tag)
    return tag_map


def _find_node(nodes: list[dict], target_id: int) -> dict | None:
    for node in nodes:
        if node["id"] == target_id:
            return node
        if node.get("children"):
            found = _find_node(node["children"], target_id)
            if found:
                return found
    return None
