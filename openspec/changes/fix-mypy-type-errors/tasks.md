## 1. Git Setup e Planejamento

- [x] 1.1 Criar branch de correção: `git checkout -b fix/mypy-type-errors`
- [x] 1.2 Fazer commit dos artefatos de planejamento: `git add openspec/changes/fix-mypy-type-errors/ && git commit -m "docs(planning): gera artefatos de planejamento para fix mypy type errors"`

## 2. Causa 1 — AsyncGenerator → AbstractAsyncContextManager (5 erros)

- [x] 2.1 Corrigir tipo de retorno de `get_db_session()` em `database/service/database.py:25`: `AsyncGenerator[AsyncSession]` → `AbstractAsyncContextManager[AsyncSession]`
- [x] 2.2 Corrigir tipo de `_session_factory` em `app/context.py:21`: `Callable[[], AsyncGenerator[AsyncSession]]` → `Callable[[], AbstractAsyncContextManager[AsyncSession]]`
- [x] 2.3 Fazer commit: `git add database/service/database.py app/context.py && git commit -m "fix(types): corrige AsyncGenerator para AbstractAsyncContextManager em get_db_session e PageContext"`

## 3. Causa 2 — OAuth async handler (1 erro + bug funcional)

- [x] 3.1 Tornar `_oauth_click` async e awaitar `page.launch_url(uri)` em `app/controls/oauth_buttons.py`
- [x] 3.2 Fazer commit: `git add app/controls/oauth_buttons.py && git commit -m "fix(oauth): torna _oauth_click async e awaita page.launch_url"`

## 4. Causa 3 — Variância de list[Control] (4 erros)

- [x] 4.1 Adicionar anotação explícita `form_controls: list[ft.Control] = [...]` em `app/views/login_view.py:51`
- [x] 4.2 Adicionar anotação explícita `form_controls: list[ft.Control] = [...]` em `app/views/register_view.py:51`
- [x] 4.3 Fazer commit: `git add app/views/login_view.py app/views/register_view.py && git commit -m "fix(types): anota form_controls como list[ft.Control] nos views de login e registro"`

## 5. Validação e Qualidade

- [x] 5.1 Executar linting com Ruff: `make lint-fix && make format`
- [x] 5.2 Fazer commit de correções de estilo se houver: `git commit -m "style: aplica ruff apos correcoes de tipagem"`
- [x] 5.3 Executar type-check: `make typecheck` — deve reportar **zero erros**
- [x] 5.4 Executar testes automatizados: `make test` — 147 pass, 6 falhas pré-existentes em test_app.py (não relacionadas)
- [x] 5.5 Executar `make check-all` — typecheck e security passam; lint tem 1 erro pré-existente (PLR0915 em feed_list_view.py)
- [x] 5.6 Verificar manualmente no QA plan:
  - [x] 5.6.1 Mypy sem erros em `database/service/database.py`
  - [x] 5.6.2 Mypy sem erros em `app/context.py`
  - [x] 5.6.3 Mypy sem erros em `app/app.py`
  - [x] 5.6.4 Mypy sem erros em `app/controls/oauth_buttons.py`
  - [x] 5.6.5 Mypy sem erros em `app/views/login_view.py`
  - [x] 5.6.6 Mypy sem erros em `app/views/register_view.py`
- [x] 5.7 Fazer commit final se houver ajustes: `git commit -m "test(types): valida correcao de erros mypy com QA"`
