## 1. Git Setup e Planejamento

- [ ] 1.1 Criar branch de funcionalidade (`git checkout -b feat/sprint-7-limpeza-copiar-link`)
- [ ] 1.2 Fazer commit dos artefatos de planejamento (`git add openspec/changes/sprint-7/ && git commit -m "docs(planning): gera artifacts do sprint 7 (limpeza + copy link)"`)

## 2. Database Migration

- [ ] 2.1 Adicionar coluna `auto_cleanup_days: int | None = None` ao modelo `User` em `database/models/couscous.py`
- [ ] 2.2 Remover classe `FeedMetadata` de `database/models/couscous.py`
- [ ] 2.3 Gerar migration Alembic (`make db-migrate-create name="adiciona-auto-cleanup-days-remove-feed-metadata"`)
- [ ] 2.4 Revisar migration gerada (confirmar `DROP TABLE IF EXISTS feed_metadata` e `ADD COLUMN auto_cleanup_days`)
- [ ] 2.5 Aplicar migration (`make db-migrate-up`)
- [ ] 2.6 Commit da migration (`git add . && git commit -m "feat(db): adiciona auto_cleanup_days ao User e remove FeedMetadata"`)

## 3. Serviço de Limpeza

- [ ] 3.1 Criar `app/services/cleanup_service.py` com `count_entries_older_than(session, user_id, days) -> int`
- [ ] 3.2 Implementar `purge_older_than(session, user_id, days) -> int` com filtro `user_id`, `important=0` e condição `first_updated_epoch < cutoff OR first_updated_epoch IS NULL`
- [ ] 3.3 Commit do serviço (`git add app/services/cleanup_service.py && git commit -m "feat(cleanup): implementa count e purge de entries antigas"`)

## 4. Diálogo de Limpeza

- [ ] 4.1 Criar `app/controls/cleanup_dialog.py` com função `show_cleanup_dialog(page, session, user_id)`
- [ ] 4.2 Implementar `AlertDialog` com `Dropdown` (opções: 7, 30, 90, 365 dias)
- [ ] 4.3 Implementar consulta de contagem ao selecionar período e exibição de "X artigos serão removidos"
- [ ] 4.4 Desabilitar botão "Limpar" quando contagem for zero
- [ ] 4.5 Implementar execução assíncrona da limpeza com `asyncio.create_task`
- [ ] 4.6 Exibir snackbar com total removido ao concluir e chamar `page.update()`
- [ ] 4.7 Commit do diálogo (`git add app/controls/cleanup_dialog.py && git commit -m "feat(cleanup): implementa diálogo de limpeza com seleção de período"`)

## 5. Configurações — Limpeza Automática

- [ ] 5.1 Estender `app/services/settings_service.py` com `get_cleanup_days(session, user_id) -> int | None` e `save_cleanup_days(session, user_id, days)`
- [ ] 5.2 Adicionar `Dropdown` "Limpeza automática" em `app/views/settings_view.py` (opções: Desligado, 7, 30, 90, 365 dias)
- [ ] 5.3 Adicionar botão "Limpar artigos antigos" em `app/views/settings_view.py` que chama `show_cleanup_dialog`
- [ ] 5.4 Commit das configurações (`git add app/services/settings_service.py app/views/settings_view.py && git commit -m "feat(settings): adiciona config de limpeza automática e botão de limpeza manual"`)

## 6. Limpeza na Inicialização

- [ ] 6.1 Adicionar flag `_cleanup_triggered: bool = False` na classe `State` (`app/state.py`)
- [ ] 6.2 Em `app/app.py`, no `on_route_change`, após `state.user` ser definido e `_cleanup_triggered` for `False` (e rota não for pública), disparar `asyncio.create_task` com `purge_older_than`
- [ ] 6.3 Exibir snackbar "🧹 Limpeza automática: N artigos antigos removidos" ao concluir (se N > 0)
- [ ] 6.4 Chamar `page.update()` após conclusão; redirecionar para `/feeds` se rota atual for `/entry/{id}` de entry removida
- [ ] 6.5 Commit da inicialização (`git add app/state.py app/app.py && git commit -m "feat(cleanup): executa limpeza automática na inicialização pós-login"`)

## 7. Cópia de Link — entry_view

- [ ] 7.1 Criar função utilitária `copy_to_clipboard(page, url)` com `page.run_javascript()` usando `navigator.clipboard.writeText`
- [ ] 7.2 No JS, `.catch()` injeta banner de erro vermelho no DOM (5s auto-remove)
- [ ] 7.3 Python sempre exibe snackbar "Link copiado!" após chamada
- [ ] 7.4 Adicionar `IconButton` com `ft.Icons.CONTENT_COPY` no `AppBar.actions` do `entry_view.py`
- [ ] 7.5 Não renderizar botão se `entry.link` for `None`, vazio, ou `page.web` for `False`
- [ ] 7.6 Commit do entry_view (`git add app/views/entry_view.py && git commit -m "feat(copy-link): adiciona botão de copiar link no entry_view"`)

## 8. Cópia de Link — ArticleCard

- [ ] 8.1 Adicionar `IconButton` com `ft.Icons.CONTENT_COPY` no `subtitle` do `ListTile` em `ArticleCard`
- [ ] 8.2 Botão deve estar em uma `Row` de ações junto com tags e metadados existentes
- [ ] 8.3 Não renderizar botão se `entry.link` for `None`, vazio, ou `page.web` for `False`
- [ ] 8.4 Commit do ArticleCard (`git add app/controls/article_card.py && git commit -m "feat(copy-link): adiciona botão de copiar link no ArticleCard"`)

## 9. Qualidade e Validação

- [ ] 9.1 Executar Ruff lint e format (`make lint && make format`)
- [ ] 9.2 Executar typecheck (`make typecheck`)
- [ ] 9.3 Executar testes existentes (`make test`) — garantir zero regressões
- [ ] 9.4 Executar security scan (`make security`)
- [ ] 9.5 Commit de ajustes de qualidade (`git commit -am "style: aplica ruff e ajustes de lint/typecheck"`)
