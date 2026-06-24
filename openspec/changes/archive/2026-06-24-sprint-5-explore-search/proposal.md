## Why

O usuário atualmente navega pelas notícias de forma linear: seleciona um feed → vê as entradas daquele feed → lê um artigo. Para descobrir conteúdo entre feeds ou encontrar artigos por tema, precisa alternar entre feeds manualmente. Além disso, não há mecanismo de busca textual — encontrar um artigo específico entre todos os feeds é impossível.

Este sprint cria uma visualização alternativa (drill-down por categorias com visão cross-feed) e adiciona busca full-text via PostgreSQL, transformando a home page no centro de descoberta de conteúdo.

## What Changes

- Criar `app/views/explore_view.py` — navegação por categorias com drill-down (categoria → entradas de todos os feeds da categoria) e visão cross-feed de artigos recentes
- Criar drawer lateral de tags à direita com filtro multi-seleção (AND), acessível por botão no AppBar
- Adicionar coluna `search_vector tsvector` gerada automaticamente + índice GIN no modelo `Entry` (via migration SQL manual)
- Criar `app/services/search_service.py` — função de busca full-text com `ts_rank`, `ts_headline` e `tsquery` usando configuração `simple` (multilíngue)
- Adicionar barra de busca no AppBar do explore view — ao digitar, a coluna central alterna de lista de entradas para resultados da busca
- Alterar rota `/` de `feed_list_view` para `explore_view`, mantendo rotas existentes
- Adicionar `list_recent()` cross-feed no `entry_service.py` para alimentar o explore view
- Adicionar `get_distinct_tags_with_counts()` no `tag_service.py` para o drawer de tags

## Capabilities

### New Capabilities
- `explore-view`: Visualização alternativa com drill-down por categorias, listagem cross-feed de entradas recentes, e filtro lateral de tags com multi-seleção
- `full-text-search`: Busca textual via PostgreSQL (tsvector/tsquery) com ranking de relevância, snippets destacados, e substituição da coluna central no explore view

### Modified Capabilities
- `app-navigation`: Rota `/` (home) passa de `feed_list_view` para `explore_view`; nav bar índice 0 aponta para `/` (explore)

## Impact

- **Modelos**: Nova coluna fantasma `search_vector tsvector` no modelo `Entry` (gerenciada pelo PostgreSQL, não pelo SQLModel); novo índice GIN; novo índice em `(user_id, published)`
- **Serviços**: Novo `search_service.py`; `entry_service.py` ganha `list_recent()`; `tag_service.py` ganha `get_distinct_tags_with_counts()`
- **Views**: Novo `explore_view.py`; `app.py` altera rota `/`; `nav_bar.py` altera índice 0
- **Banco de dados**: Migration SQL para coluna `search_vector` e índices; strip de HTML antes da indexação
- **Dependências**: Nenhuma nova dependência externa (PostgreSQL nativo)
