## Context

Estado atual do código:
- Sprints 1-4 estão essencialmente completos: autenticação multi-usuário, OAuth, categorias hierárquicas, tags em entries, filtros por tag no `entry_list_view`
- `entry_list_view.py` lista entradas por feed com filtros de "não lidos", "importantes" e tag única
- `feed_list_view.py` agrupa feeds por categoria com seções
- `category_service.py` tem função `get_category_tree()` que retorna árvore hierárquica
- `tag_service.py` tem `get_distinct_tags()` (global) e `get_distinct_tags_for_feed()` (por feed)
- `entry_service.py` tem `list_entries()` com parâmetros `feed_url`, `user_id`, `unread_only`, `important_only`, `tag`
- Nav bar: [Início] [Feeds] [Categorias] [Sobre] — índice 0 = `/feeds`
- Não existe busca full-text, nem `search_vector` no banco, nem explore view
- Não existe listagem cross-feed de entries

Restrições:
- PostgreSQL 16 com SQLModel async e Alembic para migrations
- Flet para UI (wrapper Flutter em Python)
- Busca textual deve suportar conteúdo multilíngue (PT + EN)
- Layout deve adaptar-se a desktop e mobile

## Goals / Non-Goals

**Goals:**
- Criar explore view como nova home page (`/`) com drill-down por categorias
- Adicionar drawer lateral direito com filtro de tags multi-seleção AND
- Implementar busca full-text PostgreSQL com `tsvector`, GIN index, `plainto_tsquery`, `ts_rank`, `ts_headline`
- Barra de busca no AppBar que alterna a coluna central entre modo explore e modo busca
- Listagem cross-feed de entradas recentes (`list_recent()`)
- Contagem de tags por usuário (`get_distinct_tags_with_counts()`)
- Layout responsivo (3 colunas em desktop, adaptável em mobile)

**Non-Goals:**
- Paginação nos resultados da busca (MVP — limit 50)
- Stemming por idioma (usa `simple`, sem stemming)
- Sugestão/autocomplete na busca
- Busca em tempo real (só ao pressionar Enter ou após debounce)
- Gestão de tags no explore view (adicionar/remover tags continua sendo no `entry_view`)
- Substituir o `feed_list_view` existente (ele permanece em `/feeds`)
- Exportar/importar configuração do explore

## Decisions

### 1. Índice full-text: configuração `simple` (sem stemming, multilíngue)

**Decisão**: Usar `to_tsvector('simple', ...)` e `plainto_tsquery('simple', ...)` em vez de configurações com stemming (`'portuguese'`, `'english'`).

**Alternativa considerada**: Coluna dupla `search_vector_pt` + `search_vector_en` com OR na query. Rejeitada porque:
- Dobra o tamanho do índice GIN
- Não escala para outros idiomas (francês, alemão, etc.)
- Complexidade adicional na migration e no service

**Alternativa considerada**: `ILIKE '%term%'`. Rejeitada porque:
- Sem ranking de relevância
- Sem snippet com destaque
- Table scan inevitável (sem índice utilizável)
- Muito inferior ao tsvector

**Consequência**: Perda de stemming ("learning" não encontra "learn"). Aceitável para MVP. Se necessário no futuro, adicionar coluna `language` no modelo `Feed` e usar `CASE WHEN` na generated column.

### 2. Strip de HTML antes da indexação

**Decisão**: Usar `regexp_replace(content, '<[^>]+>', '', 'g')` na expressão da generated column para remover tags HTML antes da tokenização.

**Alternativa considerada**: Indexar HTML bruto. Rejeitada porque tags HTML poluem o índice com tokens como "div", "class", "span", "href", degradando a qualidade da busca.

**Consequência**: Entities HTML (`&amp;`, `&lt;`) não são decodificadas. Aceitável — são raras em conteúdo RSS moderno e não quebram a busca.

### 3. Layout do explore view: Row com 3 zonas

**Decisão**: Usar `ft.Row` com 3 filhos: árvore de categorias (`width=220`), conteúdo central (`expand=True`), drawer de tags (`width=180`, visibilidade condicional).

**Alternativa considerada**: Navegação drill-down em tela cheia (como mobile nav). Rejeitada porque:
- Não é uma "visualização alternativa" — é só mais navegação
- Perde a vantagem de ver categorias e conteúdo simultaneamente
- O plano descreve "navegação por categorias", não "substituir navegação"

**Adaptação mobile**: Em `page.width < 600`, a árvore vira um `ft.PopupMenuButton` expansível no AppBar e o drawer de tags vira `ft.ModalBottomSheet`.

### 4. Barra de busca: substitui coluna central (não a view inteira)

**Decisão**: Ao digitar na barra de busca, apenas a coluna central alterna de `entry_list` para `search_results`. A árvore de categorias e o drawer de tags permanecem visíveis.

**Alternativa considerada**: Navegar para `/search` (view dedicada). Rejeitada porque:
- Perde o contexto da árvore de categorias
- Quebra a experiência de "explore" contínuo
- O usuário quer drill-down + busca, não busca isolada

**Alternativa considerada**: Modal de busca que cobre a tela toda. Rejeitada porque impede drill-down simultâneo.

### 5. Filtro de tags: drawer direito com multi-seleção AND

**Decisão**: Tags selecionadas combinam-se com AND (entrada precisa ter todas as tags). Drawer fecha ao selecionar uma tag. Botão no AppBar com badge de contagem.

**Alternativa considerada**: OR (entrada precisa ter qualquer uma das tags). Rejeitada porque:
- AND é mais útil para refinar resultados ("quero #python E #ai")
- OR produz muitos resultados com baixa precisão

**Alternativa considerada**: Chips inline abaixo da barra de busca (como no `entry_list_view`). Rejeitada porque:
- Ocupa espaço vertical precioso na coluna central
- Com muitas tags, os chips empurram o conteúdo para baixo
- Um drawer lateral é mais organizado e permite ver a lista completa

### 6. Árvore de categorias: só categorias, sem feeds

**Decisão**: A árvore lateral mostra apenas categorias (hierárquicas). Tocar numa categoria filtra a coluna central (entradas dos feeds da categoria). Os feeds não aparecem como nós na árvore.

**Alternativa considerada**: Árvore com feeds como filhos das categorias. Rejeitada porque:
- O usuário pediu explicitamente "a árvore da esquerda não mostra feeds"
- Exibir feeds na árvore mistura dois níveis de abstração (categorias e fontes)
- O `feed_list_view` já serve para navegar por feeds

### 7. `list_recent()` cross-feed no `entry_service.py`

**Decisão**: Nova função no `entry_service.py` que aceita `user_id`, `category_id` (opcional), `tag` (opcional), `limit`. Usa JOIN com `Feed` para filtrar por `category_id`, JOIN com `EntryTag` para filtrar por tag múltipla.

**Alternativa considerada**: Fazer a filtragem no Python após carregar todas as entries. Rejeitada por performance — usuários podem ter milhares de entries.

### 8. Coluna `search_vector`: generated column gerenciada pelo PostgreSQL

**Decisão**: A coluna `search_vector` não é declarada no modelo Python (SQLModel). É criada via migration SQL com `GENERATED ALWAYS AS ... STORED`. O `search_service.py` usa `sqlalchemy.text()` para queries.

**Alternativa considerada**: Declarar `search_vector` como campo SQLModel com `sa_column=Column(TSVECTOR)`. Rejeitada porque SQLModel não suporta `GENERATED ALWAYS AS` e tentaria criar/gerenciar a coluna.

**Consequência**: O campo é invisível para o ORM. Inserções e atualizações no modelo `Entry` continuam funcionando normalmente porque o PostgreSQL gerencia a coluna automaticamente.

### 9. Índice auxiliar `(user_id, published DESC)`

**Decisão**: Adicionar índice composto para otimizar `list_recent()`, que filtra por `user_id` e ordena por `published DESC`.

**Alternativa considerada**: Usar apenas o índice existente da PK. Rejeitada porque consultas com `WHERE user_id = X ORDER BY published DESC LIMIT 50` fariam table scan.

## Risks / Trade-offs

- **[Write overhead GIN]**: Índice GIN em `search_vector` aumenta o custo de INSERT/UPDATE. Mitigação: entries são inseridas em lote durante refresh, não uma a uma. O overhead é amortizado.
- **[Espaço em disco]**: Coluna `search_vector` + índice GIN ocupam espaço adicional (~30% do texto indexado). Mitigação: aceitável para um leitor RSS pessoal. O Sprint 7 (limpeza) reduz entries antigas.
- **[Complexidade da migration]**: SQL bruto em Alembic é frágil (depende da sintaxe exata do PostgreSQL). Mitigação: testar a migration no banco `couscous_test` antes de aplicar em produção.
- **[Conteúdo HTML residual]**: O `regexp_replace` não cobre todos os casos (entities, CDATA, JavaScript inline). Mitigação: aceitável para MVP. No futuro, usar `BeautifulSoup` para strip robusto via trigger ou Python.
- **[Performance com muitos feeds]**: `list_recent()` com 100+ feeds pode ficar lenta. Mitigação: índice `(user_id, published DESC)` + LIMIT 50. Sem paginação, 50 resultados é suficiente para a tela inicial.
- **[Layout mobile vs desktop]**: A detecção de `page.width` pode ter edge cases (redimensionamento, orientação). Mitigação: usar `page.on_resize` para reavaliar o layout dinamicamente.

## Migration Plan

1. Criar migration Alembic (`make db-migrate-create name="add-search-vector"`)
2. Editar o arquivo gerado para adicionar SQL bruto:
   ```sql
   ALTER TABLE entries ADD COLUMN search_vector tsvector
     GENERATED ALWAYS AS (
       to_tsvector('simple',
         regexp_replace(
           coalesce(title, '') || ' ' ||
           coalesce(summary, '') || ' ' ||
           coalesce(content, ''),
           '<[^>]+>', '', 'g'
         )
       )
     ) STORED;
   CREATE INDEX idx_entries_search_vector ON entries USING GIN (search_vector);
   CREATE INDEX idx_entries_user_published ON entries (user_id, published DESC);
   ```
3. Aplicar migration: `make db-migrate-up`
4. Rollback: `make db-migrate-down` — o Alembic gerencia o downgrade automaticamente se a migration tiver `downgrade()` implementado

## Open Questions

- Nenhuma pendente — todas as decisões de design foram resolvidas durante a exploração
