## 1. Setup e Remoção de Dependências

- [x] 1.1 Adicionar `flet` ao `pyproject.toml` e remover `rio-ui`
- [x] 1.2 Remover arquivos: `web/`, `api/`, `rio.toml`
- [x] 1.3 Criar diretório `app/` com `__init__.py`
- [x] 1.4 Criar `main.py` (entrypoint: `ft.app(target=app_run)`)

## 2. Infraestrutura Core do Flet

- [x] 2.1 Criar `app/app.py` com `app_run(page)`, tema, e `on_route_change`
- [x] 2.2 Criar `app/state.py` com classe `State` (usuário logado, feed ativo, loading)
- [x] 2.3 Implementar roteamento em `on_route_change` com sessão por tela
- [x] 2.4 Configurar `ft.NavigationBar` com destinos: Home, Feeds, About
- [x] 2.5 Verificar que `database/service/database.py` funciona com `AsyncSession` importado do Flet

## 3. Camada de Serviço

- [x] 3.1 Criar `app/services/__init__.py`
- [x] 3.2 Criar `app/services/feed_service.py`: `list_feeds`, `add_feed`, `remove_feed`
- [x] 3.3 Criar `app/services/entry_service.py`: `list_entries`, `get_entry`, `mark_read`, `mark_important`
- [x] 3.4 Criar `app/services/user_service.py`: `register`, `login`, `get_by_name`
- [x] 3.5 Criar `app/services/refresh_service.py`: `refresh_all_feeds` (com `asyncio.to_thread`)

## 4. Views

- [x] 4.1 Criar `app/views/__init__.py`
- [x] 4.2 Criar `app/views/home_view.py`: página inicial com boas-vindas e resumo
- [x] 4.3 Criar `app/views/feed_list_view.py`: lista de feeds com `ft.ListView` + `ft.Card`
- [x] 4.4 Criar `app/views/entry_list_view.py`: artigos de um feed específico
- [x] 4.5 Criar `app/views/entry_view.py`: conteúdo completo de um artigo com `ft.Markdown`
- [x] 4.6 Criar `app/views/about_view.py`: página sobre
- [x] 4.7 Criar `app/views/login_view.py`: formulário de login/registro

## 5. Componentes (Controls)

- [x] 5.1 Criar `app/controls/__init__.py`
- [x] 5.2 Criar `app/controls/feed_card.py`: `ft.Card` com título, link, contagem de artigos
- [x] 5.3 Criar `app/controls/article_card.py`: `ft.Card` com título, data, resumo
- [x] 5.4 Criar `app/controls/add_feed_dialog.py`: `ft.AlertDialog` com campo de URL
- [x] 5.5 Criar `app/controls/confirm_dialog.py`: `ft.AlertDialog` genérico de confirmação

## 6. Integração e Estado Global

- [x] 6.1 Conectar login_view ao state (setar `state.user` após login/registro)
- [x] 6.2 Mostrar nome do usuário no NavigationBar ou AppBar quando logado
- [x] 6.3 Implementar refresh manual na feed_list_view com loading indicator
- [x] 6.4 Garantir que NavigationBar destaque a página ativa

## 7. Testes e Limpeza

- [x] 7.1 Atualizar `tests/conftest.py`: remover fixture `web.create_app`, adicionar suporte a testes de serviço
- [x] 7.2 Testar `feed_service.list_feeds` com banco temporário
- [x] 7.3 Testar `user_service.register` e `login`
- [x] 7.4 Testar `entry_service.list_entries` com feed mockado
- [x] 7.5 Executar `ruff check .` e `pyright .` — garantir que passa
- [x] 7.6 Remover dependências não utilizadas (fastapi, rio-ui, uvicorn se não usado mais)

## 8. Cross-Platform Build

- [x] 8.1 Testar `flet run` em modo web browser
- [x] 8.2 Executar `flet build web` e verificar output
- [x] 8.3 Executar `flet build linux`
