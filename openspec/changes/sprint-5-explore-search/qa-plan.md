## Capability: explore-view

### Test: Estado inicial exibe entradas recentes
**Traces**: `specs/explore-view/spec.md` → Requirement: Exibir entradas recentes cross-feed
- **GIVEN** um usuário autenticado com 3 feeds, cada um com entradas publicadas em datas diferentes
- **WHEN** o usuário acessa a home page (`/`) sem nenhuma categoria selecionada
- **THEN** a coluna central exibe as entradas ordenadas por `published` decrescente, limitadas a 50

### Test: Estado inicial sem entradas
**Traces**: `specs/explore-view/spec.md` → Requirement: Exibir entradas recentes cross-feed
- **GIVEN** um usuário autenticado sem nenhuma entrada em nenhum feed
- **WHEN** o usuário acessa a home page
- **THEN** a coluna central exibe mensagem "Nenhum artigo encontrado"

### Test: Selecionar categoria filtra entradas
**Traces**: `specs/explore-view/spec.md` → Requirement: Drill-down por categoria
- **GIVEN** um usuário com categoria "Tech" que contém 2 feeds, e categoria "News" com 1 feed
- **WHEN** o usuário toca em "Tech" na árvore lateral
- **THEN** a coluna central exibe apenas entradas dos feeds da categoria "Tech"

### Test: Selecionar categoria sem feeds
**Traces**: `specs/explore-view/spec.md` → Requirement: Drill-down por categoria
- **GIVEN** um usuário com categoria "Vazia" que não possui feeds associados
- **WHEN** o usuário toca em "Vazia" na árvore lateral
- **THEN** a coluna central exibe mensagem "Nenhum artigo nesta categoria"

### Test: Voltar para Recentes
**Traces**: `specs/explore-view/spec.md` → Requirement: Drill-down por categoria
- **GIVEN** o usuário está visualizando entradas filtradas por uma categoria
- **WHEN** o usuário toca em "Recentes" no topo da coluna central
- **THEN** a coluna central volta a exibir entradas recentes de todos os feeds

### Test: Árvore exibe categorias hierárquicas
**Traces**: `specs/explore-view/spec.md` → Requirement: Árvore de categorias lateral
- **GIVEN** um usuário com categoria raiz "Tech" e categoria filha "Python"
- **WHEN** o explore view é renderizado
- **THEN** a coluna esquerda exibe "Tech" com "Python" indentado abaixo

### Test: Árvore sem categorias
**Traces**: `specs/explore-view/spec.md` → Requirement: Árvore de categorias lateral
- **GIVEN** um usuário sem nenhuma categoria
- **WHEN** o explore view é renderizado
- **THEN** a coluna esquerda exibe mensagem "Nenhuma categoria"

### Test: Abrir drawer de tags
**Traces**: `specs/explore-view/spec.md` → Requirement: Filtro lateral de tags (drawer direito)
- **GIVEN** um usuário com tags "#python" (12 entradas), "#rust" (8), "#ai" (5)
- **WHEN** o usuário toca no botão de tags no AppBar
- **THEN** um drawer abre no lado direito exibindo as tags com contagens

### Test: Selecionar tag fecha drawer e filtra
**Traces**: `specs/explore-view/spec.md` → Requirement: Filtro lateral de tags (drawer direito)
- **GIVEN** o drawer de tags está aberto
- **WHEN** o usuário toca em "#python"
- **THEN** o drawer fecha, "#python" fica selecionada, e a coluna central exibe apenas entradas com a tag "#python"

### Test: Multi-seleção AND
**Traces**: `specs/explore-view/spec.md` → Requirement: Filtro lateral de tags (drawer direito)
- **GIVEN** entradas: entrada A tem "#python" e "#ai", entrada B tem só "#python", entrada C tem só "#ai"
- **WHEN** o usuário seleciona "#python" e depois "#ai"
- **THEN** a coluna central exibe apenas a entrada A (que possui ambas as tags)

### Test: Badge de tags ativas
**Traces**: `specs/explore-view/spec.md` → Requirement: Filtro lateral de tags (drawer direito)
- **GIVEN** o usuário selecionou 2 tags
- **WHEN** o explore view é renderizado
- **THEN** o botão de tags no AppBar exibe `[🏷️ 2] Tags`

### Test: Limpar filtros de tag
**Traces**: `specs/explore-view/spec.md` → Requirement: Filtro lateral de tags (drawer direito)
- **GIVEN** o usuário tem 2 tags selecionadas e a coluna central está filtrada
- **WHEN** o usuário abre o drawer e toca em "Limpar filtros"
- **THEN** todas as tags são desselecionadas e a coluna central volta a mostrar sem filtro de tags

### Test: Nenhuma tag cadastrada
**Traces**: `specs/explore-view/spec.md` → Requirement: Filtro lateral de tags (drawer direito)
- **GIVEN** um usuário sem nenhuma tag
- **WHEN** o explore view é renderizado
- **THEN** o botão de tags no AppBar está visível sem badge, e o drawer exibe "Nenhuma tag"

### Test: EDGE - Drawer em mobile (< 600px)
**Traces**: `specs/explore-view/spec.md` → Requirement: Layout de 3 colunas
- **GIVEN** a largura da tela é 400px
- **WHEN** o usuário toca no botão de tags
- **THEN** o drawer abre como `ModalBottomSheet` em vez de painel lateral

### Test: Layout desktop com 3 colunas
**Traces**: `specs/explore-view/spec.md` → Requirement: Layout de 3 colunas
- **GIVEN** a largura da tela é 800px
- **WHEN** o explore view é renderizado
- **THEN** três colunas são exibidas lado a lado: árvore (~220px), central (expand), drawer (~180px)

## Capability: full-text-search

### Test: CRITICAL - Busca retorna resultados com ranking
**Traces**: `specs/full-text-search/spec.md` → Requirement: Busca full-text em entradas
- **GIVEN** entradas com conteúdo "Machine learning is fascinating" e "Learning Python basics"
- **WHEN** o usuário busca por "machine learning"
- **THEN** a primeira entrada (contém ambos os termos) aparece antes da segunda (contém só "learning"), com snippet destacando os termos

### Test: Busca sem resultados
**Traces**: `specs/full-text-search/spec.md` → Requirement: Busca full-text em entradas
- **GIVEN** nenhuma entrada contém "xyzabc123"
- **WHEN** o usuário busca por "xyzabc123"
- **THEN** a coluna central exibe "Nenhum resultado encontrado para 'xyzabc123'"

### Test: Limpar busca restaura estado anterior
**Traces**: `specs/full-text-search/spec.md` → Requirement: Busca full-text em entradas
- **GIVEN** o usuário está na categoria "Tech" e busca por "python"
- **WHEN** o usuário limpa o campo de busca
- **THEN** a coluna central volta a exibir entradas da categoria "Tech" (sem filtro de busca)

### Test: Indexação ignora tags HTML
**Traces**: `specs/full-text-search/spec.md` → Requirement: Coluna search_vector no modelo Entry
- **GIVEN** uma entrada com `content = "<div class='foo'>Hello world</div>"`
- **WHEN** a entrada é inserida no banco
- **THEN** o `search_vector` contém tokens "hello" e "world", mas NÃO contém "div", "class" ou "foo"

### Test: Busca combinada com categoria
**Traces**: `specs/full-text-search/spec.md` → Requirement: Barra de busca no AppBar do explore
- **GIVEN** categoria "Tech" tem entrada com "Python tutorial", categoria "News" tem entrada com "Python release"
- **WHEN** usuário seleciona categoria "Tech" e busca por "python"
- **THEN** apenas "Python tutorial" aparece nos resultados

### Test: Busca combinada com tag
**Traces**: `specs/full-text-search/spec.md` → Requirement: Barra de busca no AppBar do explore
- **GIVEN** entrada A tem tag "#ai" e conteúdo "gpt model", entrada B não tem tag "#ai" e conteúdo "gpt tutorial"
- **WHEN** usuário seleciona tag "#ai" e busca por "gpt"
- **THEN** apenas entrada A aparece

### Test: Snippet com destaque
**Traces**: `specs/full-text-search/spec.md` → Requirement: Snippets com destaque nos resultados
- **GIVEN** uma entrada com conteúdo "This is a long article about Python programming..."
- **WHEN** o usuário busca por "python"
- **THEN** o snippet exibido contém a palavra "Python" com destaque visual (negrito ou fundo)

### Test: Índice user_published otimiza recentes
**Traces**: `specs/full-text-search/spec.md` → Requirement: Índice para consulta de entradas recentes
- **GIVEN** um usuário com 1000 entradas espalhadas em 50 feeds
- **WHEN** `list_recent()` é chamada
- **THEN** a consulta utiliza o índice `(user_id, published DESC)` (verificável via `EXPLAIN ANALYZE`)

### Test: EDGE - Busca por termo em português
**Traces**: `specs/full-text-search/spec.md` → Requirement: Busca full-text em entradas
- **GIVEN** uma entrada com conteúdo "Aprendizado de máquina é fascinante"
- **WHEN** o usuário busca por "aprendizado de máquina"
- **THEN** a entrada é retornada nos resultados (tokenização `simple`)

### Test: EDGE - Busca com termos muito curtos
**Traces**: `specs/full-text-search/spec.md` → Requirement: Serviço de busca via ts_rank
- **GIVEN** entradas variadas
- **WHEN** o usuário busca por "a"
- **THEN** o sistema retorna resultados (não quebra) — comportamento depende do `plainto_tsquery`

### Test: EDGE - Busca com caracteres especiais
**Traces**: `specs/full-text-search/spec.md` → Requirement: Serviço de busca via ts_rank
- **GIVEN** uma entrada com conteúdo "C++ is powerful"
- **WHEN** o usuário busca por "C++"
- **THEN** o sistema não quebra (plainto_tsquery sanitiza a entrada)

## Capability: app-navigation

### Test: Login redireciona para explore
**Traces**: `specs/app-navigation/spec.md` → Requirement: Navigate via bottom navigation bar
- **GIVEN** um usuário não autenticado
- **WHEN** o usuário faz login com sucesso
- **THEN** `page.push_route("/")` é chamado e o explore view é exibido

### Test: Nav bar índice 0 vai para explore
**Traces**: `specs/app-navigation/spec.md` → Requirement: Navigate via bottom navigation bar
- **GIVEN** o usuário está em qualquer tela com nav bar visível
- **WHEN** o usuário toca no destino "Início" (índice 0) da NavigationBar
- **THEN** `page.push_route("/")` é chamado e o explore view é exibido

### Test: Nav bar índice 1 vai para feeds
**Traces**: `specs/app-navigation/spec.md` → Requirement: Navigate via bottom navigation bar
- **GIVEN** o usuário está no explore view
- **WHEN** o usuário toca no destino "Feeds" (índice 1) da NavigationBar
- **THEN** `page.push_route("/feeds")` é chamado e o feed list view é exibido

## Edge Cases

- **Múltiplas tags + categoria**: Quando tags AND e categoria estão selecionadas simultaneamente, a query de filtro combina ambas as condições
- **Busca + tags + categoria**: Os três filtros (busca, tags, categoria) combinam-se com AND — a entrada precisa satisfazer todos
- **Tag selecionada que não existe mais**: Se uma tag foi deletada enquanto estava selecionada no drawer, o sistema ignora e remove do estado local
- **Categoria deletada enquanto selecionada**: Se a categoria atual é deletada (ex: via `/categories`), o explore view volta para "Recentes" na próxima renderização
- **Conteúdo HTML com scripts inline**: `<script>alert('xss')</script>` — o `regexp_replace` remove as tags mas o texto interno ("alert('xss')") é indexado. Inofensivo para busca, mas pode poluir o índice com tokens de código
- **Muitas tags no drawer**: Com 100+ tags, o drawer usa scroll. Performance aceitável (é só uma lista de strings com contagem)

## Integration Points

- **Explore view ↔ Entry view**: Tocar numa entrada no explore view navega para `/entry/{id}` (comportamento existente, sem alteração)
- **Explore view ↔ Category management**: Criar/renomear/deletar categorias em `/categories` deve refletir na árvore do explore view na próxima renderização
- **Explore view ↔ Tag management**: Tags adicionadas/removidas em `/entry/{id}` devem refletir nas contagens do drawer na próxima renderização
- **Search service ↔ Entry service**: `search_entries()` e `list_recent()` compartilham o padrão de filtro por `user_id` + categoria + tag
- **Migration ↔ init_async_db()**: A coluna `search_vector` é criada via migration. Se `init_async_db()` usar `create_all`, a coluna NÃO será criada (SQLModel não a conhece). A migration é obrigatória.

## Review Notes

- **AMBIGUOUS**: `specs/explore-view/spec.md` → Scenario: Layout em mobile — "menu expansível no topo ou esquerda colapsável" é vago. Sugiro especificar: em mobile, a árvore vira um `ft.PopupMenuButton` com ícone de menu no AppBar, que exibe as categorias como itens de menu.
