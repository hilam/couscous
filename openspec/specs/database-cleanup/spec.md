## ADDED Requirements

### Requirement: Usuário pode limpar entries antigas manualmente

O sistema DEVE permitir que o usuário remova entries antigas através de um diálogo acessível por um botão na `settings_view`. Entries marcadas como importantes (`important=1`) NÃO DEVEM ser removidas. As `EntryTag` associadas às entries removidas DEVEM ser removidas em cascata.

#### Scenario: Acesso ao diálogo de limpeza

- **WHEN** o usuário está na tela de configurações e clica no botão "Limpar artigos antigos"
- **THEN** o diálogo de limpeza é aberto

#### Scenario: Limpeza manual com período de 30 dias

- **WHEN** o usuário abre o diálogo de limpeza, seleciona "30 dias" e confirma
- **THEN** o sistema remove todas as entries do usuário com `first_updated_epoch` anterior a 30 dias atrás e `important=0`
- **AND** as `EntryTag` associadas às entries removidas são excluídas em cascata
- **AND** entries com `important=1` são preservadas independentemente da idade

#### Scenario: Nenhuma entry para remover

- **WHEN** o usuário seleciona um período e não há entries que atendam aos critérios
- **THEN** o sistema informa "Nenhum artigo para remover" e não executa remoção

### Requirement: Diálogo de limpeza mostra contagem antes da confirmação

O diálogo de limpeza DEVE exibir o número total de entries que serão removidas antes que o usuário confirme a ação.

#### Scenario: Exibir contagem ao selecionar período

- **WHEN** o usuário seleciona um período (7, 30, 90 ou 365 dias) no dropdown do diálogo
- **THEN** o sistema consulta e exibe "X artigos serão removidos"
- **AND** o contador considera apenas entries com `important=0`

#### Scenario: Contagem zero

- **WHEN** não há entries que atendam ao período selecionado
- **THEN** o diálogo exibe "Nenhum artigo para remover" e desabilita o botão de confirmação

### Requirement: Opções de período predefinidas

O diálogo de limpeza DEVE oferecer exatamente as opções: 7, 30, 90 e 365 dias.

#### Scenario: Dropdown com opções de período

- **WHEN** o diálogo de limpeza é aberto
- **THEN** o dropdown exibe as opções "7 dias", "30 dias", "90 dias" e "365 dias"

### Requirement: Limpeza em background com atualização da view

A limpeza DEVE ser executada de forma assíncrona (background) e a view corrente DEVE ser atualizada ao concluir. Se a rota atual for `/entry/{id}` e a entry foi removida, o sistema DEVE redirecionar para `/feeds`.

#### Scenario: Limpeza concluída enquanto usuário está na lista de feeds

- **WHEN** a limpeza em background é concluída e o usuário está em `/feeds` ou `/feed/{url}`
- **THEN** a lista de entries é recarregada para refletir as remoções

#### Scenario: Limpeza concluída enquanto usuário visualiza entry removida

- **WHEN** a limpeza em background é concluída e o usuário está em `/entry/{id}` de uma entry que foi removida
- **THEN** o sistema redireciona para `/feeds`

### Requirement: Configuração de limpeza automática por usuário

O usuário DEVE poder configurar uma política de retenção automática na tela de configurações. Quando configurada, a limpeza automática DEVE ser executada na inicialização do app, em background.

#### Scenario: Configurar retenção automática nas configurações

- **WHEN** o usuário acessa a tela de configurações e seleciona "30 dias" no dropdown "Limpeza automática"
- **THEN** a preferência é salva no banco como `auto_cleanup_days=30`
- **AND** a limpeza será executada automaticamente na inicialização do app

#### Scenario: Desligar limpeza automática

- **WHEN** o usuário seleciona "Desligado" no dropdown de limpeza automática
- **THEN** `auto_cleanup_days` é salvo como `None`
- **AND** nenhuma limpeza automática será executada

#### Scenario: Limpeza automática na inicialização

- **WHEN** o usuário faz login e `auto_cleanup_days` está definido (ex: 30)
- **THEN** o sistema executa a limpeza em background durante a inicialização
- **AND** ao concluir, exibe snackbar "🧹 Limpeza automática: N artigos antigos removidos" se N > 0
- **AND** não exibe snackbar se nenhum artigo foi removido

### Requirement: Remoção do modelo FeedMetadata

O modelo `FeedMetadata` e sua tabela correspondente DEVEM ser removidos do código e do banco de dados, pois não são utilizados em nenhum lugar do sistema.

#### Scenario: Migration remove tabela feed_metadata

- **WHEN** a migration é aplicada
- **THEN** a tabela `feed_metadata` é removida do banco de dados
- **AND** a classe `FeedMetadata` é removida de `database/models/couscous.py`

### Requirement: Escopo multi-usuário na limpeza

A limpeza DEVE operar apenas sobre entries do usuário autenticado, nunca afetando entries de outros usuários.

#### Scenario: Limpeza isolada por usuário

- **WHEN** o usuário A executa limpeza com período de 30 dias
- **THEN** apenas entries com `user_id` do usuário A são removidas
- **AND** entries de outros usuários não são afetadas
