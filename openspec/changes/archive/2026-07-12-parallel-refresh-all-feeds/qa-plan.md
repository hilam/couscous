## Capability: dorefresh (refresh paralelo de feeds)

Mudança apenas em implementação — sem spec scenarios. Validação via typecheck, testes existentes e lint.

### Test: CRITICAL - typecheck passa
**Traces**: não se aplica
- **GIVEN** o código refatorado com `asyncio.gather`, `Semaphore` e `get_db_session`
- **WHEN** executa-se `make typecheck`
- **THEN** o output contém "Success: no issues found"

### Test: CRITICAL - testes de refresh passam
**Traces**: não se aplica
- **GIVEN** o MockTransport do httpx (respostas instantâneas)
- **WHEN** executa-se `uv run pytest tests/test_refresh_service.py -v`
- **THEN** todos os testes passam (0 failed)

### Test: make lint passa
**Traces**: não se aplica
- **GIVEN** o código refatorado
- **WHEN** executa-se `make lint`
- **THEN** o output contém "All checks passed!"

### Test: EDGE - loop sequencial antigo não existe mais
**Traces**: não se aplica
- **GIVEN** o arquivo `app/services/refresh_service.py`
- **WHEN** executa-se `grep -n "for feed in feeds" app/services/refresh_service.py`
- **THEN** nenhum match (loop substituído por gather)

## Edge Cases

- Lista de feeds vazia: `refresh_all_feeds` deve retornar imediatamente sem erro
- `get_db_session()` sob concorrência: cada chamada cria nova sessão, sem estado compartilhado

## Integration Points

Nenhum — a API pública não muda. Views que chamam `refresh_all_feeds(s, user_id)` continuam funcionando sem alteração.

## Review Notes

Nenhuma ambiguidade.
