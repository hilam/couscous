# Plano de Desenvolvimento — CousCous

Baseado no `README.md`, 8 sprints de 1 dia (8h) cada, priorizados com dependências.

---

## Sprint 1 — Multi-usuário + correções de segurança (8h)

| # | Tarefa | Tempo |
|---|--------|-------|
| 1.1 | Hash de senhas (bcrypt) no `user_service.py` | 1h |
| 1.2 | Adicionar `user_id` (FK) ao modelo `Feed` e `Entry` | 1h |
| 1.3 | Migration script ou recriação das tabelas | 1h |
| 1.4 | Adaptar `feed_service`, `entry_service`, `refresh_service` para filtrar por usuário | 2h |
| 1.5 | Corrigir toggle visual da estrela (important) no `entry_view.py` | 0.5h |
| 1.6 | Adicionar filtro "não lidos" e "importantes" na lista de entries | 1.5h |
| 1.7 | Atualizar testes existentes para a nova FK de usuário | 1h |

**Dependência para:** todos os sprints seguintes.

---

## Sprint 2 — OAuth Google + GitHub (8h)

| # | Tarefa | Tempo |
|---|--------|-------|
| 2.1 | Adicionar dependência (`authlib`) no `pyproject.toml` | 0.5h |
| 2.2 | Criar `app/services/oauth_service.py` com fluxos Google e GitHub | 3h |
| 2.3 | Configurar variáveis de ambiente (client_id, secret, redirect_uri) | 0.5h |
| 2.4 | Criar botões OAuth na `login_view.py` e `register_view.py` | 1.5h |
| 2.5 | Callback de OAuth — criar usuário ou logar existente | 2h |
| 2.6 | Adicionar coluna `oauth_provider` + `oauth_id` ao modelo `User` (nullable) | 0.5h |

**Dependências:** Sprint 1.

---

## Sprint 3 — Categorias hierárquicas (pastas) (8h)

| # | Tarefa | Tempo |
|---|--------|-------|
| 3.1 | Criar modelo `Category` (id, user_id, name, parent_id FK self-referencing) | 1h |
| 3.2 | Adicionar `category_id` (FK nullable) ao modelo `Feed` | 0.5h |
| 3.3 | Criar `app/services/category_service.py` (CRUD + tree query) | 2h |
| 3.4 | Criar `app/views/category_list_view.py` com árvore de pastas | 2h |
| 3.5 | Adaptar `AddFeedDialog` para permitir selecionar categoria | 1h |
| 3.6 | Exibir feeds agrupados por categoria no `feed_list_view.py` | 1.5h |

**Dependências:** Sprint 1.

---

## Sprint 4 — Etiquetas para notícias (8h)

| # | Tarefa | Tempo |
|---|--------|-------|
| 4.1 | Criar modelo `EntryTag` (entry_id FK, tag str, user_id FK) — substitui `FeedTag` que é dead code | 1h |
| 4.2 | Criar `app/services/tag_service.py` (CRUD de tags + assign/remove em entries) | 2h |
| 4.3 | Interface de etiquetas no `entry_view.py` — adicionar/remover tags inline | 2h |
| 4.4 | Criar `app/controls/tag_chip.py` para exibição de tags nos cards | 1h |
| 4.5 | Exibir tags nos `ArticleCard` da lista de entries | 1h |
| 4.6 | Filtro por tag na `entry_list_view.py` | 1h |

**Dependências:** Sprint 1.

---

## Sprint 5 — Visualização alternativa + Busca full-text (8h)

| # | Tarefa | Tempo |
|---|--------|-------|
| 5.1 | Criar `app/views/explore_view.py` — navegação por categorias (drill-down: categoria → feeds → entries) | 3h |
| 5.2 | Criar filtro lateral por tags no explore view | 1.5h |
| 5.3 | Adicionar coluna `search_vector tsvector` gerada automaticamente (generated column) + índice GIN no modelo `Entry` — migration SQL manual (SQLModel não gera tsvector) | 1h |
| 5.4 | Criar `app/services/search_service.py` — função de busca com `ts_rank`, `ts_headline` e `tsquery` sobre `title`, `summary`, `content` | 1h |
| 5.5 | Criar barra de busca no app bar + `app/views/search_view.py` com resultados | 1.5h |

**Dependências:** Sprints 3 e 4.

---

## Sprint 6 — Temas claro/escuro + tamanho do texto (8h)

| # | Tarefa | Tempo |
|---|--------|-------|
| 6.1 | Adicionar `theme_mode` (light/dark/system) e `font_scale` ao modelo `User` | 0.5h |
| 6.2 | Substituir `about_view` por `settings_view` com toggle de tema + botão "Sobre" que abre popup (conteúdo legacy do about_view) — rota `/about` vira Config; NavBar: [Início] [Feeds] [Categorias] [Config] | 1.5h |
| 6.3 | Aplicar `page.theme_mode` dinamicamente e persistir no banco | 1h |
| 6.4 | Incluir controle de ajuste de tamanho de texto (slider ou botões +/-) na settings | 2h |
| 6.5 | Aplicar `font_scale` globalmente via `page.theme` | 1.5h |
| 6.6 | Persistir preferência do usuário e aplicar ao iniciar sessão | 1.5h |

**Dependências:** Sprint 1.

---

## Sprint 7 — Limpeza do banco + Copiar link (8h)

| # | Tarefa | Tempo |
|---|--------|-------|
| 7.1 | Criar `app/services/cleanup_service.py` — função `purge_older_than(days)` para entries e estatísticas de uso | 2h |
| 7.2 | Criar `app/controls/cleanup_dialog.py` com seleção de período (7, 30, 90, 365 dias) e confirmação | 2h |
| 7.3 | Adicionar opção de limpeza automática ao adicionar feed (checkbox "manter apenas X dias") | 1.5h |
| 7.4 | Implementar cópia de link via `page.run_javascript("navigator.clipboard.writeText(...)")` no `entry_view.py` — `page.set_clipboard()` não funciona na web (política de segurança do browser) | 1h |
| 7.5 | Adicionar botão "copiar link" com feedback visual (snackbar) no `entry_view.py` e `ArticleCard` | 1h |
| 7.6 | Executar limpeza na inicialização (opcional, configurável) | 0.5h |

**Dependências:** Sprint 1.

---

## Sprint 8 — Backup e restauração com criptografia (8h)

| # | Tarefa | Tempo |
|---|--------|-------|
| 8.1 | Criar `app/services/backup_service.py` — exportar feeds + entries do usuário como JSON | 2h |
| 8.2 | Implementar criptografia simétrica (AES via `cryptography`) com senha fornecida pelo usuário | 2h |
| 8.3 | Criar função de restauração — decriptar + importar feeds e entries (merge, não duplicar) | 2h |
| 8.4 | Criar `app/controls/backup_dialog.py` — exportar com seleção de caminho + senha | 1h |
| 8.5 | Criar `app/controls/restore_dialog.py` — importar arquivo + senha | 1h |

**Dependências:** Sprint 1.

---

## Ordem de execução sugerida

```
Sprint 1 (fundação)
 ├── Sprint 3 (pastas)
 ├── Sprint 4 (tags)        ───┐
 ├── Sprint 2 (OAuth)          │
 ├── Sprint 6 (tema + fonte)   │
 ├── Sprint 7 (limpeza + link) │
 └── Sprint 8 (backup)         │
                               │
                 Sprint 5 (busca + explore)  ← depende de 3 e 4
```

Sprints 2, 3, 4, 6, 7 e 8 podem rodar em paralelo se houver mais de um dev, pois todas dependem apenas da Sprint 1. Sprint 5 requer 3+4 concluídas.

---

**Total estimado:** 8 sprints × 8h = **64 horas** (~8 dias úteis para 1 pessoa, ~4-5 dias para 2 pessoas com paralelismo).
