## ADDED Requirements

### Requirement: Exibir entradas recentes cross-feed
O sistema DEVE exibir as entradas mais recentes de todos os feeds do usuário na coluna central do explore view, ordenadas por data de publicação decrescente, quando nenhuma categoria está selecionada.

#### Scenario: Estado inicial com entradas recentes
- **WHEN** o usuário acessa a home page (`/`) sem nenhuma categoria selecionada
- **THEN** a coluna central exibe as 50 entradas mais recentes de todos os feeds do usuário, ordenadas por `published DESC`

#### Scenario: Nenhuma entrada disponível
- **WHEN** o usuário acessa a home page e não possui nenhuma entrada em nenhum feed
- **THEN** a coluna central exibe mensagem "Nenhum artigo encontrado"

### Requirement: Drill-down por categoria
O sistema DEVE permitir ao usuário selecionar uma categoria na árvore lateral esquerda e filtrar as entradas da coluna central para exibir apenas artigos dos feeds pertencentes àquela categoria.

#### Scenario: Selecionar categoria com feeds
- **WHEN** o usuário toca em uma categoria na árvore lateral que possui feeds associados
- **THEN** a coluna central passa a exibir apenas as entradas dos feeds daquela categoria, ordenadas por `published DESC`

#### Scenario: Selecionar categoria sem feeds
- **WHEN** o usuário toca em uma categoria na árvore lateral que não possui feeds associados
- **THEN** a coluna central exibe mensagem "Nenhum artigo nesta categoria"

#### Scenario: Desselecionar categoria (voltar para Recentes)
- **WHEN** o usuário toca em um botão "Recentes" ou "Todas" no topo da coluna central
- **THEN** a coluna central volta a exibir as entradas recentes de todos os feeds

### Requirement: Árvore de categorias lateral
O sistema DEVE exibir a árvore hierárquica de categorias do usuário na coluna lateral esquerda do explore view, sem mostrar feeds como nós-filhos. Apenas categorias são exibidas.

#### Scenario: Categorias aninhadas
- **WHEN** o usuário possui categorias com hierarquia (ex: "Tecnologia" → "Python")
- **THEN** a árvore exibe "Tecnologia" com indentação para "Python" como filho

#### Scenario: Nenhuma categoria cadastrada
- **WHEN** o usuário não possui nenhuma categoria
- **THEN** a árvore lateral exibe mensagem "Nenhuma categoria"

### Requirement: Filtro lateral de tags (drawer direito)
O sistema DEVE exibir um drawer lateral à direita com todas as tags distintas do usuário e suas contagens de uso. O drawer é acessado por um botão `[🏷️]` no AppBar. Ao selecionar uma ou mais tags, a coluna central é filtrada para exibir apenas entradas que possuem TODAS as tags selecionadas (AND).

#### Scenario: Abrir drawer de tags
- **WHEN** o usuário toca no botão de tags no AppBar
- **THEN** um drawer abre no lado direito exibindo todas as tags do usuário com contagem de entradas entre parênteses

#### Scenario: Selecionar uma tag
- **WHEN** o usuário toca em uma tag no drawer
- **THEN** a tag é marcada como selecionada, o drawer fecha, e a coluna central é filtrada para exibir apenas entradas com aquela tag

#### Scenario: Selecionar múltiplas tags (AND)
- **WHEN** o usuário abre o drawer, seleciona "#python" e em seguida "#ai"
- **THEN** ambas as tags ficam marcadas e a coluna central exibe apenas entradas que possuem "#python" E "#ai" simultaneamente

#### Scenario: Badge de tags ativas
- **WHEN** o usuário tem 2 tags selecionadas
- **THEN** o botão de tags no AppBar exibe o texto `[🏷️ 2] Tags`

#### Scenario: Limpar filtros de tag
- **WHEN** o usuário toca em "Limpar filtros" dentro do drawer
- **THEN** todas as tags são desselecionadas e a coluna central volta a exibir sem filtro de tags

#### Scenario: Nenhuma tag cadastrada
- **WHEN** o usuário não possui nenhuma tag
- **THEN** o botão de tags permanece visível sem badge, e o drawer exibe mensagem "Nenhuma tag"

#### Scenario: Drawer de tags em dispositivo móvel
- **WHEN** a largura da tela é menor que 600px
- **THEN** o drawer de tags abre como um `ModalBottomSheet` em vez de um painel lateral

### Requirement: Layout de 3 colunas
O sistema DEVE organizar o explore view em três zonas: árvore de categorias (esquerda, ~220px), conteúdo central (expand), e drawer de tags (direita, ~180px, ocultável). Em telas menores que 600px, a árvore de categorias colapsa em um menu expansível e o drawer de tags vira `ModalBottomSheet`.

#### Scenario: Layout em desktop
- **WHEN** a largura da tela é maior ou igual a 600px
- **THEN** as três colunas são exibidas lado a lado como `Row` com larguras fixas para as laterais e `expand` para a central

#### Scenario: Layout em mobile
- **WHEN** a largura da tela é menor que 600px
- **THEN** a árvore de categorias é substituída por um menu expansível no topo ou esquerda colapsável, e o drawer de tags abre como `ModalBottomSheet`
