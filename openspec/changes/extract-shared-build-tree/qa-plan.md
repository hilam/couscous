## Capability: (refatoração interna — sem specs comportamentais)

Esta mudança não modifica capacidades existentes nem introduz novas. A validação
foca em garantir que o comportamento permanece idêntico após a extração.

### Test: A árvore retornada por `build_category_tree` é idêntica à das funções originais
**Traces**: (refatoração interna — sem spec associado)
- **GIVEN** uma lista de categorias com hierarquia pai-filho, `feed_counts` e `unread_counts`
- **WHEN** `build_category_tree` é chamada com os mesmos dados das funções originais
- **THEN** a estrutura da árvore, contagens e rollup são idênticos

### Test: CRITICAL — `load()` em `feed_browser.py` continua funcionando
**Traces**: (refatoração interna — sem spec associado)
- **GIVEN** o módulo `feed_browser.py` com `build_category_tree` importado de `category_service`
- **WHEN** `load()` é chamada
- **THEN** a função executa sem erro e retorna a árvore correta

### Test: CRITICAL — `refresh_tree()` em `category_list_view.py` continua funcionando
**Traces**: (refatoração interna — sem spec associado)
- **GIVEN** o módulo `category_list_view.py` com `build_category_tree` importado de `category_service`
- **WHEN** `refresh_tree()` é chamada
- **THEN** a função executa sem erro e renderiza a árvore corretamente

### Test: `_build_create_dialog` em `category_list_view.py` continua funcionando
**Traces**: (refatoração interna — sem spec associado)
- **GIVEN** o módulo `category_list_view.py` com `build_category_tree` importado
- **WHEN** `_build_create_dialog` é chamada
- **THEN** a função executa sem erro

### Test: build_category_tree com parâmetros opcionais default (None)
**Traces**: (refatoração interna — sem spec associado)
- **GIVEN** `build_category_tree` é chamada sem `feed_counts` e `unread_counts`
- **WHEN** a função processa a lista de categorias
- **THEN** as contagens são zero (fallback para `{}`)

## Edge Cases

- **Categoria sem filhos**: Deve aparecer como nó folha com `children: []`
- **Categoria com parent_id inválido (orphan)**: Deve ser tratada como nó raiz (o código atual faz isso via `if c.parent_id and c.parent_id in cat_map`)
- **Lista de categorias vazia**: Deve retornar lista vazia `[]`
- **feed_counts/unread_counts vazios**: Todas as contagens devem ser zero
- **Categoria única (sem hierarquia)**: Deve retornar um único nó raiz

## Integration Points

- `category_service.build_category_tree` é chamado por `feed_browser.py` e `category_list_view.py` — ambos devem ser verificados
- `_flatten_tree_for_dropdown` em `category_list_view.py` consome o output da árvore — o formato do dict não muda, mas deve ser verificado
- Testes existentes em `test_feed_browser.py` (plano 003) devem continuar passando — são a principal proteção contra regressão

## Review Notes

_Nenhuma._ Sem specs comportamentais para revisar. A validação é puramente técnica (typecheck, lint, testes existentes).
