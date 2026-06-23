## 1. Git Setup e Planejamento

- [x] 1.1 Criar branch de refatoração: `git checkout -b refactor/refactor-app-run`
- [x] 1.2 Fazer commit dos artefatos de planejamento: `git add openspec/changes/refactor-app-run/ && git commit -m "docs(planning): gera artefatos de planejamento para refactor app_run"`

## 2. Extrair tabela de rotas e helpers

- [x] 2.1 Criar a dataclass `_Route` e a tabela `_ROUTES` com todas as rotas atuais (login, register, oauth/callback, about, feeds, feed/, entry/, categories, /) no topo de `app/app.py`, antes de `app_run`
- [x] 2.2 Criar a função `_match_route(route: str) -> _Route | None` que itera `_ROUTES` e retorna a rota correspondente por prefix-matching
- [x] 2.3 Criar a função `_invoke_handler(route_def: _Route, route: str, ctx: PageContext)` que despacha para o handler correto, tratando extração de parâmetros para `/feed/` e `/entry/`
- [x] 2.4 Criar a função `_build_and_invoke(route_def: _Route, route: str, page: ft.Page, state: State)` que gerencia `async with get_db_session()` (se `requires_session=True`) e chama `_invoke_handler`
- [x] 2.5 Fazer commit: `git add app/app.py && git commit -m "refactor(routing): extrai tabela de rotas e helpers do on_route_change"`

## 3. Reescrever on_route_change com os novos helpers

- [x] 3.1 Reescrever `on_route_change` para: `page.views.clear()` → `_match_route(route)` → guarda de auth → `_build_and_invoke` ou `login_view` → `page.views.append(v)` → `set_navbar` condicional → `page.update()`
- [x] 3.2 Garantir que o fallback (`home_view`) é usado quando `_match_route` retorna `None`
- [x] 3.3 Garantir que a guarda de autenticação (`not state.user and not matched.is_public`) funciona como antes
- [x] 3.4 Fazer commit: `git add app/app.py && git commit -m "refactor(routing): reescreve on_route_change com tabela de rotas e helpers"`

## 4. Validação e Qualidade

- [x] 4.1 Executar linting e formatação com Ruff: `ruff check --fix . && ruff format .`
- [x] 4.2 Fazer commit de correções de estilo se houver: `git commit -m "style: aplica ruff apos refactor do app_run"`
- [x] 4.3 Executar type-check com mypy: `uv run mypy .`
- [x] 4.4 Executar testes automatizados: `uv run pytest`
- [x] 4.5 Executar QA manual conforme `qa-plan.md`:
  - [x] 4.5.1 Verificar rota `/login` — exibe login_view sem navbar
  - [x] 4.5.2 Verificar rota `/register` — exibe register_view sem navbar
  - [x] 4.5.3 Verificar rota `/about` — exibe about_view com navbar (índice Sobre)
  - [x] 4.5.4 Verificar rota `/feeds` — exibe feed_list_view com navbar (índice Feeds)
  - [x] 4.5.5 Verificar rota `/` — exibe feed_list_view com navbar (índice Início)
  - [x] 4.5.6 Verificar rota `/feed/<url>` — popula state.active_feed_url e exibe entry_list_view
  - [x] 4.5.7 Verificar rota `/entry/<id>` — extrai ID e exibe entry_view
  - [x] 4.5.8 Verificar rota `/categories` — exibe category_list_view com navbar (índice Categorias)
  - [x] 4.5.9 Verificar rota `/oauth/callback?code=...` — processa OAuth sem navbar
  - [x] 4.5.10 Verificar rota desconhecida — fallback para home_view
  - [x] 4.5.11 Verificar redirecionamento para login com usuário não autenticado em rota protegida
  - [x] 4.5.12 Verificar navegação sequencial por todas as rotas via navbar
- [x] 4.6 Fazer commit final se houver ajustes: `git commit -m "test(routing): valida refactor do on_route_change com QA manual"`
