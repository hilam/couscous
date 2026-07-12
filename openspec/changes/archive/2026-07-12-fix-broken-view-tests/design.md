## Context

12 testes de view falham porque `PageContext` agora requer `session` e `_session_factory` (desde ADR-0003), mas os testes foram escritos antes dessa mudança e constroem `PageContext(page=page, state=state)` sem esses parâmetros. A correção é puramente nos testes — o runtime não é afetado.

## Goals / Non-Goals

**Goals:**
- `uv run pytest tests/test_about_view.py tests/test_home.py tests/test_login_view.py tests/test_register_view.py -v` → 0 failed
- Criar fixture `page_context` reutilizável em `conftest.py` para evitar repetição futura

**Non-Goals:**
- Nenhuma alteração na classe `PageContext` ou em qualquer arquivo de `app/`
- Nenhuma alteração em outros testes que já passam

## Decisions

| Decisão | Alternativa | Por quê |
|---------|-------------|---------|
| Fixture centralizada em `conftest.py` | Repetir mock em cada arquivo de teste | DRY — se `PageContext` mudar de novo, só um lugar precisa ser atualizado |
| `AsyncMock` para `session` | `MagicMock` puro | `session` é async context manager (usado em `ctx.open_session()`), precisa de suporte a `__aenter__`/`__aexit__` |
| `MagicMock` para `page` e `session_factory` | `AsyncMock` | Nenhum dos dois é usado como async context manager nos testes atuais |

## Risks / Trade-offs

- **Risco**: Algum teste pode chamar `ctx.open_session()` no callback submit, exigindo mock de `__aenter__`/`__aexit__` no `session`. → Mitigação: se ocorrer, adicionar `session.__aenter__.return_value = session` na fixture.
- **Risco**: A fixture em conftest.py pode conflitar com fixtures existentes. → Mitigação: nome `page_context` é único e descritivo.
