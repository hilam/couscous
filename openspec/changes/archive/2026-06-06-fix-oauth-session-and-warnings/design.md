## Context

O fluxo OAuth usa PKCE com um `code_verifier` e um `state` anti-CSRF, armazenados em `_oauth_states: dict` no nível do módulo (`oauth_service.py:48`). Quando o usuário clica no botão Google/GitHub, `page.launch_url()` abre o provider no browser. O provider redireciona de volta para `localhost:8550/oauth/callback?...`.

O problema: em Flet, esse redirect pode criar uma **nova conexão WebSocket** (nova sessão). O `_oauth_states` é um dict Python em memória de um processo específico — não é compartilhado entre sessões. Resultado: `handle_callback()` não encontra o state → `ValueError("Sessão OAuth inválida ou expirada")` → tela de erro → login.

Além disso, Flet 0.90.0 depreciou `page.launch_url()` em favor de `UrlLauncher().launch_url()`, gerando warnings.

## Goals / Non-Goals

**Goals:**
- Fazer o fluxo OAuth funcionar corretamente: state sobrevive ao redirect do provider
- Eliminar `DeprecationWarning` de `launch_url()` nos 2 locais afetados
- Manter compatibilidade com testes existentes (adaptar mocks)

**Non-Goals:**
- Alterar o protocolo OAuth (PKCE, escopos, endpoints)
- Adicionar suporte a novos providers
- Migrar para `flet_fastapi` ou outro servidor
- Alterar a UX do fluxo OAuth

## Decisions

### 1. `page.session.store` para estado OAuth (não `client_storage`, não cookie, não DB)

**Escolha:** Armazenar `code_verifier` + `provider` em `page.session.store` sob chave prefixada (ex: `oauth_state_{state}`).

**Alternativas consideradas:**

| Alternativa | Por que rejeitada |
|-------------|-------------------|
| `page.client_storage` | Persiste no `localStorage` do browser. Overkill — o state é efêmero (vive só até o callback). Além disso, expõe o `code_verifier` no cliente, o que é um risco de segurança. |
| Cookie assinado | Adiciona complexidade de criptografia/assinatura sem necessidade. O `page.session` já resolve. |
| Tabela no Postgres | Overkill para dados efêmeros. Adiciona latência de DB no fluxo de autenticação. |
| Continuar com dict de módulo + lock | Não resolve o problema — o dict de módulo não é compartilhado entre sessões Flet. |

**Fundamento:** `page.session.store` é o mecanismo nativo do Flet para estado que sobrevive a reconexões. Já é usado para `State` do usuário (`app.py:30`). Os dados ficam no servidor, não no cliente. O state OAuth expira naturalmente (é removido após o callback).

### 2. `get_authorization_url(page, provider)` e `handle_callback(page, code, state)`

**Escolha:** Adicionar `page: ft.Page` como primeiro parâmetro em ambas as funções.

**Alternativa considerada:** Passar apenas o `session.store` como dict. Rejeitada porque `page` é o objeto canônico do Flet e já é passado em todas as views — manter a assinatura consistente com o resto do app.

**Fundamento:** Todas as funções de view e serviço no app já recebem `page`. É idiomático.

### 3. `UrlLauncher().launch_url()` para substituir `page.launch_url()`

**Escolha:** Usar `ft.UrlLauncher().launch_url(uri)` (síncrono, sem await) nos dois locais.

**Fundamento:** A API é mais explícita e segue a recomendação do Flet 0.90+. O método síncrono é suficiente — não precisamos esperar o lançamento do URL.

## Risks / Trade-offs

- **Chave de sessão grande**: O state tem 16 bytes (22 chars base64). Prefixado com `oauth_state_`, fica ~35 chars. Desprezível.
- **Session store é opaco nos testes**: `page.session.store` é um dicionário simples no Flet — fácil de mockar com `MagicMock` ou `{}`.
- **Limpeza de states órfãos**: Se o usuário fecha o browser após iniciar OAuth mas antes do callback, o state fica no `session.store` até expirar. Não é um problema real (o state é inútil sem o code), mas poderíamos adicionar TTL no futuro.
- **`launch_url` síncrono vs assíncrono**: O método antigo era `await page.launch_url()`. O novo `UrlLauncher().launch_url()` é síncrono. Isso simplifica o código (não precisa de `asyncio.create_task` no lambda do botão).
