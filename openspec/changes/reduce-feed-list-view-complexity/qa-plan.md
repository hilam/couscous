## Capability: lint-compliance

### Test: make lint passa com zero erros
**Traces**: `specs/no-behavioral-change.md` → (refactoring validation)
- **GIVEN** o código após a extração de `on_feed_added` para módulo
- **WHEN** executa `make lint`
- **THEN** o comando retorna zero erros (sem PLR0915 em feed_list_view.py)

### Test: make check-all passa completo
**Traces**: `specs/no-behavioral-change.md` → (refactoring validation)
- **GIVEN** o código após a refatoração
- **WHEN** executa `make check-all`
- **THEN** lint, typecheck, testes e security passam sem falhas

## Capability: feed-management

### Test: Adicionar feed via dialog — fluxo de sucesso
**Traces**: `specs/no-behavioral-change.md` → (regression)
- **GIVEN** um usuário autenticado na tela de feeds
- **WHEN** abre o dialog de adicionar feed, insere uma URL válida e confirma
- **THEN** o feed é criado, o refresh individual é executado e o usuário é redirecionado para `/feed/{url}`

### Test: Adicionar feed duplicado exibe SnackBar
**Traces**: `specs/no-behavioral-change.md` → (regression)
- **GIVEN** um feed já cadastrado pelo usuário
- **WHEN** tenta adicionar o mesmo feed novamente
- **THEN** um SnackBar com "Feed já cadastrado" é exibido e o feed NÃO é duplicado

### Test: Adicionar feed com erro de fetch exibe SnackBar
**Traces**: `specs/no-behavioral-change.md` → (regression)
- **GIVEN** uma URL de feed inválida ou inacessível
- **WHEN** o usuário tenta adicionar
- **THEN** um SnackBar com a mensagem de erro (`feed.last_exception`) é exibido

### Test: CRITICAL - Adicionar feed com categoria especificada
**Traces**: `specs/no-behavioral-change.md` → (regression)
- **GIVEN** uma categoria existente
- **WHEN** o usuário adiciona um feed selecionando essa categoria no dialog
- **THEN** o feed é criado com `category_id` correto e aparece agrupado na tela

## Edge Cases

- **Lambda wrapper mantém interface**: `AddFeedDialog` chama `on_feed_added(url, category_id)` — o callback extraído deve receber os mesmos argumentos na mesma ordem
- **Parâmetro `category_id` opcional**: quando o dialog não passa categoria, `category_id` deve ser `None`, e `add_feed` deve tratar isso corretamente
- **Lista de feeds atualiza após adição**: a view deve reconstruir `feed_list` para refletir o novo feed, incluindo seu posicionamento correto por categoria

## Integration Points

- **AddFeedDialog**: o dialog carrega categorias via `add_feed_dialog.load_categories()` e passa `category_id` ao callback. A nova função `_handle_feed_added` deve receber esse parâmetro e repassá-lo a `add_feed`.
- **refresh_single_feed**: após adicionar o feed, a função chama `refresh_single_feed(s, feed)` — este fluxo deve permanecer inalterado.
- **Navegação pós-cadastro**: após sucesso, a view faz `page.push_route(f"/feed/{url}")` — este fluxo também deve permanecer inalterado.

## Review Notes

Nenhuma — specs são mínimas (refactoring puro, sem requisitos comportamentais novos ou modificados).
