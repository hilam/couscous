## Context

CousCous uses SQLModel with async PostgreSQL. The current `Feed` model has no categorization — all feeds render in a flat list. Sprint 1 already added `user_id` to all models. The app uses Flet for UI, with views in `app/views/` and reusable controls in `app/controls/`. Services follow an async pattern taking `session` as first parameter.

## Goals / Non-Goals

**Goals:**
- Introduce a `Category` model with self-referencing hierarchy (parent/child folders)
- Allow feeds to be assigned to one category (nullable FK)
- Provide a Category tree view for CRUD management
- Group feeds by category in the feed list view
- Allow category selection when adding a new feed

**Non-Goals:**
- Drag-and-drop to move feeds between categories
- Category colors, icons, or custom ordering (all future enhancements)
- Nested categories in the feed grouping view (only one level shown at a time in feed list)
- Batch operations on categories

## Decisions

**1. Self-referencing FK on Category model**
- *Choice*: `parent_id` (FK → `categories.id`, nullable) on the `Category` model
- *Rationale*: Standard adjacency list. Simple to implement with SQLModel, sufficient for expected nesting depth (<5 levels). CTE-based recursive query for tree building.
- *Alternative considered*: Materialized path / nested sets — overkill for the expected scale and adds complexity on insert/move.

**2. Recursive tree in Python, not SQL**
- *Choice*: Fetch all categories for a user, build the tree structure in Python using dicts/lists
- *Rationale*: Simpler than recursive CTE in SQLModel, easier to debug, and the number of categories per user is expected to be small (<100). Performance difference is negligible.
- *Alternative considered*: PostgreSQL recursive CTE — better for deep hierarchies but adds complexity to the service layer and is harder to test.

**3. category_id on Feed is nullable**
- *Choice*: `category_id` defaults to NULL (uncategorized)
- *Rationale*: Backward compatible — existing feeds remain uncategorized. Users are not forced to categorize. Feeds without a category appear in an "Uncategorized" group.
- *Alternative considered*: Requiring a category — too restrictive for initial setup.

**4. Single category per feed (not many-to-many)**
- *Choice*: One `category_id` column on Feed (not a join table)
- *Rationale*: Matches the PLANO.md spec. Folder metaphor — a feed lives in one folder. Simpler UI, fewer edge cases.
- *Alternative considered*: Many-to-many tags — Sprint 4 handles entry-level tagging separately.

**5. Inline category selector in AddFeedDialog**
- *Choice*: Add a dropdown to the existing `AddFeedDialog` showing a flattened tree (indented by level)
- *Rationale*: Minimal UI changes, reuses existing dialog. The dropdown with indentation is sufficient for typical category counts.
- *Alternative considered*: Separate dialog step or modal — adds friction to the add-feed flow.

**6. Category list view as a separate route**
- *Choice*: New route `/categories` with a standalone view for managing the category tree
- *Rationale*: Separates management from consumption. Feed list view shows feeds grouped by category; category view handles CRUD. Clean separation of concerns.
- *Alternative considered*: Inline tree in the feed list sidebar — Flet has no sidebar support, and combining both would make the view too complex.

**7. Cascade on category delete: set child.parent_id to NULL**
- *Choice*: When a category is deleted, child categories have their `parent_id` set to NULL (promoted to root), and feeds in that category have `category_id` set to NULL.
- *Rationale*: Prevents accidental data loss. Safer than cascading deletes which would remove feeds.
- *Alternative considered*: Prevent deletion if category has children/feeds — too restrictive.

## Risks / Trade-offs

- **Recursive tree in Python may be slow for very large hierarchies**: Mitigation — categories per user are expected to be <100, and the tree is rebuilt on each view render which is instant at that scale.
- **No database-level constraint for circular references**: Mitigation — the service layer validates that `parent_id` does not create a cycle during create/update operations.
- **Migration requires table recreation**: Mitigation — `init_async_db()` already handles table creation on startup. Users will need to re-add their data unless a migration script is provided.
