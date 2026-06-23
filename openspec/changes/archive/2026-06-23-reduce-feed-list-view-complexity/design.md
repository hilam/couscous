## Context

A função `feed_list_view` em `app/views/feed_list_view.py` concentra múltiplos callbacks como closures internos: `refresh`, `on_feed_added`, `confirm_delete`, `delete_feed`, `open_add_dialog`. O callback `on_feed_added` é o maior deles (~20 statements) e contém lógica de negócio significativa: criação de feed, refresh individual, tratamento de erros com SnackBar e navegação pós-cadastro.

O padrão em outras views (ex: `category_list_view.py`) é extrair funções complexas para o escopo de módulo, mantendo a view function enxuta com closures curtos.

## Goals / Non-Goals

**Goals:**
- Reduzir `feed_list_view` abaixo de 50 statements para passar no `make lint`
- Extrair apenas `on_feed_added` — a maior fonte de statements
- Manter `confirm_delete` e `delete_feed` como closures (extraí-los criaria cascata desnecessária)
- Zero mudança de comportamento ou API

**Non-Goals:**
- Extrair todos os callbacks da view
- Refatorar outras views
- Alterar o limite PLR0915 globalmente

## Decisions

### Extrair `on_feed_added` como função de módulo `_handle_feed_added`

**Alternativa considerada:** Extrair `confirm_delete` + `delete_feed` em vez de `on_feed_added`.

**Decisão:** `on_feed_added` escolhido porque:
- É o maior contribuidor (20 statements vs 8 dos outros)
- A extração é mecânica: basta mover o corpo para uma função async com os parâmetros explícitos (`ctx`, `page`, `user_id`, `feed_list`, `confirm_delete_cb`)
- Os outros callbacks (`confirm_delete`/`delete_feed`) têm dependência circular entre si e com `_rebuild_feed_list`, exigindo refatoração mais profunda

**Forma da assinatura:**
```python
async def _handle_feed_added(
    url: str,
    category_id: int | None,
    ctx,
    page: ft.Page,
    user_id: int,
    feed_list: ft.ListView,
    confirm_delete_cb,
) -> None:
```

**Wrapper na view:**
```python
on_feed_added = lambda url, cid=None: asyncio.create_task(
    _handle_feed_added(url, cid, ctx, page, user_id, feed_list, confirm_delete)
)
```

Nota: `on_feed_added` é passado como callback para `AddFeedDialog`, que o chama como `on_feed_added(url, category_id)`. O wrapper mantém essa interface.

## Risks / Trade-offs

- **[Baixo] Assinatura com 7 parâmetros:** Aceitável por ser função privada de módulo, não API pública. Se o número de parâmetros crescer no futuro, considerar um dataclass de contexto.
- **[Baixo] Dupla manutenção:** Se `on_feed_added` precisar de nova dependência no futuro, alterar tanto a assinatura quanto o wrapper. Mitigação: o wrapper é trivial (1 linha), fácil de atualizar.
