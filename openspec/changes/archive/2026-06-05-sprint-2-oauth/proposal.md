## Why

Atualmente o CousCous só permite login via nome de usuário + senha. Adicionar OAuth com Google e GitHub reduz fricção no onboarding (usuário não precisa criar/escolher mais uma senha), aumenta conversão de registro e atende a uma expectativa moderna de qualquer aplicação web.

## What Changes

- Adicionar dependência `authlib` para fluxos OAuth 2.0 padronizados
- Criar `app/services/oauth_service.py` com fluxos de autorização para Google e GitHub
- Adicionar colunas `oauth_provider` (google/github/null) e `oauth_id` (string, nullable) ao modelo `User`
- Configurar variáveis de ambiente para client_id, client_secret e redirect_uri de cada provider
- Criar botões "Entrar com Google" e "Entrar com GitHub" nas telas de login e registro
- Implementar callback OAuth que cria novo usuário (se não existir) ou autentica usuário existente vinculado ao mesmo provider + id
- Vincular conta OAuth a usuário existente por email (Google) ou username (GitHub), evitando duplicatas

## Capabilities

### New Capabilities
- `oauth-authentication`: Login e registro via OAuth 2.0 com Google e GitHub, incluindo criação automática de conta, vinculação por email/username e tratamento de erros do fluxo OAuth

### Modified Capabilities
- `user-auth`: Suporte a autenticação alternativa via OAuth — o login pode ocorrer por senha OU por provider OAuth, e o estado da sessão (`state.user`) é populado da mesma forma em ambos os casos

## Impact

- **Modelos**: `User` ganha 2 novas colunas nullable (`oauth_provider`, `oauth_id`)
- **Serviços**: Novo `app/services/oauth_service.py`; `user_service.py` ganha funções `get_or_create_oauth_user` e `get_by_oauth`
- **Views**: `login_view.py` e `register_view.py` ganham botões OAuth; nova rota `/oauth/callback` no `app.py`
- **Dependências**: Adicionar `authlib` ao `pyproject.toml`
- **Configuração**: Novas variáveis de ambiente no `.env` e `.env.sample` para credenciais OAuth
- **Segurança**: PKCE (Proof Key for Code Exchange) deve ser usado no fluxo OAuth; `state` parameter para prevenção de CSRF
