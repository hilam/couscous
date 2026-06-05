## Context

O CousCous atualmente suporta apenas autenticação tradicional via nome de usuário + senha (com bcrypt). A Sprint 2 adiciona OAuth 2.0 com Google e GitHub como provedores alternativos.

O app é construído com Flet (framework Python full-stack), com navegação baseada em rotas no lado do cliente. O estado da sessão (`State.user`) é mantido em memória durante a execução do app — não há tokens JWT ou cookies de sessão. O modelo `User` atual tem apenas `id`, `name`, `password`.

### Ambiente atual
- **Flet**: executa como desktop (via `python main.py`) ou web (`flet run -w` na porta 8550)
- **Banco**: PostgreSQL 16 via Docker Compose, acessado via SQLModel async
- **Serviços**: todos assíncronos, recebem `session` como primeiro argumento
- **Rotas**: `/login`, `/register`, `/about` (públicas); `/feeds`, `/feed/<url>`, `/entry/<id>` (autenticadas)
- **Dependências**: não há biblioteca OAuth no momento

## Goals / Non-Goals

**Goals:**
- Adicionar login via Google OAuth 2.0
- Adicionar login via GitHub OAuth 2.0  
- Criar automaticamente conta de usuário no primeiro login OAuth
- Exibir botões OAuth nas telas de login e registro
- Manter consistência com o fluxo de autenticação existente (popula `state.user` e redireciona para `/feeds`)

**Non-Goals:**
- Vincular múltiplos provedores a uma mesma conta
- Gerenciamento de tokens OAuth (refresh, revoke)
- Sessão persistente entre reinicializações do app
- Email como campo obrigatório no modelo User
- Suporte a outros provedores além de Google e GitHub

## Decisions

### Biblioteca: authlib

**Escolha**: `authlib` (>=1.5) como biblioteca OAuth.

**Alternativas consideradas**:
- `httpx` direto: mais controle mas muito boilerplate para OAuth 2.0 (PKCE, state, token exchange)
- `requests-oauthlib`: síncrono, não compatível com a arquitetura async do app
- `authlib`: suporte nativo a async, PKCE integrado, clientes pré-configurados para Google/GitHub

**Rationale**: `authlib` oferece `OAuth2Session` async com PKCE e `register` de providers conhecidos, minimizando código customizado.

### Modelo User: colunas oauth_provider + oauth_id

**Escolha**: Adicionar duas colunas nullable ao modelo `User`:
- `oauth_provider: str | None` — "google" ou "github"
- `oauth_id: str | None` — identificador único do usuário no provider (Google: `sub` claim do id_token; GitHub: `id` numérico como string)

**Alternativas consideradas**:
- Tabela separada `OAuthAccount`: mais normalizada mas overkill para o caso atual (um usuário = um método de login)
- Campo `email` como chave de vinculação: exigiria solicitar scope `email` e mudar modelo User; muitos usuários GitHub têm email privado

**Rationale**: Colunas nullable mantêm compatibilidade com usuários existentes (que usam senha). A combinação `(oauth_provider, oauth_id)` é única por provider.

### Fluxo OAuth: PKCE + state parameter

**Escolha**: Usar PKCE (Proof Key for Code Exchange) com `code_challenge_method=S256` e parâmetro `state` anti-CSRF.

**Alternativas consideradas**:
- Client secret apenas (sem PKCE): menos seguro para apps públicos (desktop/single-page)
- Implicit flow: deprecated pelo OAuth 2.0 Security Best Current Practice

**Rationale**: PKCE é obrigatório para segurança em apps que não podem manter client_secret seguro (como apps desktop e SPAs). O Flet roda como app desktop ou web — ambos são considerados "public clients".

### Rota de callback: `/oauth/callback`

**Escolha**: Rota única `/oauth/callback` que recebe `code` e `state`, com o provider armazenado no `state` parameter ou query string.

**Alternativas consideradas**:
- Rotas separadas (`/oauth/google/callback`, `/oauth/github/callback`): mais explícito mas duplica lógica de callback

**Rationale**: Flet gerencia rotas client-side; uma única rota de callback reduz duplicação. O provider é codificado no `state` parameter do OAuth.

### Criação de usuário: name automático

**Escolha**: Para Google, usar o `name` do userinfo como `User.name`. Para GitHub, usar o `login` do userinfo. Se o nome já existir para outro usuário (não-OAuth), usar prefixo do provider (ex: `gh_nomeusuario`).

**Rationale**: O `User.name` é unique — colisões entre provider e usuários locais são possíveis e precisam de fallback.

### Env vars: prefixadas por provider

**Escolha**: Variáveis de ambiente no formato:
```
COUSCOUS_GOOGLE_CLIENT_ID
COUSCOUS_GOOGLE_CLIENT_SECRET
COUSCOUS_GITHUB_CLIENT_ID
COUSCOUS_GITHUB_CLIENT_SECRET
COUSCOUS_OAUTH_REDIRECT_URI
```

**Rationale**: Prefixo `COUSCOUS_` segue a convenção existente (e.g., `COUSCOUS_DATABASE_HOST`). Um único `redirect_uri` serve ambos os providers.

## Risks / Trade-offs

- **[Risco] Flet web mode não tem redirect_uri estático**: O `flet run -w` roda em `localhost:8550` mas o path exato depende de como o Flet gerencia rotas. → **Mitigação**: documentar que OAuth web requer configurar o redirect_uri correto no Google Cloud Console / GitHub OAuth Apps; o path `/oauth/callback` é previsível.

- **[Risco] State parameter armazenado em memória**: Se o app reiniciar entre iniciar o fluxo e receber o callback, o state é perdido. → **Mitigação**: escopo limitado (app roda localmente); state tem validade implícita de sessão.

- **[Risco] Client secrets em variáveis de ambiente**: Em app desktop, secrets ficam acessíveis no processo. → **Mitigação**: PKCE reduz a gravidade; para produção web, usar backend proxy.

- **[Trade-off] Nome de usuário automático pode ser não-intuitivo**: Usuário não escolhe o nome exibido. → **Mitigação**: nomes do Google/GitHub são familiares ao usuário; edição de perfil pode ser adicionada futuramente.

## Open Questions

- Deve ser possível definir senha posteriormente para contas OAuth? (escopo futuro)
- Suportar múltiplos providers por conta (link de contas)? (escopo futuro)
