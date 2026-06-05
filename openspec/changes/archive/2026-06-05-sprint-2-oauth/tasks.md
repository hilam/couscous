## 1. Model and dependencies

- [x] 1.1 Adicionar colunas `oauth_provider` (str, nullable) e `oauth_id` (str, nullable) ao modelo `User` em `database/models/couscous.py`
- [x] 1.2 Adicionar dependência `authlib>=1.5` no `pyproject.toml`
- [x] 1.3 Adicionar variáveis de ambiente OAuth no `.env.sample`: `COUSCOUS_GOOGLE_CLIENT_ID`, `COUSCOUS_GOOGLE_CLIENT_SECRET`, `COUSCOUS_GITHUB_CLIENT_ID`, `COUSCOUS_GITHUB_CLIENT_SECRET`, `COUSCOUS_OAUTH_REDIRECT_URI`
- [x] 1.4 Atualizar `database/service/config.py` para carregar as novas variáveis de ambiente OAuth

## 2. OAuth service

- [x] 2.1 Criar `app/services/oauth_service.py` com configuração dos providers Google e GitHub usando `authlib`
- [x] 2.2 Implementar função `get_authorization_url(provider)` que gera URL com PKCE code challenge e state anti-CSRF
- [x] 2.3 Implementar função `handle_callback(provider, code, state)` que troca o code por tokens e busca userinfo
- [x] 2.4 Implementar função `get_or_create_oauth_user(session, provider, oauth_id, name, password_placeholder)` no `user_service.py` ou `oauth_service.py`
- [x] 2.5 Implementar lógica de fallback para colisão de nome de usuário (prefixo `gh_` ou `google_`)

## 3. OAuth route and callback

- [x] 3.1 Adicionar rota `/oauth/callback` no `app/app.py` com handler que delega para `oauth_service.handle_callback`
- [x] 3.2 Implementar `oauth_callback_view` no `app/views/` que processa o callback: valida state, troca code, cria/autentica usuário, redireciona para `/feeds`
- [x] 3.3 Tratar erros no callback: state mismatch, provider error, falha na troca de token — exibir mensagem e redirecionar para `/login`

## 4. UI — OAuth buttons

- [x] 4.1 Adicionar botões "Entrar com Google" e "Entrar com GitHub" no `login_view.py` (abaixo do formulário de senha)
- [x] 4.2 Adicionar botões "Entrar com Google" e "Entrar com GitHub" no `register_view.py`
- [x] 4.3 Esconder botão de provider quando as variáveis de ambiente correspondentes não estiverem configuradas
- [x] 4.4 Implementar `on_click` dos botões OAuth: abrir URL de autorização no navegador via `page.launch_url()`

## 5. Tests

- [x] 5.1 Atualizar `tests/conftest.py` com fixtures para simular configuração OAuth (env vars mockadas)
- [x] 5.2 Criar `tests/test_oauth_service.py` com testes para `get_or_create_oauth_user` (criação, retorno, colisão de nome)
- [x] 5.3 Atualizar `tests/test_user_service.py` para cobrir as novas funções OAuth no user_service
- [x] 5.4 Executar `uv run pytest` e garantir que todos os testes passam
