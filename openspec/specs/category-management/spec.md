## Purpose

Define requirements for managing hierarchical categories in CousCous.

## Requirements

### Requirement: Create category
The system SHALL allow the user to create a new category with a name. Each category SHALL belong to the authenticated user. The dialog SHALL include both a "Criar" button (save and close) and a "Criar outro" button (save, clear fields, and keep dialog open for continued entry).

#### Scenario: Create root category
- **WHEN** user creates a category named "Tech" without specifying a parent
- **THEN** the system stores a new category with `parent_id = NULL` and shows it at the root level

#### Scenario: Create child category
- **WHEN** user creates a category named "Python" under an existing "Tech" category
- **THEN** the system stores a new category with `parent_id` pointing to the "Tech" category

#### Scenario: Duplicate name at same level
- **WHEN** user tries to create a category with a name that already exists under the same parent (or root)
- **THEN** the system rejects with an error message "Categoria já existe neste nível"

#### Scenario: Criar button saves and closes
- **WHEN** user fills the category name and clicks "Criar"
- **THEN** the system saves the category and closes the dialog

#### Scenario: Criar outro button saves and continues
- **WHEN** user fills the category name and clicks "Criar outro"
- **THEN** the system saves the category, clears the name field, reloads the parent dropdown with the new category available as an option, refreshes the category tree in the background, and keeps the dialog open with focus returned to the name field

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

### Requirement: Multi-category creation
O sistema DEVE oferecer um botão "Criar outro" no diálogo de nova categoria que salva o registro atual e mantém o formulário aberto para criar categorias adicionais em sequência.

#### Scenario: Criar outro após primeira categoria
- **WHEN** o usuário preenche o nome da categoria, seleciona um pai opcional e clica em "Criar outro"
- **THEN** o sistema salva a nova categoria, limpa o campo de nome, recarrega o dropdown de categorias-pai (incluindo a categoria recém-criada), atualiza a árvore de categorias visível e mantém o diálogo aberto com o foco no campo de nome

#### Scenario: Criar outro com nome vazio
- **WHEN** o usuário clica em "Criar outro" com o campo de nome vazio
- **THEN** o sistema não faz nada (não salva, não fecha, não limpa)

#### Scenario: Criar outro com nome duplicado
- **WHEN** o usuário clica em "Criar outro" com um nome que já existe no mesmo nível
- **THEN** o sistema exibe o snackbar "Categoria já existe neste nível", mantém o nome preenchido e mantém o diálogo aberto

### Requirement: Keyboard navigation in category creation form
O sistema DEVE permitir navegação por teclado entre os campos do formulário de criação de categoria.

#### Scenario: ENTER no campo de nome
- **WHEN** o usuário pressiona ENTER no campo de nome da categoria
- **THEN** o foco é movido para o dropdown de categoria-pai
