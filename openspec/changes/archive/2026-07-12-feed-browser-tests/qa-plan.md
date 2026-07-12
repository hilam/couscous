## Capability: dotestes (cobertura de feed_browser)

Esta mudança adiciona testes — a validação é executar os próprios testes e medir cobertura.

### Test: CRITICAL - Todos os testes de feed_browser passam
**Traces**: não se aplica (sem spec)
- **GIVEN** a fixture `db_session` com PostgreSQL rodando
- **WHEN** executa-se `uv run pytest tests/test_feed_browser.py -v`
- **THEN** todos os testes passam (mínimo 11, 0 failed)

### Test: CRITICAL - Cobertura >80% em feed_browser.py
**Traces**: não se aplica
- **GIVEN** o módulo `app/services/feed_browser.py`
- **WHEN** executa-se `uv run pytest tests/test_feed_browser.py --cov=app.services.feed_browser --cov-report=term-missing`
- **THEN** a cobertura reportada é >80%

### Test: make lint passa
**Traces**: não se aplica
- **GIVEN** o arquivo de teste criado
- **WHEN** executa-se `make lint`
- **THEN** o output contém "All checks passed!"

### Test: EDGE - Nenhum arquivo app/ foi modificado
**Traces**: não se aplica
- **GIVEN** o repositório após as alterações
- **WHEN** executa-se `git diff --name-only main...HEAD`
- **THEN** apenas `tests/test_feed_browser.py` aparece

## Edge Cases

Testes de `search()` podem falhar se a coluna `search_vector` não existir no banco de teste — depende da fixture `db_session` que a cria via `_add_search_vector_column()`.

## Integration Points

Nenhum — mudança isolada em 1 arquivo de teste.

## Review Notes

Nenhuma ambiguidade identificada. O comportamento esperado de cada função está documentado no feed_browser.py e nos nomes dos testes.
