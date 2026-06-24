## Capability: feed-management

### Test: Adicionar outro salva e mantém diálogo aberto
**Traces**: `specs/feed-management/spec.md` → Requirement: Multi-feed creation
- **GIVEN** o diálogo "Adicionar Feed" está aberto
- **AND** o campo de URL contém "https://example.com/feed.xml"
- **AND** o dropdown categoria está em "Sem categoria"
- **WHEN** o usuário clica em "Adicionar outro"
- **THEN** o feed é salvo no banco
- **AND** o refresh das entradas é executado em background
- **AND** o campo de URL é limpo
- **AND** o dropdown de categoria permanece inalterado
- **AND** a lista de feeds visível é atualizada
- **AND** o diálogo permanece aberto
- **AND** o foco está no campo de URL

### Test: Adicionar outro com categoria
**Traces**: `specs/feed-management/spec.md` → Requirement: Multi-feed creation
- **GIVEN** o diálogo "Adicionar Feed" está aberto
- **AND** existe a categoria "Tech"
- **AND** o campo de URL contém "https://example.com/feed.xml"
- **AND** o dropdown categoria está selecionado em "Tech"
- **WHEN** o usuário clica em "Adicionar outro"
- **THEN** o feed é salvo com `category_id` apontando para "Tech"
- **AND** o campo de URL é limpo
- **AND** o dropdown de categoria mantém o valor "Tech"

### Test: CRITICAL - Adicionar fecha o diálogo e navega
**Traces**: `specs/feed-management/spec.md` → Requirement: Add feed by URL
- **GIVEN** o diálogo "Adicionar Feed" está aberto
- **AND** o campo de URL contém "https://example.com/feed.xml"
- **WHEN** o usuário clica em "Adicionar"
- **THEN** o feed é salvo
- **AND** o diálogo é fechado
- **AND** a navegação vai para `/feed/https://example.com/feed.xml`

### Test: Adicionar outro com URL vazia não faz nada
**Traces**: `specs/feed-management/spec.md` → Requirement: Multi-feed creation
- **GIVEN** o diálogo "Adicionar Feed" está aberto
- **AND** o campo de URL está vazio
- **WHEN** o usuário clica em "Adicionar outro"
- **THEN** o sistema não tenta salvar
- **AND** o diálogo permanece aberto
- **AND** nenhum erro é exibido

### Test: Adicionar outro com feed duplicado exibe erro e mantém URL
**Traces**: `specs/feed-management/spec.md` → Requirement: Multi-feed creation
- **GIVEN** o diálogo "Adicionar Feed" está aberto
- **AND** já existe o feed "https://example.com/feed.xml" para o usuário
- **AND** o campo de URL contém "https://example.com/feed.xml"
- **WHEN** o usuário clica em "Adicionar outro"
- **THEN** o sistema exibe snackbar "Feed já cadastrado"
- **AND** o campo de URL mantém o valor "https://example.com/feed.xml"
- **AND** o diálogo permanece aberto

### Test: ENTER no campo URL move foco para dropdown
**Traces**: `specs/feed-management/spec.md` → Requirement: Keyboard navigation in feed creation form
- **GIVEN** o diálogo "Adicionar Feed" está aberto
- **AND** o foco está no campo de URL
- **WHEN** o usuário pressiona ENTER no campo de URL
- **THEN** o foco move-se para o dropdown de categoria

### Test: EDGE - Adicionar outro múltiplas vezes em sequência
**Traces**: `specs/feed-management/spec.md` → (edge case)
- **GIVEN** o diálogo "Adicionar Feed" está aberto
- **WHEN** o usuário adiciona "url-a" com "Adicionar outro", depois "url-b" com "Adicionar outro", depois "url-c" com "Adicionar outro"
- **THEN** os três feeds existem na lista
- **AND** o diálogo permanece aberto após cada adição

### Test: EDGE - Adicionar outro seguido de Adicionar
**Traces**: `specs/feed-management/spec.md` → (edge case)
- **GIVEN** o diálogo "Adicionar Feed" está aberto
- **WHEN** o usuário adiciona "url-a" com "Adicionar outro"
- **AND** preenche "url-b" e clica em "Adicionar"
- **THEN** ambos os feeds existem
- **AND** o diálogo fecha e navega para "/feed/url-b"

### Test: EDGE - Cancelar diálogo após Adicionar outro
**Traces**: `specs/feed-management/spec.md` → (edge case)
- **GIVEN** o diálogo "Adicionar Feed" está aberto
- **AND** o usuário já adicionou um feed com "Adicionar outro"
- **WHEN** o usuário clica em "Cancelar"
- **THEN** o diálogo fecha normalmente
- **AND** o feed adicionado anteriormente permanece na lista

## Edge Cases

- **Cancelar após múltiplos "Adicionar outro"**: feeds já salvos não são desfeitos ao cancelar.
- **Refresh concorrente**: se o usuário clicar "Adicionar outro" rapidamente várias vezes, múltiplos refreshes podem estar em andamento. O `state.loading` previne visualmente, mas o backend precisa lidar.

## Integration Points

- **Lista de feeds**: `_rebuild_feed_list()` é chamada tanto após "Adicionar" quanto após "Adicionar outro". Ambas devem produzir o mesmo resultado na lista visível.
- **Serviço `add_feed`**: não alterado. Ambos os botões passam pelos mesmos parâmetros. `ValueError` (duplicata) é tratado com snackbar.
- **Serviço `refresh_single_feed`**: chamado em background para ambos os botões.
- **`state.loading` + `ProgressRing`**: já existe em `feed_list_view`. Reutilizado sem alterações.

## Review Notes

Nenhuma ambiguidade ou cenário não testável identificado.
