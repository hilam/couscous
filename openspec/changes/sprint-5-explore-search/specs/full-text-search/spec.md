## ADDED Requirements

### Requirement: Busca full-text em entradas
O sistema DEVE permitir ao usuário buscar por texto em todas as suas entradas utilizando busca full-text do PostgreSQL com configuração `simple` (multilíngue, sem stemming), indexando `title`, `summary` e `content` com remoção de tags HTML.

#### Scenario: Busca com resultados
- **WHEN** o usuário digita "machine learning" na barra de busca do explore view e pressiona Enter
- **THEN** a coluna central exibe as entradas que contêm os termos, ordenadas por relevância (`ts_rank`), com os termos destacados no snippet (`ts_headline`), limitado a 50 resultados

#### Scenario: Busca sem resultados
- **WHEN** o usuário digita um termo que não existe em nenhuma entrada
- **THEN** a coluna central exibe mensagem "Nenhum resultado encontrado para '<termo>'"

#### Scenario: Busca vazia volta ao estado anterior
- **WHEN** o usuário limpa o campo de busca (query vazia)
- **THEN** a coluna central volta a exibir o estado anterior (Recentes ou drill-down por categoria), mantendo filtros de tag ativos

### Requirement: Coluna search_vector no modelo Entry
O sistema DEVE adicionar uma coluna `search_vector tsvector` gerada automaticamente na tabela `entries` que indexa `title`, `summary` e `content` com remoção de tags HTML, usando configuração `simple`. A coluna DEVE ter um índice GIN para busca eficiente.

#### Scenario: Indexação automática ao inserir entrada
- **WHEN** uma nova entrada é inserida na tabela `entries`
- **THEN** o PostgreSQL automaticamente popula a coluna `search_vector` com o tsvector dos campos textuais

#### Scenario: Busca ignora tags HTML
- **WHEN** uma entrada contém `<div class="foo">Hello world</div>` no campo `content`
- **THEN** o `search_vector` indexa apenas os tokens "hello" e "world", ignorando "div", "class" e "foo"

### Requirement: Índice para consulta de entradas recentes
O sistema DEVE adicionar um índice composto `(user_id, published DESC)` na tabela `entries` para otimizar a consulta de entradas recentes cross-feed usada pelo explore view.

#### Scenario: Consulta de recentes com índice
- **WHEN** o explore view consulta `list_recent()` para um usuário
- **THEN** a consulta utiliza o índice `(user_id, published DESC)` em vez de table scan

### Requirement: Barra de busca no AppBar do explore
O sistema DEVE exibir uma barra de busca textual no AppBar do explore view. Ao digitar, a coluna central alterna do modo "explore" (lista de entradas) para o modo "busca" (resultados da busca). A árvore de categorias e o drawer de tags permanecem visíveis e seus filtros combinam-se com a busca.

#### Scenario: Busca combinada com filtro de categoria
- **WHEN** o usuário seleciona a categoria "Tecnologia" e depois busca por "python"
- **THEN** a coluna central exibe apenas entradas que pertencem a feeds da categoria "Tecnologia" E contêm "python"

#### Scenario: Busca combinada com filtro de tag
- **WHEN** o usuário seleciona a tag "#ai" e depois busca por "gpt"
- **THEN** a coluna central exibe apenas entradas que possuem a tag "#ai" E contêm "gpt"

#### Scenario: Limpar busca preserva filtros
- **WHEN** o usuário limpa o campo de busca após ter filtros de categoria e tag ativos
- **THEN** a coluna central volta a exibir as entradas filtrando por categoria e tag, sem o filtro de busca

### Requirement: Snippets com destaque nos resultados
O sistema DEVE exibir snippets (`ts_headline`) com os termos da busca destacados visualmente nos resultados da busca, usando até 40 palavras com mínimo de 20 palavras.

#### Scenario: Resultado com snippet destacado
- **WHEN** a busca por "python" encontra uma entrada cujo conteúdo contém "python"
- **THEN** o card de resultado exibe um snippet onde a palavra "python" aparece destacada (ex: em negrito ou com fundo colorido)

### Requirement: Serviço de busca via ts_rank
O sistema DEVE implementar `search_service.py` com função `search_entries(session, query, user_id, category_id, tag, limit)` que utiliza `plainto_tsquery` e `ts_rank` para ordenar resultados por relevância. A função DEVE aceitar filtros opcionais de categoria e tag combináveis com a busca.

#### Scenario: Busca por múltiplos termos
- **WHEN** o usuário busca por "machine learning python"
- **THEN** o sistema converte para `plainto_tsquery('simple', 'machine learning python')` e retorna entradas ordenadas por relevância

#### Scenario: Busca por termo em português
- **WHEN** o usuário busca por "aprendizado de máquina"
- **THEN** o sistema encontra entradas que contêm as palavras "aprendizado", "de" e "máquina" (tokenização `simple`)
