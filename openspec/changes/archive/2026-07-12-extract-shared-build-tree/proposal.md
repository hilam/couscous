## Why

A função `_build_tree` — que monta uma árvore aninhada de categorias a partir de dados planos — está duplicada em dois arquivos (`feed_browser.py` e `category_list_view.py`) com ~35 linhas idênticas cada. Qualquer mudança na estrutura da árvore (ex: adicionar `has_unread` ou `icon`) exige tocar dois arquivos, e a probabilidade de divergência silenciosa cresce com o tempo. Extrair para um local compartilhado elimina a duplicação sem adicionar complexidade.

## What Changes

- Adicionar função pública `build_category_tree()` em `app/services/category_service.py`
- Substituir a `_build_tree` local em `app/services/feed_browser.py` por um import da nova função
- Substituir a `_build_tree` local em `app/views/category_list_view.py` por um import da nova função
- Remover ambas as funções `_build_tree` locais
- Nenhuma mudança na lógica interna da árvore — apenas movida, não refatorada
- Nenhuma mudança de comportamento visível ao usuário

## Capabilities

### New Capabilities

_Nenhuma._ Trata-se de refatoração interna (tech-debt) sem nova capacidade visível no spec-level.

### Modified Capabilities

_Nenhuma._ Nenhuma especificação existente tem requirements alterados — a mudança é puramente de implementação.

## Impact

- `app/services/category_service.py` — ganha nova função pública `build_category_tree()`
- `app/services/feed_browser.py` — perde `_build_tree` local, importa `build_category_tree` de category_service
- `app/views/category_list_view.py` — perde `_build_tree` local, importa `build_category_tree` de category_service
- Nenhum outro arquivo é afetado
- Nenhuma dependência nova é adicionada
- Nenhuma API ou interface pública muda
