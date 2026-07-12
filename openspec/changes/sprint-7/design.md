## Context

O CousCous nunca remove entries antigas — o banco cresce indefinidamente. Não há mecanismo de limpeza nem botão de copiar link funcional na web (Flet não suporta `set_clipboard` por restrições de segurança do browser). Este design cobre as duas capacidades novas: `database-cleanup` e `copy-link`, mais a remoção do modelo morto `FeedMetadata`.

O app usa Flet (Flutter wrapper), PostgreSQL + SQLModel async, Alembic para migrations. Serviços são funções async standalone recebendo `AsyncSession`. Views são funções async que retornam `ft.View`.

## Goals / Non-Goals

**Goals:**
- Permitir que o usuário remova entries antigas manualmente (via diálogo com seleção de período)
- Permitir limpeza automática configurável por usuário, executada após refresh e na inicialização
- Remover `FeedMetadata` (dead code) do modelo e do banco
- Implementar cópia de link funcional na web com feedback visual

**Non-Goals:**
- Limpeza agendada por timer/cron (fora do escopo do sprint)
- Exportação dos dados antes da limpeza (isso é sprint 8)
- Fallback para `document.execCommand('copy')` (não justifica o código extra)
- Remoção de feeds órfãos ou categorias vazias

## Decisions

### 1. Coluna `auto_cleanup_days` no modelo `User` + UI na `settings_view`

**Decisão:** Adicionar `auto_cleanup_days: int | None = None` ao modelo `User` (nullable). Quando `None`, limpeza automática desligada. Quando definido (ex: 30), entries não-importantes mais antigas que N dias são removidas.

Na `settings_view`, adicionar um `Dropdown` com label "Limpeza automática" e opções:
- "Desligado" (`None`)
- "7 dias"
- "30 dias"
- "90 dias"
- "365 dias"

O `settings_service` ganha `get_cleanup_days(session, user_id) -> int | None` e `save_cleanup_days(session, user_id, days)` (ou estende `save_settings` com parâmetro adicional).

**Alternativa considerada:** Coluna `retention_days` por feed — rejeitada por ser mais complexa (migration em Feed, UI em AddFeedDialog) sem ganho claro de granularidade.

### 2. Serviço de limpeza: duas funções separadas

**Decisão:** `cleanup_service.py` exporta duas funções:

- `count_entries_older_than(session, user_id, days) -> int` — usada pelo diálogo para mostrar quantas entries serão afetadas (barata, só `SELECT COUNT`).
- `purge_older_than(session, user_id, days) -> int` — executa a remoção de entries e retorna o número removido.

A remoção em cascata das `EntryTag` é automática — o modelo já tem `ondelete="CASCADE"` na FK.

**Alternativa considerada:** Função única com parâmetro `dry_run=True` — rejeitada, duas funções são mais explícitas e o count pode ser chamado sem preocupação com transação.

### 3. Query de limpeza: filtro por `first_updated_epoch`, excluindo importantes

**Decisão:** Filtrar entries por `first_updated_epoch < cutoff_date`, onde `cutoff_date = now() - timedelta(days=days)`. Incluir filtro `user_id` para escopo multi-usuário. **Entries com `important=1` são sempre preservadas**, independentemente da idade — o usuário marcou como relevante e espera que permaneçam.

```python
cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=days)
stmt = delete(Entry).where(
    Entry.user_id == user_id,
    Entry.important == 0,
    or_(
        Entry.first_updated_epoch < cutoff,
        Entry.first_updated_epoch == None,
    ),
)
```

**Alternativa considerada:** `published` (pode ser `None` ou antiga demais), `last_updated` (muda a cada refresh) — rejeitadas. `first_updated_epoch` é a data real de chegada ao sistema. Entries com `first_updated_epoch = NULL` são tratadas como antigas (dado corrompido ou ingestão anterior à existência do campo).

### 4. Diálogo de limpeza: `AlertDialog` com `Dropdown`

**Decisão:** `cleanup_dialog.py` implementa uma função `show_cleanup_dialog(page, session, user_id)` acionada por um botão "Limpar artigos antigos" na `settings_view`.
1. Abre `AlertDialog` com `Dropdown` (opções: 7, 30, 90, 365 dias)
2. Ao selecionar, chama `count_entries_older_than` e mostra o número
3. Botão "Limpar" chama `purge_older_than` em background (`asyncio.create_task`)
4. Ao concluir, mostra snackbar com total removido e atualiza a página

**Alternativa considerada:** `BottomSheet` — rejeitado, `AlertDialog` é mais natural para ação destrutiva com confirmação.

### 5. Limpeza automática apenas na inicialização

**Decisão:** A limpeza automática (`auto_cleanup_days` configurado) executa apenas na inicialização do app, em background, após o login. O botão de limpeza manual na `settings_view` cobre o caso de o usuário querer limpar sob demanda sem reiniciar. Não há limpeza automática durante o refresh de feeds — isso evita acoplar lógica de UI no fluxo de refresh e cobre o caso de uso real (limpeza periódica no início da sessão).

### 6. Limpeza na inicialização

**Decisão:** No `app_run` (em `app/app.py`), após login bem-sucedido, verificar `auto_cleanup_days` do usuário. Se definido, disparar `asyncio.create_task` que executa `purge_older_than` em background e, ao concluir, mostra snackbar com o total removido (ex: "🧹 Limpeza automática: 42 artigos antigos removidos"). Se nenhum entry foi removida, não mostra snackbar. Após o snackbar, chama `page.update()` para refletir mudanças na UI.

### 7. Cópia de link: `navigator.clipboard.writeText` + fallback com feedback DOM

**Decisão:** Função utilitária `copy_to_clipboard(page, url)` que executa JS com feedback visível:

```python
page.run_javascript(
    f"navigator.clipboard.writeText({json.dumps(url)})"
    f".then(function(){{}})"  # sucesso: silencioso, Python mostra snackbar
    f".catch(function(){{"
    f"var b=document.createElement('div');"
    f"b.textContent='\u26a0\ufe0f Erro ao copiar link — verifique as permissões do navegador';"
    f"b.style.cssText='position:fixed;bottom:20px;right:20px;background:#d32f2f;"
    f"color:white;padding:12px 20px;border-radius:8px;z-index:9999;font:14px sans-serif;';"
    f"document.body.appendChild(b);"
    f"setTimeout(function(){{b.remove();}},5000);"
    f"}})"
)
```

O Python sempre mostra snackbar "Link copiado!" após `run_javascript`. Em caso de falha (raro em localhost), o JS injeta um banner vermelho no DOM que desaparece em 5s — o usuário vê ambos e sabe que falhou. Sem polling, sem callbacks Python↔JS complexos.

**Alternativa considerada:** `document.execCommand('copy')` síncrono — rejeitado, é deprecated e não resolve o problema de feedback (ainda precisaríamos ler resultado do JS).

### 8. Posicionamento do botão "Copiar link"

**Decisão:** Dois pontos de inserção:
- **`entry_view`**: `IconButton` com ícone `Icons.CONTENT_COPY` no `actions` do `AppBar`, ao lado do botão de estrela/importante.
- **`ArticleCard`**: `IconButton` com ícone `Icons.CONTENT_COPY` no `subtitle` do `ListTile`, dentro de uma `Row` de ações junto com tags e metadados.

### 9. Remoção do `FeedMetadata`

**Decisão:** Remover a classe `FeedMetadata` de `database/models/couscous.py` e gerar migration Alembic que executa `DROP TABLE IF EXISTS feed_metadata`. Confirmado via `rg` que não há importações ou referências em `app/` ou `database/`.

## Risks / Trade-offs

- **[Limpeza em background race condition]**: Usuário pode estar visualizando uma entry que é removida durante a limpeza. Mitigação: ao concluir limpeza, disparar `page.update()`. Se a rota atual for `/entry/{id}` e a entry foi removida, redirecionar para `/feeds`. Se for `/feed/{url}` ou `/feeds`, recarregar a lista normalmente.
- **[`first_updated_epoch` sem índice]**: A coluna não tem índice dedicado. Para volumes pequenos (<100k entries) o scan sequencial é aceitável. Se degradar, adicionar índice `(user_id, first_updated_epoch)` via migration.
- **[`navigator.clipboard.writeText` em produção]**: Requer HTTPS ou localhost. O app é primariamente local (`127.0.0.1:8550`), então funciona. Se exposto via HTTP em rede, o botão falha silenciosamente — snackbar de erro seria útil mas adiciona complexidade de verificação JS. Deixamos sem verificação (ponytail: adicionar quando houver demanda de deploy remoto).
