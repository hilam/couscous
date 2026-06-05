## MODIFIED Requirements

### Requirement: List all feeds
The system SHALL display a list of all registered RSS feeds for the authenticated user on the feeds page, grouped by category. Uncategorized feeds SHALL appear under a "Sem categoria" header displayed last.

#### Scenario: View feed list grouped by category
- **WHEN** user navigates to `/feeds` and has feeds in one or more categories
- **THEN** the system displays feeds grouped under their respective category section headers

#### Scenario: View feed list with uncategorized feeds
- **WHEN** user navigates to `/feeds` and has feeds without a category
- **THEN** the system displays those feeds under a "Sem categoria" section header, shown after all categorized groups

#### Scenario: Feed list is empty
- **WHEN** user navigates to `/feeds` and no feeds exist for the current user
- **THEN** the system displays an empty state message "Nenhum feed adicionado"
