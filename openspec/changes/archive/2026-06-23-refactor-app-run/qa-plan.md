## Capability: route-handler-refactor

### Test: Rota /login exibe tela de login
**Traces**: `specs/route-handler-refactor/spec.md` → Requirement: Preservação de comportamento existente
- **GIVEN** o app inicia ou um usuário não autenticado acessa qualquer rota protegida
- **WHEN** o sistema processa a rota `/login`
- **THEN** a view `login_view` é renderizada e a navbar NÃO é exibida

### Test: Rota /register exibe tela de cadastro
**Traces**: `specs/route-handler-refactor/spec.md` → Requirement: Preservação de comportamento existente
- **GIVEN** um usuário não autenticado
- **WHEN** o usuário navega para `/register`
- **THEN** a view `register_view` é renderizada e a navbar NÃO é exibida

### Test: Rota /about exibe tela sobre
**Traces**: `specs/route-handler-refactor/spec.md` → Requirement: Preservação de comportamento existente
- **GIVEN** um usuário autenticado
- **WHEN** o usuário navega para `/about`
- **THEN** a view `about_view` é renderizada com a navbar visível e índice "Sobre" selecionado

### Test: Rota /feeds exibe lista de feeds
**Traces**: `specs/route-handler-refactor/spec.md` → Requirement: Tabela de rotas declarativa
- **GIVEN** um usuário autenticado
- **WHEN** o usuário navega para `/feeds`
- **THEN** a view `feed_list_view` é renderizada com sessão de banco ativa e navbar com índice "Feeds" selecionado

### Test: Rota / exibe lista de feeds (mesmo handler que /feeds)
**Traces**: `specs/route-handler-refactor/spec.md` → Requirement: Tabela de rotas declarativa
- **GIVEN** um usuário autenticado
- **WHEN** o usuário navega para `/`
- **THEN** a view `feed_list_view` é renderizada (mesmo handler de `/feeds`) com navbar com índice "Início" selecionado

### Test: Rota /feed/<url> exibe entradas do feed
**Traces**: `specs/route-handler-refactor/spec.md` → Requirement: Extração de parâmetros de rota
- **GIVEN** um usuário autenticado
- **WHEN** o usuário navega para `/feed/https://example.com/rss`
- **THEN** `state.active_feed_url` é definido como `https://example.com/rss` e `entry_list_view` é renderizada

### Test: Rota /entry/<id> exibe uma entrada específica
**Traces**: `specs/route-handler-refactor/spec.md` → Requirement: Extração de parâmetros de rota
- **GIVEN** um usuário autenticado e uma entrada com ID 42 existe
- **WHEN** o usuário navega para `/entry/42`
- **THEN** `entry_view` é chamada com `entry_id=42` e renderiza o conteúdo da entrada

### Test: Rota /categories exibe lista de categorias
**Traces**: `specs/route-handler-refactor/spec.md` → Requirement: Tabela de rotas declarativa
- **GIVEN** um usuário autenticado
- **WHEN** o usuário navega para `/categories`
- **THEN** a view `category_list_view` é renderizada com navbar com índice "Categorias" selecionado

### Test: Rota /oauth/callback processa retorno OAuth
**Traces**: `specs/route-handler-refactor/spec.md` → Requirement: Preservação de comportamento existente
- **GIVEN** um usuário retornando do provedor OAuth
- **WHEN** o sistema processa `/oauth/callback?code=abc&state=xyz`
- **THEN** `oauth_callback_view` é chamada com sessão de banco ativa e navbar NÃO é exibida

### Test: Rota desconhecida usa fallback home_view
**Traces**: `specs/route-handler-refactor/spec.md` → Requirement: Tabela de rotas declarativa
- **GIVEN** um usuário autenticado
- **WHEN** o usuário navega para uma rota não registrada (ex: `/xyz`)
- **THEN** a view `home_view` é renderizada como fallback

### Test: Usuário não autenticado é redirecionado para login
**Traces**: `specs/route-handler-refactor/spec.md` → Requirement: Preservação de comportamento existente
- **GIVEN** um usuário NÃO autenticado (state.user é None)
- **WHEN** o usuário tenta acessar `/feeds` (rota não-pública)
- **THEN** a view `login_view` é renderizada em vez de `feed_list_view`

### Test: Usuário não autenticado acessa rota pública com sucesso
**Traces**: `specs/route-handler-refactor/spec.md` → Requirement: Preservação de comportamento existente
- **GIVEN** um usuário NÃO autenticado
- **WHEN** o usuário acessa `/about` (rota pública)
- **THEN** a view `about_view` é renderizada normalmente

### Test: EDGE - Ordem da tabela de rotas não causa match incorreto
**Traces**: `specs/route-handler-refactor/spec.md` → (edge case)
- **GIVEN** a tabela de rotas contém tanto `/` quanto `/feed/`
- **WHEN** o sistema processa a rota `/feed/https://example.com/rss`
- **THEN** a rota `/feed/` é matched (não `/`) e `entry_list_view` é chamada

### Test: EDGE - Rota /entry/ com ID não numérico
**Traces**: `specs/route-handler-refactor/spec.md` → (edge case)
- **GIVEN** um usuário autenticado
- **WHEN** o usuário navega para `/entry/abc`
- **THEN** o sistema lança `ValueError` (comportamento atual preservado — `int("abc")` falha)

### Test: EDGE - Sessão de banco fechada após renderização
**Traces**: `specs/route-handler-refactor/spec.md` → Requirement: Factory de contexto centralizada
- **GIVEN** uma rota com `requires_session=True` é acessada
- **WHEN** a view é renderizada e `page.update()` é chamado
- **THEN** a sessão de banco é fechada corretamente (não há vazamento de conexão)

## Edge Cases

- **Rota `/feed/` sem URL após a barra**: Comportamento atual — `state.active_feed_url` fica como string vazia. Deve ser preservado.
- **Rota `/entry/` sem ID**: `ValueError` ao chamar `int("")`. Comportamento atual preservado.
- **Múltiplas navegações rápidas**: O `page.views.clear()` + reconstrução de contexto deve funcionar corretamente sem interferência entre sessões concorrentes.
- **Rota `/` com usuário autenticado**: Deve corresponder ao handler `feed_list_view`, não ao fallback `home_view`.

## Integration Points

- **set_navbar**: A chamada `set_navbar(page)` após `page.views.append(v)` deve continuar funcionando exatamente como antes (já foi corrigida no change `fix-navigation-bar-views-list-empty`).
- **PageContext.new_session()**: Views que precisam criar sessões adicionais (ex: `oauth_callback_view` que chama `feed_list_view` internamente) devem continuar funcionando com `ctx.new_session()`.
- **State**: `state.active_feed_url` deve ser populado corretamente na rota `/feed/<url>` antes da view ser chamada.

## Review Notes

- **AMBIGUO**: `specs/route-handler-refactor/spec.md` → Scenario: Rota não encontrada na tabela (fallback) — não especifica se o fallback (`home_view`) requer ou não sessão de banco. O comportamento atual de `home_view` (linha 98-99 do `app.py`) cria `PageContext` sem `session`. A spec deve ser interpretada como "preservar o comportamento atual".
