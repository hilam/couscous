## Context

A `explore_view` (rota `/`) exibe a árvore de categorias no painel esquerdo (desktop 220px). Atualmente a árvore é renderizada plana — todos os nós visíveis, indentados por nível. Não há expand/colapsar, nem indicação de conteúdo. O clique em qualquer nó dispara `refresh_entries()` consultando `list_recent(category_id=X)`, que filtra apenas feeds com `category_id` exato (sem subcategorias).

A `category_list_view` (rota `/categories`) também renderiza árvore plana com botões edit/delete — esta view não é afetada por esta mudança, exceto pela alteração na estrutura de retorno de `get_category_tree`, que agora inclui campos de contagem.

## Goals / Non-Goals

**Goals:**
- Árvore interativa com expand/colapsar na `explore_view`
- Badge de artigos não lidos por categoria (contagem recursiva)
- Clique contextual: toggle (se filhos) + seleção (se feeds recursivos)
- `list_recent` com modo `include_subcategories`
- Mobile mantido simples (PopupMenuButton com badges)

**Non-Goals:**
- Alterar a `category_list_view` (continua plana com edit/delete)
- Expand/colapsar interativo no mobile
- Persistir estado de expansão entre sessões
- Animação de expand/colapsar (mantém toggle instantâneo)
- Contagem de "todos os artigos" (lidos + não lidos) — apenas não lidos

## Decisions

### Decisão 1: Controle manual de visibilidade (não ExpansionTile)

**Escolha**: Gerenciar `expanded_ids: set[int]` no closure da view e renderizar filhos condicionalmente no `ListView`.

**Alternativa considerada**: `ft.ExpansionTile` nativo do Flet.

**Razão**: Precisamos de controle fino sobre o comportamento do clique — o mesmo toque no tile dispara toggle E seleção quando aplicável. `ExpansionTile` separa o toque no header (toggle) do conteúdo interno, dificultando o clique contextual unificado. Além disso, queremos badge inline no título, o que exigiria customização do `ExpansionTile` via `trailing`.

### Decisão 2: Contagens agregadas em Python, não no SQL

**Escolha**: Fazer queries simples (`COUNT GROUP BY category_id` via SQLModel) para feeds e não lidos, depois agregar os totais recursivos subindo a árvore em memória (Python).

**Alternativa considerada**: CTE recursiva no PostgreSQL para calcular totais diretamente no banco.

**Razão**: A árvore de categorias de um usuário é pequena (dezenas de nós, não milhares). O overhead de trafegar os counts brutos e agregar em Python é insignificante. CTE recursiva adicionaria complexidade ao SQL que o SQLModel não abstrai bem, além de dificultar testes.

### Decisão 3: Coleta de IDs descendentes via árvore em memória

**Escolha**: Função `_collect_descendant_ids(tree: list[dict], category_id: int) -> list[int]` que percorre a árvore já carregada para coletar IDs.

**Alternativa considerada**: Query recursiva no banco para coletar IDs.

**Razão**: A árvore já está carregada em memória (chamada a `get_category_tree` no início da view). Percorrê-la é O(n) trivial. Evita segunda query.

### Decisão 4: Badge no `trailing` do `ListTile`

**Escolha**: Usar `ft.Container` com `ft.Text` estilizado como badge posicionado no `trailing` do `ListTile`.

**Alternativa considerada**: `ft.Chip` ou `ft.Badge`.

**Razão**: `ListTile.trailing` aceita qualquer control e posiciona naturalmente à direita. Um `Container` circular com `Text` dá o visual desejado sem dependências extras.

### Decisão 5: Estrutura do nó da árvore estendida

**Escolha**: Adicionar campos `feed_count`, `total_feed_count` e `unread_count` ao dicionário retornado por `get_category_tree()`, calculados via duas queries agregadas + roll-up em memória.

```
Novo formato do nó:
{
    "id": int,
    "name": str,
    "parent_id": int | None,
    "children": [...],
    "feed_count": int,        # feeds com category_id == este nó
    "total_feed_count": int,  # feed_count + soma dos filhos
    "unread_count": int,      # não lidos recursivo
}
```

**Alternativa considerada**: Endpoint separado para counts, ou calcular counts na view.

**Razão**: Manter o serviço como fonte única da verdade. A view só consome. Evita lógica de negócio espalhada.

## Risks / Trade-offs

- **[Risco] Badges desatualizados após marcar leitura**: Quando o usuário navega para `/entry/<id>` e marca como lido, ao voltar com "voltar" do navegador a `explore_view` não é reconstruída (Flet mantém a view no stack). Os badges ficarão desatualizados até um refresh manual ou re-navegação.
  - **Mitigação**: O botão de refresh já existente na AppBar resolve isso. Podemos considerar um `page.on_view_pop` future para forçar refresh ao retornar, mas isso é Non-Goal para esta mudança.

- **[Risco] Performance com muitas categorias**: Se um usuário tiver centenas de categorias, a renderização inicial pode ser lenta.
  - **Mitigação**: Cenário improvável para um leitor RSS pessoal. A árvore é renderizada sob demanda (filhos só existem no DOM Flet quando expandidos).

- **[Trade-off] Clique contextual pode surpreender**: Um clique que faz duas coisas (toggle + carregar notícias) pode não ser óbvio para novos usuários.
  - **Mitigação**: Comportamento natural de tree views — é o mesmo padrão de exploradores de arquivo onde clicar na pasta mostra seu conteúdo E expande. O badge de contagem serve como affordance visual.
