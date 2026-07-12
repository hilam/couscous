## 1. Git Setup e Planejamento

- [x] 1.1 Criar branch de funcionalidade (`git checkout -b feat/sprint-7-limpeza-copiar-link`)
- [x] 1.2 Fazer commit dos artefatos de planejamento (`git add openspec/changes/sprint-7/ && git commit -m "docs(planning): gera artifacts do sprint 7 (limpeza + copy link)"`)

## 2. Database Migration

- [x] 2.1 Adicionar coluna `auto_cleanup_days: int | None = None` ao modelo `User` em `database/models/couscous.py`
- [x] 2.2 Remover classe `FeedMetadata` de `database/models/couscous.py`
- [x] 2.3 Gerar migration Alembic (`make db-migrate-create name="adiciona-auto-cleanup-days-remove-feed-metadata"`)
- [x] 2.4 Revisar migration gerada (confirmar `DROP TABLE IF EXISTS feed_metadata` e `ADD COLUMN auto_cleanup_days`)
- [x] 2.5 Aplicar migration (`make db-migrate-up`)
- [x] 2.6 Commit da migration (`git add . && git commit -m "feat(db): adiciona auto_cleanup_days ao User e remove FeedMetadata"`) (`git add . && git commit -m "feat(db): adiciona auto_cleanup_days ao User e remove FeedMetadata"`)

## 3. Serviço de Limpeza

- [x] 3.1 Criar `app/services/cleanup_service.py` com `count_entries_older_than(session, user_id, days) -> int`
- [x] 3.2 Implementar `purge_older_than(session, user_id, days) -> int` com filtro `user_id`, `important=0` e condição `first_updated_epoch < cutoff`
- [x] 3.3 Commit do serviço (`git add app/services/cleanup_service.py tests/test_cleanup_service.py && git commit -m "feat(cleanup): ..."`)

## 4. Diálogo de Limpeza

- [x] 4.1 Criar `app/controls/cleanup_dialog.py` com função `show_cleanup_dialog(page, session, user_id)`
- [x] 4.2 Implementar `AlertDialog` com `Dropdown` (opções: 7, 30, 90, 365 dias)
- [x] 4.3 Implementar consulta de contagem ao selecionar período e exibição de "X artigos serão removidos"
- [x] 4.4 Desabilitar botão "Limpar" quando contagem for zero
- [x] 4.5 Implementar execução assíncrona da limpeza com `asyncio.create_task`
- [x] 4.6 Exibir snackbar com total removido ao concluir e chamar `page.update()`
- [x] 4.7 Commit do diálogo (`git add app/controls/cleanup_dialog.py && git commit -m "feat(cleanup): implementa diálogo de limpeza com seleção de período"`)

## 5. Configurações — Limpeza Automática

- [x] 5.1 Estender `app/services/settings_service.py` com `auto_cleanup_days` get/save
- [x] 5.2 Adicionar `Dropdown` "Limpeza automática" em `app/views/settings_view.py` (opções: Desligado, 7, 30, 90, 365 dias)
- [x] 5.3 Adicionar botão "Limpar artigos antigos" em `app/views/settings_view.py` que chama `show_cleanup_dialog`
- [x] 5.4 Commit das configurações (`git add ... && git commit -m "feat(settings): adiciona config de limpeza automática e botão de limpeza manual"`) (`git add app/services/settings_service.py app/views/settings_view.py && git commit -m "feat(settings): adiciona config de limpeza automática e botão de limpeza manual"`)

## 6. Limpeza na Inicialização

- [x] 6.1 Adicionar flag `_cleanup_triggered: bool = False` na classe `State` (`app/state.py`)
- [x] 6.2 Em `app/app.py`, no `on_route_change`, após `state.user` ser definido e `_cleanup_triggered` for `False`, disparar `asyncio.create_task` com `_auto_cleanup`
- [x] 6.3 Função `_auto_cleanup` com snackbar
- [x] 6.4 Commit da inicialização (`git add app/state.py app/app.py && git commit -m "feat(cleanup): executa limpeza automática na inicialização pós-login"`)

## 7. Cópia de Link — entry_view

- [x] 7.1 Criar função utilitária `copy_to_clipboard(page, url)` com `page.run_javascript()` usando `navigator.clipboard.writeText`
- [x] 7.2 No JS, `.catch()` injeta banner de erro vermelho no DOM (5s auto-remove)
- [x] 7.3 Python sempre exibe snackbar "Link copiado!" após chamada
- [x] 7.4 Adicionar `IconButton` com `ft.Icons.CONTENT_COPY` no `AppBar.actions` do `entry_view.py`
- [x] 7.5 Não renderizar botão se `entry.link` for `None`, vazio, ou `page.web` for `False`
- [x] 7.6 Commit do entry_view (`git add app/views/entry_view.py && git commit -m "feat(copy-link): adiciona botão de copiar link no entry_view"`)

## 8. Cópia de Link — ArticleCard

- [x] 8.1 Adicionar `IconButton` com `ft.Icons.CONTENT_COPY` no `subtitle` do `ListTile` em `ArticleCard`
- [x] 8.2 Botão deve estar em uma `Row` de ações junto com tags e metadados existentes
- [x] 8.3 Não renderizar botão se `entry.link` for `None`, vazio, ou `page.web` for `False`
- [x] 8.4 Commit do ArticleCard (`git add app/controls/article_card.py && git commit -m "feat(copy-link): adiciona botão de copiar link no ArticleCard"`)

## 9. Qualidade e Validação

- [x] 9.1 Executar Ruff lint e format (`make lint && make format`)
- [x] 9.2 Executar typecheck (`make typecheck`)
- [x] 9.3 Executar testes existentes (`make test`) — 168/168 passaram
- [x] 9.4 Executar security scan (`make security`)
- [x] 9.5 Commit de ajustes de qualidade (`git commit -am "style: aplica ruff e ajustes de lint/typecheck"`)
