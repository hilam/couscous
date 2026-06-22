## Why

O usuário precisa organizar notícias com etiquetas (tags) para categorizar e encontrar rapidamente artigos por temas transversais (ex: "python", "IA", "tutorial"). Atualmente o modelo `FeedTag` existe mas é dead code (não tem FK de usuário, não tem service, não é usado em views). Precisamos substituí-lo por `EntryTag` com escopo de usuário e integrar completamente à interface.

## What Changes

- Criar modelo `EntryTag` (entry_id FK, tag str, user_id FK) em substituição ao `FeedTag` (dead code)
- Criar `app/services/tag_service.py` com CRUD de tags + assign/remove em entries
- Adicionar interface de etiquetas no `entry_view.py` — adicionar/remover tags inline durante leitura do artigo
- Criar componente `app/controls/tag_chip.py` para exibição de tags nos cards e na tela de detalhe
- Exibir tags nos `ArticleCard` da lista de entries
- Adicionar filtro por tag na `entry_list_view.py`

## Capabilities

### New Capabilities
- `entry-tags`: Gerenciamento de etiquetas em notícias — criar tags, atribuir/remover tags de entries, visualizar tags nos cards e na tela de detalhe

### Modified Capabilities
- `entry-filters`: Adicionar filtro por tag na lista de entries, permitindo ao usuário filtrar artigos que possuem uma tag específica

## Impact

- **Modelos**: Novo modelo `EntryTag`; remoção do modelo `FeedTag` (dead code, sem uso em produção)
- **Serviços**: Novo `tag_service.py`; `entry_service.py` pode precisar de consulta auxiliar para tags
- **Views**: `entry_view.py` ganha seção de tags; `entry_list_view.py` ganha filtro por tag
- **Controles**: Novo `tag_chip.py`; `article_card.py` exibe tags
- **Banco de dados**: Nova tabela `entry_tags`; remoção da tabela `feed_tags`
- **Dependências**: Nenhuma nova dependência externa
