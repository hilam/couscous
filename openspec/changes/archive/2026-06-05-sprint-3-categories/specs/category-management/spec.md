## ADDED Requirements

### Requirement: Create category
The system SHALL allow the user to create a new category with a name. Each category SHALL belong to the authenticated user.

#### Scenario: Create root category
- **WHEN** user creates a category named "Tech" without specifying a parent
- **THEN** the system stores a new category with `parent_id = NULL` and shows it at the root level

#### Scenario: Create child category
- **WHEN** user creates a category named "Python" under an existing "Tech" category
- **THEN** the system stores a new category with `parent_id` pointing to the "Tech" category

#### Scenario: Duplicate name at same level
- **WHEN** user tries to create a category with a name that already exists under the same parent (or root)
- **THEN** the system rejects with an error message "Categoria já existe neste nível"

### Requirement: List categories as tree
The system SHALL return all categories for the authenticated user organized as a hierarchical tree structure.

#### Scenario: Flat categories
- **WHEN** user has two root-level categories "Tech" and "News" with no children
- **THEN** the system returns both categories at the root level with no children

#### Scenario: Nested categories
- **WHEN** user has "Tech" as root and "Python" as a child of "Tech"
- **THEN** the system returns "Tech" with "Python" nested inside its children list

#### Scenario: No categories
- **WHEN** user has no categories
- **THEN** the system returns an empty tree

### Requirement: Rename category
The system SHALL allow the user to rename an existing category.

#### Scenario: Successful rename
- **WHEN** user renames "Tech" to "Technology"
- **THEN** the system updates the category name and the new name appears in the tree

#### Scenario: Rename to duplicate name
- **WHEN** user renames a category to a name that already exists under the same parent
- **THEN** the system rejects with an error message "Categoria já existe neste nível"

### Requirement: Delete category
The system SHALL allow the user to delete a category. Child categories SHALL be promoted to root level (`parent_id` set to NULL). Feeds in the deleted category SHALL have `category_id` set to NULL.

#### Scenario: Delete empty category
- **WHEN** user deletes a category that has no children and no feeds
- **THEN** the system removes the category from the database

#### Scenario: Delete category with children
- **WHEN** user deletes a category that has child categories
- **THEN** the system removes the category and sets its children's `parent_id` to NULL

#### Scenario: Delete category with feeds
- **WHEN** user deletes a category that has feeds assigned
- **THEN** the system removes the category and sets those feeds' `category_id` to NULL
