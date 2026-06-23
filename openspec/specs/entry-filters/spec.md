## Purpose

Define requirements for filtering RSS feed entries in CousCous. (TBD)

## Requirements

### Requirement: Filter entries by read status
The system SHALL allow the user to filter the entry list to show only unread entries.

#### Scenario: Show only unread entries
- **WHEN** user toggles the "Não lidos" filter in the entry list view
- **THEN** the system displays only entries where `is_read` is false

#### Scenario: Show all entries
- **WHEN** user toggles the "Não lidos" filter off
- **THEN** the system displays all entries for the current feed

### Requirement: Filter entries by importance
The system SHALL allow the user to filter the entry list to show only important (starred) entries.

#### Scenario: Show only important entries
- **WHEN** user toggles the "Importantes" filter in the entry list view
- **THEN** the system displays only entries where `is_important` is true

#### Scenario: Show all entries after important filter
- **WHEN** user toggles the "Importantes" filter off
- **THEN** the system displays all entries for the current feed

### Requirement: Filter entries by tag
O sistema DEVE permitir ao usuário filtrar a lista de entries por uma tag específica.

#### Scenario: Filtrar por tag
- **WHEN** o usuário seleciona uma tag no filtro da `entry_list_view.py`
- **THEN** o sistema exibe apenas as entries que possuem a tag selecionada

#### Scenario: Remover filtro de tag
- **WHEN** o usuário desseleciona a tag no filtro
- **THEN** o sistema volta a exibir todas as entries do feed (respeitando outros filtros ativos como "não lidos" e "importantes")

#### Scenario: Combinação de filtros
- **WHEN** o usuário ativa simultaneamente o filtro de tag, o filtro "não lidos" e o filtro "importantes"
- **THEN** o sistema exibe apenas entries que satisfazem TODOS os critérios (possuem a tag, não foram lidas e são importantes)
