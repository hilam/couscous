## 1. Git Setup e Planejamento

- [ ] 1.1 Criar branch de correção: `git checkout -b fix/navigation-bar-views-list-empty`
- [ ] 1.2 Fazer commit dos artefatos de planejamento: `git add openspec/changes/fix-navigation-bar-views-list-empty/ && git commit -m "docs(planning): gera artefatos de planejamento para fix navbar"`

## 2. Centralizar set_navbar no handler on_route_change

- [ ] 2.1 Adicionar `from app.controls.nav_bar import set_navbar` em `app/app.py`
- [ ] 2.2 Após `page.views.append(v)` (linha 100), adicionar chamada condicional `set_navbar(page)` apenas para rotas que NÃO são `/login`, `/register` ou iniciam com `/oauth/callback`
- [ ] 2.3 Fazer commit: `git add app/app.py && git commit -m "fix(navbar): move set_navbar para apos page.views.append no handler"`

## 3. Remover set_navbar das funções de view

- [ ] 3.1 Remover `from app.controls.nav_bar import set_navbar` e chamada `set_navbar(page)` de `app/views/feed_list_view.py`
- [ ] 3.2 Remover `from app.controls.nav_bar import set_navbar` e chamada `set_navbar(ctx.page)` de `app/views/home_view.py`
- [ ] 3.3 Remover `from app.controls.nav_bar import set_navbar` e chamada `set_navbar(page)` de `app/views/entry_list_view.py`
- [ ] 3.4 Remover `from app.controls.nav_bar import set_navbar` e chamada `set_navbar(page)` de `app/views/entry_view.py`
- [ ] 3.5 Remover `from app.controls.nav_bar import set_navbar` e chamada `set_navbar(page)` de `app/views/category_list_view.py`
- [ ] 3.6 Remover `from app.controls.nav_bar import set_navbar` e chamada `set_navbar(ctx.page)` de `app/views/about_view.py`
- [ ] 3.7 Fazer commit: `git add app/views/ && git commit -m "refactor(navbar): remove set_navbar das funcoes de view"`

## 4. Validação e Qualidade

- [ ] 4.1 Executar linting com Ruff: `ruff check --fix . && ruff format .`
- [ ] 4.2 Fazer commit de correções de estilo se houver: `git commit -m "style: aplica ruff apos refactor da navbar"`
- [ ] 4.3 Executar type-check com mypy: `uv run mypy .`
- [ ] 4.4 Executar testes automatizados: `uv run pytest`
- [ ] 4.5 Executar QA manual — testar cenários do `qa-plan.md`:
  - [ ] 4.5.1 Login → verificar navbar em `/feeds` sem erro
  - [ ] 4.5.2 Cadastro → verificar navbar em `/feeds` sem erro
  - [ ] 4.5.3 Navegar pela navbar: Início, Feeds, Categorias, Sobre
  - [ ] 4.5.4 Verificar índices corretos em cada rota (`/`, `/feed/<url>`, `/categories`, `/about`)
  - [ ] 4.5.5 Verificar que `/login` e `/register` NÃO exibem navbar
- [ ] 4.6 Fazer commit final se houver ajustes: `git commit -m "test(navbar): valida correcao da navbar com QA manual"`
