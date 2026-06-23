## Context

O handler `on_route_change` em `app/app.py:34-106` contém 72 linhas com 8 branches if/elif. Cada branch que requer banco repete o mesmo padrão de 5+ linhas:

```python
async with get_db_session() as session:
    ctx = PageContext(
        page=page,
        state=state,
        session=session,
        _session_factory=get_db_session,
    )
    v = await <view_func>(ctx, ...)
```

Rotas sem banco (`/login`, `/register`, `/about`, fallback) repetem `ctx = PageContext(page=page, state=state, ...)` com pequenas variações. A extração de parâmetros de rota usa slicing inline (`route[len("/feed/"):]`, `int(route[len("/entry/"):])`).

O projeto já usa dataclasses (`PageContext`) e funções async como handlers de view. O padrão de views (uma função async por arquivo em `app/views/`) não é afetado por esta refatoração.

## Goals / Non-Goals

**Goals:**
- Reduzir o `on_route_change` para ~30 linhas, delegando a lógica para helpers privadas
- Eliminar a duplicação do boilerplate `PageContext(...)` + `async with get_db_session()`
- Tornar a adição de novas rotas uma operação de 1 linha (adicionar entrada na tabela)
- Preservar 100% do comportamento observável (rotas, views, navbar, autenticação, fallback)

**Non-Goals:**
- Alterar a assinatura ou comportamento de qualquer função de view
- Modificar `PageContext`, `State`, `get_db_session` ou `set_navbar`
- Extrair a lógica de roteamento para um novo arquivo/módulo (pode ser feito futuramente)
- Adicionar suporte a regex ou padrões complexos de rota (prefix-matching é suficiente)

## Decisions

**Decisão 1: Tabela de rotas como lista de dataclasses**

Cada rota é representada por uma instância de `_Route` com campos: `prefix` (padrão de prefixo), `handler` (função de view async), `requires_session` (bool), `is_public` (bool).

```python
@dataclass
class _Route:
    prefix: str
    handler: Callable[..., Awaitable[ft.View]]
    requires_session: bool
    is_public: bool = False
```

A busca percorre a lista em ordem e usa `route.startswith(prefix)` para rotas parametrizadas (prefixo termina com `/`) ou `route == prefix` para rotas exatas.

Alternativa considerada: dicionário `dict[str, ...]`. Rejeitada porque rotas parametrizadas (`/feed/<url>`, `/entry/<id>`) não podem ser chaves exatas de dicionário — exigiriam regex ou lógica adicional.

Alternativa considerada: tuplas `(prefix, handler, requires_session, is_public)`. Rejeitada por ser menos legível que dataclasses nomeadas, e o projeto já usa dataclasses em `PageContext`.

**Decisão 2: Extração de parâmetros inline no handler**

Apenas duas rotas têm parâmetros dinâmicos: `/feed/<url>` e `/entry/<id>`. A extração é feita com if/elif após o matching de rota, dentro da função auxiliar `_invoke_handler`:

```python
async def _invoke_handler(route_def, route, ctx):
    if route_def.prefix == "/feed/":
        ctx.state.active_feed_url = route[len("/feed/"):]
        return await route_def.handler(ctx)
    elif route_def.prefix == "/entry/":
        entry_id = int(route[len("/entry/"):])
        return await route_def.handler(ctx, entry_id)
    else:
        return await route_def.handler(ctx)
```

Alternativa considerada: callback `param_extractor` por rota. Rejeitada por overengineering — apenas 2 casos especiais não justificam infraestrutura adicional.

**Decisão 3: Sessão gerenciada com if/else no handler principal**

O `on_route_change` decide se abre ou não uma sessão de banco com base em `route_def.requires_session`. O bloco `async with get_db_session()` envolve apenas a chamada ao `_invoke_handler`:

```python
if route_def.requires_session:
    async with get_db_session() as session:
        ctx = PageContext(page=page, state=state, session=session, _session_factory=get_db_session)
        v = await _invoke_handler(route_def, route, ctx)
else:
    ctx = PageContext(page=page, state=state, _session_factory=get_db_session)
    v = await _invoke_handler(route_def, route, ctx)
```

Alternativa considerada: async context manager genérico que aceita um booleano. Rejeitada por obscurecer o ciclo de vida da sessão — manter o `async with` explícito deixa claro quando a sessão é aberta e fechada.

**Decisão 4: Guarda de autenticação unificada**

A lógica de autenticação (redirecionar para `/login` se usuário não autenticado em rota não-pública) é aplicada antes do despacho:

```python
matched = _match_route(route)
if matched is None:
    matched = _FALLBACK_ROUTE
if route == "/login" or (not state.user and not matched.is_public):
    ctx = PageContext(page=page, state=state, _session_factory=get_db_session)
    v = await login_view(ctx)
else:
    v = await _build_and_invoke(matched, route, page, state)
```

Alternativa considerada: verificação de auth dentro de cada view. Rejeitada — a verificação centralizada é mais segura (não depende de cada view implementar corretamente) e já é o padrão atual.

**Decisão 5: Helpers como funções privadas no próprio app.py**

As funções `_match_route`, `_build_and_invoke`, `_invoke_handler` e a dataclass `_Route` ficam como membros privados do módulo `app/app.py`.

Alternativa considerada: extrair para `app/routing.py`. Rejeitada para manter o escopo da refatoração contido. Se a lógica de roteamento crescer no futuro, a extração para um módulo separado é natural.

## Risks / Trade-offs

- **Ordem da tabela de rotas é significativa** → Rotas mais específicas (ex: `/feed/` com prefixo) devem aparecer ANTES de rotas mais genéricas (ex: `/`). Mitigação: documentar no comentário da tabela e validar com testes. Se `/` viesse antes de `/feed/`, a rota `/feed/...` casaria com `/` erroneamente.
- **Duas rotas compartilham handler** → `/` e `/feeds` usam `feed_list_view`. Isso é intencional e reflete o comportamento atual. Mitigação: documentado na definição da tabela.
- **Regressão silenciosa** → Como é uma refatoração pura, bugs podem não ser óbvios visualmente. Mitigação: QA plan cobre todas as rotas e cenários de autenticação; testes automatizados existentes devem continuar passando.
