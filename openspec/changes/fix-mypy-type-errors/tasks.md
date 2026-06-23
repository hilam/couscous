## 1. Git Setup e Planejamento

- [ ] 1.1 Criar branch de correção: `git checkout -b fix/mypy-type-errors`
- [ ] 1.2 Fazer commit dos artefatos de planejamento: `git add openspec/changes/fix-mypy-type-errors/ && git commit -m "docs(planning): gera artefatos de planejamento para fix mypy type errors"`

## 2. Causa 1 — AsyncGenerator → AbstractAsyncContextManager (5 erros)

- [ ] 2.1 Corrigir tipo de retorno de `get_db_session()` em `database/service/database.py:25`: `AsyncGenerator[AsyncSession]` → `AbstractAsyncContextManager[AsyncSession]`
- [ ] 2.2 Corrigir tipo de `_session_factory` em `app/context.py:21`: `Callable[[], AsyncGenerator[AsyncSession]]` → `Callable[[], AbstractAsyncContextManager[AsyncSession]]`
- [ ] 2.3 Fazer commit: `git add database/service/database.py app/context.py && git commit -m "fix(types): corrige AsyncGenerator para AbstractAsyncContextManager em get_db_session e PageContext"`

## 3. Causa 2 — OAuth async handler (1 erro + bug funcional)

- [ ] 3.1 Tornar `_oauth_click` async e awaitar `page.launch_url(uri)` em `app/controls/oauth_buttons.py`
- [ ] 3.2 Fazer commit: `git add app/controls/oauth_buttons.py && git commit -m "fix(oauth): torna _oauth_click async e awaita page.launch_url"`

## 4. Causa 3 — Variância de list[Control] (4 erros)

- [ ] 4.1 Adicionar anotação explícita `form_controls: list[ft.Control] = [...]` em `app/views/login_view.py:51`
- [ ] 4.2 Adicionar anotação explícita `form_controls: list[ft.Control] = [...]` em `app/views/register_view.py:51`
- [ ] 4.3 Fazer commit: `git add app/views/login_view.py app/views/register_view.py && git commit -m "fix(types): anota form_controls como list[ft.Control] nos views de login e registro"`

## 5. Validação e Qualidade

- [ ] 5.1 Executar linting com Ruff: `make lint-fix && make format`
- [ ] 5.2 Fazer commit de correções de estilo se houver: `git commit -m "style: aplica ruff apos correcoes de tipagem"`
- [ ] 5.3 Executar type-check: `make typecheck` — deve reportar **zero erros**
- [ ] 5.4 Executar testes automatizados: `make test`
- [ ] 5.5 Executar `make check-all` — deve passar todos os estágios (lint, typecheck, test, security)
- [ ] 5.6 Verificar manualmente no QA plan:
  - [ ] 5.6.1 Mypy sem erros em `database/service/database.py`
  - [ ] 5.6.2 Mypy sem erros em `app/context.py`
  - [ ] 5.6.3 Mypy sem erros em `app/app.py`
  - [ ] 5.6.4 Mypy sem erros em `app/controls/oauth_buttons.py`
  - [ ] 5.6.5 Mypy sem erros em `app/views/login_view.py`
  - [ ] 5.6.6 Mypy sem erros em `app/views/register_view.py`
- [ ] 5.7 Fazer commit final se houver ajustes: `git commit -m "test(types): valida correcao de erros mypy com QA"`
