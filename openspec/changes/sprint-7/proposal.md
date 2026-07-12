## Why

O banco de dados do CousCous acumula entries de feeds indefinidamente, sem mecanismo de limpeza — o que leva a consumo crescente de disco e degradação de performance ao longo do tempo. Além disso, o compartilhamento de links no Flet web está quebrado: `page.set_clipboard()` não funciona por restrições de segurança do browser, e não há botão visível de "copiar link" para o usuário.

## What Changes

- **Serviço de limpeza de entries antigas**: Nova função `purge_older_than(days)` que remove entries e suas `EntryTag` associadas anteriores a um período configurável. **Entries marcadas como importantes (`important=1`) são preservadas** independentemente da idade. Exibe contagem de entries afetadas antes da confirmação.
- **Diálogo de limpeza manual**: Interface com seleção de período (7, 30, 90, 365 dias), confirmação com contagem de entries afetadas, e execução assíncrona.
- **Remoção do modelo `FeedMetadata`**: Modelo não utilizado em nenhum lugar do código — removido junto com sua tabela.
- **Limpeza automática por usuário**: Configuração global de retenção (dias) no perfil do usuário. A limpeza é executada no refresh de feeds e, opcionalmente, na inicialização do app.
- **Cópia de link funcional na web**: Substituição de `set_clipboard()` por `navigator.clipboard.writeText()` via `page.run_javascript()` no `entry_view` e no `ArticleCard`.
- **Feedback visual de cópia**: Snackbar confirmando "Link copiado!" após a ação.

## Capabilities

### New Capabilities

- `database-cleanup`: Remoção de entries antigas com seleção de período (7/30/90/365 dias), contagem prévia de registros afetados, modo manual via diálogo e modo automático por usuário. Inclui remoção em cascata das `EntryTag` associadas, remoção do modelo morto `FeedMetadata`, e preservação de entries marcadas como importantes (`important=1`). Configuração de retenção exposta na `settings_view` como dropdown.
- `copy-link`: Cópia do link da entry para a área de transferência usando `navigator.clipboard.writeText` (compatível com web) com feedback via snackbar. Botão presente no `entry_view` (abertura individual) e no `ArticleCard` (lista de entries).

### Modified Capabilities

_Nenhuma._ As capacidades existentes (`feed-management`, `entry-viewing`, `feed-viewing`) mantêm seus requisitos inalterados. O botão de copiar link é aditivo — não muda o comportamento existente de visualização de entry.

## Impact

- **Novos arquivos**: `app/services/cleanup_service.py`, `app/controls/cleanup_dialog.py`
- **Arquivos modificados**: `app/views/entry_view.py` (botão copiar link + snackbar), `app/controls/article_card.py` (botão copiar link), `app/views/settings_view.py` (configuração de retenção + botão de limpeza manual), `app/services/settings_service.py` (persistência de `auto_cleanup_days`), `app/app.py` (limpeza na inicialização)
- **Banco de dados**: Nova coluna `auto_cleanup_days` (nullable int) no modelo `User`, remoção da tabela `feed_metadata` e do modelo `FeedMetadata` — migration Alembic necessária
- **Dependências**: Nenhuma nova. `navigator.clipboard.writeText` é API nativa do browser. `json.dumps` da stdlib para serializar a string no `run_javascript`
- **Sem breaking changes**
