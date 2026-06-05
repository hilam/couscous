## Why

Feeds currently display as a flat list, which becomes unmanageable as users subscribe to more feeds. Hierarchical categories (folders) let users organize feeds into logical groups (e.g., "Tech", "News", "Blogs"), improving navigation and reducing cognitive load. This is a core RSS reader feature expected by users.

## What Changes

- Add a `Category` model with self-referencing `parent_id` for arbitrary nesting depth
- Add optional `category_id` foreign key to the `Feed` model so feeds can belong to a category
- Create `category_service.py` with CRUD operations and recursive tree queries
- Create `category_list_view.py` — a folder tree UI to browse, create, rename, and delete categories
- Adapt `AddFeedDialog` to include a category selector (dropdown with tree indentation)
- Adapt `feed_list_view.py` to group feeds by category, with uncategorized feeds shown separately
- **BREAKING**: `add_feed` in `feed_service.py` gains an optional `category_id` parameter

## Capabilities

### New Capabilities
- `category-management`: Complete CRUD for hierarchical categories (folders), including recursive tree queries to build the hierarchy. Each category belongs to a user.
- `feed-categorization`: Feeds can be assigned to a category at creation time or later. Feeds in the list view are grouped by category.

### Modified Capabilities
- `feed-management`: `add_feed` accepts an optional `category_id` parameter. `remove_feed` cascades without category side effects. The delta specifies the new parameter and behavior.
- `feed-viewing`: Feed list display changes from flat to grouped-by-category. The delta specifies grouping behavior and the "uncategorized" fallback group.

## Impact

- **Models** (`database/models/couscous.py`): New `Category` model + new column `category_id` on `Feed`
- **Services**: New `app/services/category_service.py`; modified `app/services/feed_service.py` (`add_feed` signature)
- **Views**: New `app/views/category_list_view.py`; modified `app/views/feed_list_view.py`
- **Controls**: Modified `app/controls/add_feed_dialog.py` (category selector); modified `app/controls/feed_card.py` (optional)
- **Database**: New `categories` table; migration or table recreation needed
- **Tests**: New `tests/test_category_service.py`; updates to existing feed service tests
