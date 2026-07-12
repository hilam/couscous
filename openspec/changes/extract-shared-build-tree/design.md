## Context

A função `_build_tree` — que transforma uma lista plana de categorias em uma árvore aninhada com contagens de feeds e não-lidos agregadas por rollup — está duplicada em dois arquivos do código:

- `app/services/feed_browser.py` (~35 linhas, usada em `load()`)
- `app/views/category_list_view.py` (~35 linhas, usada em `refresh_tree()`, `_build_create_dialog`, e na inicialização)

Ambas as cópias são funcionalmente idênticas. O módulo `app/services/category_service.py` já exporta `get_categories_with_counts()`, que retorna a tripla `(list[Category], dict[int,int], dict[int,int])` que alimenta `_build_tree`. Isso faz de `category_service.py` o lar natural para a função extraída.

## Goals / Non-Goals

**Goals:**
- Eliminar a duplicação de `_build_tree` movendo-a para um único local compartilhado
- Manter a lógica interna da árvore exatamente como está (sem refatoração do algoritmo)
- Garantir que todos os consumidores existentes continuem funcionando sem mudança de comportamento

**Non-Goals:**
- Não refatorar a lógica interna de construção da árvore
- Não alterar o formato do dicionário retornado
- Não adicionar novas funcionalidades (ex: `has_unread`, `icon`)
- Não modificar testes existentes ou adicionar novos testes
- Não tocar arquivos fora do escopo (`explore_view.py`, outros services ou views)

## Decisions

| Decisão | Alternativa | Rationale |
|---------|-------------|-----------|
| Nome público: `build_category_tree()` | Manter `_build_tree` como privada | O plano original usa `build_category_tree` como nome exportado. Seguir convenção de nomes verbosos em inglês para funções públicas no service layer. |
| Função síncrona e pura | Tornar async | A função não faz I/O — apenas processa dados em memória. Mantê-la síncrona evita overhead desnecessário e é consistente com seu uso atual (chamada síncrona dentro de funções async). |
| Parâmetros opcionais com `None` como default (`feed_counts=None, unread_counts=None`) | Parâmetros obrigatórios | As chamadas existentes sempre passam os dicts, mas tornar opcional com fallback para `{}` é mais robusto e permite uso em contextos que só precisam da estrutura da árvore sem contagens. |
| Destino: `category_service.py` | Novo módulo separado (`tree_utils.py`) | A função é consumidora natural de `get_categories_with_counts` que já vive em `category_service`. Evita criar novo módulo para uma única função de 35 linhas (YAGNI). |
| Import substitui chamada local | Manter `_build_tree` e delegar | Substituir o import é mais limpo — elimina a função local morta e deixa explícito que a implementação vive em outro lugar. |

## Risks / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| As duas cópias podem ter divergido desde o plano | Comparar linha por linha antes de extrair. Se divergiram, criar versão que atenda a ambas ou reportar como condição STOP. |
| `_flatten_tree_for_dropdown` em `category_list_view.py` depende do formato da árvore | A função usa o mesmo formato de dict que `_build_tree` produz. Como o formato não muda, não há risco. |
| Regressão silenciosa se a ordem dos nós na árvore mudar | A entrada (`cats: list[Category]`) determina a ordem. A lógica de árvore é idêntica. Testes existentes de `feed_browser` (plano 003) protegem contra regressão. |
