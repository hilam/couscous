## ADDED Requirements

### Requirement: Tabela de rotas declarativa

O sistema SHALL definir uma tabela de rotas (`_ROUTE_TABLE`) que mapeia cada padrão de rota para uma tupla `(handler, requires_session)`. O handler `on_route_change` SHALL iterar sobre essa tabela para encontrar a view correspondente, em vez de usar uma cadeia longa de if/elif.

#### Scenario: Rota encontrada na tabela
- **WHEN** o usuário navega para uma rota registrada na tabela (ex: `/feeds`, `/feed/<url>`, `/categories`)
- **THEN** o sistema encontra o handler correspondente e renderiza a view apropriada

#### Scenario: Rota não encontrada na tabela (fallback)
- **WHEN** o usuário navega para uma rota desconhecida que não corresponde a nenhum padrão na tabela
- **THEN** o sistema renderiza a view padrão (`home_view`) como fallback

#### Scenario: Adição de nova rota
- **WHEN** um desenvolvedor precisa adicionar uma nova rota ao sistema
- **THEN** basta adicionar uma entrada na `_ROUTE_TABLE` com o padrão de rota, handler e flag de sessão, sem modificar a lógica do `on_route_change`

### Requirement: Factory de contexto centralizada

O sistema SHALL fornecer uma função `_build_context` que constrói o `PageContext` apropriado com ou sem sessão de banco de dados, dependendo da flag `requires_session` da rota. A criação de `AsyncSession` via `get_db_session()` SHALL ser feita exclusivamente dentro dessa factory.

#### Scenario: Rota que requer sessão de banco
- **WHEN** uma rota com `requires_session=True` é acessada
- **THEN** a factory cria um `PageContext` com `session` e `_session_factory` populados a partir de `get_db_session()`

#### Scenario: Rota que não requer sessão de banco
- **WHEN** uma rota com `requires_session=False` é acessada (ex: `/login`, `/about`)
- **THEN** a factory cria um `PageContext` sem `session` e sem `_session_factory`

### Requirement: Extração de parâmetros de rota

O sistema SHALL fornecer funções utilitárias para extrair parâmetros de rota (URL do feed, ID da entrada) de forma explícita, em vez de usar slicing inline de strings (ex: `route[len("/feed/"):]`). As rotas com parâmetros dinâmicos SHALL ser identificadas por padrões de prefixo na tabela de rotas.

#### Scenario: Extração de URL do feed
- **WHEN** o usuário navega para `/feed/https://example.com/rss`
- **THEN** o sistema extrai `https://example.com/rss` como `feed_url` e o atribui a `state.active_feed_url`

#### Scenario: Extração de ID da entrada
- **WHEN** o usuário navega para `/entry/42`
- **THEN** o sistema extrai `42` como inteiro e o passa para `entry_view`

### Requirement: Preservação de comportamento existente

O sistema SHALL preservar exatamente o mesmo comportamento de roteamento observável: mesmas rotas mapeadas para as mesmas views, mesmas condições de exibição da navbar, mesma inicialização (push para `/login`), mesma ordem de operações (clear → build context → call view → append → set navbar → update).

#### Scenario: Roteamento de autenticação
- **WHEN** o app inicia ou um usuário não autenticado acessa uma rota protegida
- **THEN** o sistema redireciona para `/login` e NÃO exibe a navbar

#### Scenario: Navegação entre telas
- **WHEN** um usuário autenticado navega entre `/feeds`, `/`, `/about`, `/categories` via navbar
- **THEN** cada rota renderiza a view correta com a navbar visível e o índice selecionado correto

#### Scenario: Rotas com parâmetros dinâmicos
- **WHEN** um usuário autenticado navega para `/feed/<url>` ou `/entry/<id>`
- **THEN** a view correspondente recebe os parâmetros corretos e renderiza o conteúdo apropriado
