## Why

Adicionar vários feeds em sequência é trabalhoso. Atualmente o usuário precisa abrir o diálogo, preencher URL, selecionar categoria (opcional), clicar "Adicionar", aguardar o refresh e a navegação para a página do feed, e então voltar à lista para adicionar o próximo. Não há suporte à adição em lote.

## What Changes

- Adicionar botão "Adicionar outro" no diálogo `AddFeedDialog`, que salva o feed, faz o refresh em background, mantém o formulário aberto, limpa o campo de URL e refoca o campo para nova digitação.
- Manter o botão "Adicionar" com comportamento inalterado (salva, faz refresh, fecha o diálogo e navega para `/feed/{url}`).
- Adicionar navegação por teclado: ENTER no campo de URL move o foco para o dropdown de categoria.
- Extrair lógica de submissão compartilhada no dialog (`_do_submit`) com retorno `bool` indicando sucesso.
- Reutilizar `state.loading` + `ProgressRing` existente como indicador visual durante o refresh em background.

## Capabilities

### Modified Capabilities
- `feed-management`: altera o requisito "Add feed by URL" para incluir o botão "Adicionar outro" e a navegação por teclado entre campos.

## Impact

- `app/controls/add_feed_dialog.py`: adicionar `on_submit_another`, `_submit_another`, extrair `_do_submit`, configurar `on_submit` no `url_field`.
- `app/views/feed_list_view.py`: adicionar `_handle_feed_add_another` callback, wire `on_submit_another` no `AddFeedDialog`.
- `tests/test_controls.py`: adicionar testes para novo botão e callback de continuidade.
