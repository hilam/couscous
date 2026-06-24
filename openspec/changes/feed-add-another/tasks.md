## 1. Git Setup e Planejamento

- [x] 1.1 Criar branch `feat/feed-add-another` a partir de `main`
- [x] 1.2 Fazer commit dos artefatos de planejamento (`docs(planning): gera proposal, specs, design, qa-plan e tasks`)

## 2. Refatorar `AddFeedDialog`

- [x] 2.1 Extrair `_do_submit()` — método que valida `url_field.value`, determina `category_id`, e retorna `(url, category_id)` ou `(None, None)` se URL vazia
- [x] 2.2 Refatorar `_submit` existente para fechar dialog e delegar ao `on_submit` via `_do_submit()`
- [x] 2.3 Adicionar `on_submit_another` como parâmetro opcional do `__init__` e `_submit_another` como método assíncrono que chama `on_submit_another(url, cid)`, e em caso de sucesso limpa `url_field`, refoca, e atualiza o dialog
- [x] 2.4 Adicionar `on_submit` no `url_field` para mover foco ao `category_dropdown` via `asyncio.create_task`
- [x] 2.5 Atualizar `actions` do `AlertDialog` para incluir "Cancelar", "Adicionar outro" (`ft.FilledButton`) e "Adicionar" (`ft.FilledButton`), com `actions_alignment` mantido
- [x] 2.6 Fazer commit do dialog refatorado (`feat(feeds): adiciona botao Adicionar outro ao AddFeedDialog`)

## 3. Adaptar `feed_list_view`

- [x] 3.1 Criar `_handle_feed_add_another(url, cid) -> bool` — salva feed, seta `state.loading`, faz refresh, trata duplicata com snackbar retornando `False`, trata erro de refresh com snackbar retornando `True`, sucesso retorna `True` e chama `_rebuild_feed_list`
- [x] 3.2 Passar `on_submit_another=_handle_feed_add_another` na construção do `AddFeedDialog`
- [x] 3.3 Fazer commit da view adaptada (`feat(feeds): implementa callback de adicao continua na view`)

## 4. Testes

- [x] 4.1 Atualizar `test_dialog_structure` para verificar 3 botões em vez de 2
- [x] 4.2 Adicionar teste `test_submit_another_with_valid_url` — verifica callback chamado com parâmetros corretos e campos limpos pós-sucesso
- [x] 4.3 Adicionar teste `test_submit_another_duplicate_keeps_url` — verifica que URL não é limpa quando callback retorna False
- [x] 4.4 Adicionar teste `test_submit_another_empty_url` — verifica que callback não é chamado
- [x] 4.5 Fazer commit dos testes (`test(feeds): adiciona testes para botao Adicionar outro`)

## 5. Validação e Qualidade

- [x] 5.1 Executar lint com `ruff check --fix .`
- [x] 5.2 Executar formatação com `ruff format .`
- [x] 5.3 Fazer commit de correções de estilo se houver (`style: aplica ruff`)
- [x] 5.4 Executar typecheck com `make typecheck`
- [x] 5.5 Executar testes existentes com `make test`
- [x] 5.6 Fazer commit de ajustes finais se houver
