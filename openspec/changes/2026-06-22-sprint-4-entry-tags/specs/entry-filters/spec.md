## MODIFIED Requirements

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
