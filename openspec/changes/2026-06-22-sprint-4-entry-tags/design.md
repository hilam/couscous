## Context

O modelo `FeedTag` existe em `database/models/couscous.py` como dead code — não possui `user_id` FK, não tem service associado e não é referenciado em nenhuma view. O Sprint 4 do plano de desenvolvimento propõe substituí-lo por `EntryTag` com escopo de usuário e integrar completamente à interface do leitor.

Estado atual:
- `Entry` já tem `user_id` FK (Sprint 1)
- `Feed` já tem `user_id` FK (Sprint 1)
- `entry_list_view.py` já tem filtros "não lidos" e "importantes" com chips
- `entry_view.py` já tem toggle de estrela
- `ArticleCard` exibe título, autor, data e resumo

## Goals / Non-Goals

**Goals:**
- Substituir `FeedTag` (dead code) por `EntryTag` com `entry_id` FK, `tag` string, `user_id` FK
- Criar `tag_service.py` com operações: listar tags distintas do usuário, atribuir/remover tag de entry, listar entries por tag
- Exibir tags como chips no `ArticleCard`
- Interface de gerenciamento de tags na `entry_view.py` (adicionar/remover inline)
- Filtro por tag na `entry_list_view.py` combinável com filtros existentes

**Non-Goals:**
- Renomear tags (fora do escopo — tags são strings imutáveis; para "renomear", remove-se a antiga e adiciona-se a nova)
- Cores customizadas por tag
- Hierarquia de tags
- Sugestão automática de tags (autocomplete)
- Exportação/importação de tags

## Decisions

### 1. Modelo `EntryTag` sem tabela `Tag` separada

**Decisão**: Usar um único modelo `EntryTag` com chave composta `(entry_id, tag)` e campo `user_id` FK. Sem tabela `Tag` dedicada.

**Alternativa considerada**: Tabela `Tag` (id, name, user_id) + tabela `EntryTag` (entry_id FK, tag_id FK). Rejeitada porque:
- Adiciona complexidade desnecessária para o escopo atual (sem renomeação, sem metadados de tag)
- O PLANO especifica explicitamente `tag` como `str` no modelo `EntryTag`
- Tags são efêmeras — se todas as entries perdem uma tag, ela "deixa de existir" naturalmente

**Consequência**: "Criar tag" equivale a atribuir uma string nova a uma entry. "Excluir tag" equivale a remover todas as associações com aquela string para o usuário. Não há operação de "renomear".

### 2. Chave primária composta vs. id autoincrement

**Decisão**: Chave primária composta `(entry_id, tag)`, igual ao padrão do `FeedTag` existente.

**Alternativa considerada**: Coluna `id` autoincrement como PK + unique constraint em `(entry_id, tag)`. Rejeitada porque a chave composta expressa melhor a semântica do domínio (uma entry não pode ter a mesma tag duas vezes) e evita coluna extra.

### 3. Filtro por tag via service layer

**Decisão**: Adicionar parâmetro `tag: str | None` à função `list_entries` em `entry_service.py`. O filtro usa JOIN com `EntryTag` e cláusula WHERE.

**Alternativa considerada**: Filtro no frontend (carregar todas as entries e filtrar no Python). Rejeitada porque:
- Ineficiente com muitos artigos
- Inconsistente com os filtros existentes (unread_only, important_only) que já operam no banco

### 4. Tag chips: componente reutilizável

**Decisão**: Criar `app/controls/tag_chip.py` com dois modos:
- `TagChip` (exibição): chip colorido com nome da tag, usado no `ArticleCard`
- `TagChip` com `on_delete`: chip com botão X, usado na `entry_view.py`

Usa `ft.Chip` ou `ft.Container` estilizado como chip pequeno.

**Alternativa considerada**: `ft.FilterChip`. Rejeitado porque o comportamento de toggle do FilterChip não é adequado para exibição passiva nos cards.

### 5. Interface de adicionar tag na entry_view

**Decisão**: Usar um `ft.PopupMenuButton` ou `ft.AlertDialog` com lista de tags existentes + campo de texto para criar nova tag. Ao selecionar uma tag existente ou digitar nova, atribui à entry.

**Alternativa considerada**: Campo de texto com autocomplete via `ft.AutofillGroup`. Rejeitado por complexidade e baixa disponibilidade no Flet web. A lista de tags do usuário é pequena o suficiente para um dropdown/dialog simples.

## Risks / Trade-offs

- **[Tags órfãs]**: Se uma entry é deletada, as EntryTag correspondentes devem ser removidas. Mitigação: configurar `ondelete="CASCADE"` na FK `entry_id` ou remover manualmente no service de remoção de feed/entry.
- **[Escalabilidade]**: Com muitas tags por entry, os chips podem ocupar muito espaço no card. Mitigação: limitar exibição a N chips (ex: 3) com "+X mais" no ArticleCard.
- **[Consistência com FeedTag]**: O modelo `FeedTag` existente será removido. Se algum código futuro referenciava `FeedTag`, quebrará. Mitigação: verificar com grep que não há referências além do modelo e removê-lo.

## Migration Plan

1. Remover classe `FeedTag` do modelo (não há dados para migrar — é dead code)
2. Adicionar classe `EntryTag` ao modelo
3. `init_async_db()` recria as tabelas automaticamente (já é o comportamento atual)
4. Nenhum script de migração necessário — sem dados de produção a preservar
