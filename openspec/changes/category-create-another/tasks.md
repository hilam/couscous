## 1. Git Setup e Planejamento

- [ ] 1.1 Criar branch `feat/category-create-another` a partir de `main`
- [ ] 1.2 Fazer commit dos artefatos de planejamento (`docs(planning): gera proposal, specs, design, qa-plan e tasks`)

## 2. Refatorar `_build_create_dialog`

- [ ] 2.1 Extrair `_do_create()` — função assíncrona que valida `name_field.value`, resolve `parent_id`, chama `create_category`, trata `ValueError` com snackbar, e retorna `bool` indicando sucesso
- [ ] 2.2 Refatorar `_submit` existente para `_submit_and_close` — chama `_do_create()` e fecha o diálogo apenas em caso de sucesso
- [ ] 2.3 Adicionar `_submit_and_continue` — chama `_do_create()`, em caso de sucesso limpa `name_field.value`, recarrega `_load_parent_dropdown()`, chama `refresh_cb()`, e move foco para `name_field`
- [ ] 2.4 Adicionar `on_submit` no `name_field` para mover foco ao `parent_dropdown` via `asyncio.create_task`
- [ ] 2.5 Substituir `actions` do `AlertDialog` para incluir "Cancelar", "Criar outro" (`ft.FilledButton`) e "Criar" (`ft.FilledButton`), com `actions_alignment` mantido
- [ ] 2.6 Fazer commit do código refatorado (`feat(categories): adiciona botao Criar outro e navegacao por teclado`)

## 3. Validação e Qualidade

- [ ] 3.1 Executar lint com `ruff check --fix .`
- [ ] 3.2 Executar formatação com `ruff format .`
- [ ] 3.3 Fazer commit de correções de estilo se houver (`style: aplica ruff`)
- [ ] 3.4 Executar typecheck com `make typecheck`
- [ ] 3.5 Executar testes existentes com `make test`
- [ ] 3.6 Fazer commit de ajustes finais se houver
