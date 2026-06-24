## Context

O diálogo de adição de feed (`AddFeedDialog` em `app/controls/add_feed_dialog.py`) possui um único botão "Adicionar" que fecha o diálogo e delega o salvamento ao callback `on_submit`. Na view (`feed_list_view.py`), `_handle_feed_added` salva o feed, faz refresh e navega para `/feed/{url}`.

O usuário final deseja adicionar vários feeds em sequência sem reabrir o diálogo ou ser redirecionado a cada adição.

Escopo: `app/controls/add_feed_dialog.py`, `app/views/feed_list_view.py`, `tests/test_controls.py`. Nenhum serviço, modelo ou rota é alterado.

## Goals / Non-Goals

**Goals:**
- Botão "Adicionar outro" salva feed, faz refresh em background com spinner (`state.loading`), limpa URL, atualiza lista, mantém diálogo aberto com foco no campo URL
- Botão "Adicionar" mantém comportamento inalterado
- ENTER no campo URL → foco no dropdown categoria
- Lógica de submissão extraída em `_do_submit()` compartilhada
- Callback `on_submit_another(url, cid) -> bool` para que o dialog saiba se deve limpar os campos

**Non-Goals:**
- Não altera o serviço `feed_service.py` ou `refresh_service.py`
- Não altera o modelo `Feed`
- Não altera a navegação pós-"Adicionar" (continua indo para `/feed/{url}`)

## Decisions

| Decisão | Opção | Alternativa | Razão |
|---------|-------|-------------|-------|
| Callback para "Adicionar outro" | `on_submit_another(url, cid) -> bool` separado | Callback único com parâmetro `stay_open` | Separação clara de responsabilidades, espelha o padrão de categorias |
| ENTER no campo URL | `url_field.on_submit` → foco no dropdown | ENTER submeter "Adicionar outro" | Segue padrão de formulário: foco no próximo campo |
| Indicador de carregamento | Reutilizar `state.loading` + `ProgressRing` existente | Spinner no próprio dialog | Consistência com o restante da UI, evita duplicação |
| Pós-sucesso no "Adicionar" | Fecha dialog, navega para `/feed/{url}` (inalterado) | Manter na lista | Comportamento existente funciona bem para adição única |
| Pós-sucesso no "Adicionar outro" | Limpa URL, refoca, atualiza lista, mantém dialog | Recarregar dropdown de categoria também | Categorias não mudam com a adição de feeds, dropdown não precisa recarregar |
| Tratamento de duplicata | Snackbar + manter URL + manter dialog aberto | Fechar dialog | Igual ao pattern de categorias: usuário pode corrigir a URL |

## Risks / Trade-offs

- **Refresh em background pode ser lento**: o `state.loading` + `ProgressRing` page-level cobre visualmente. O usuário pode continuar preenchendo a URL enquanto o refresh anterior termina.
- **Ordem de operações**: o feed é salvo primeiro, depois refresh é disparado. Se o refresh falhar, o feed já existe no banco — consistente com o comportamento atual.
