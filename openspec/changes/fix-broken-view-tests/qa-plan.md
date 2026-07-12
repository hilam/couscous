## Capability: dotestes (correção de testes de view)

Esta mudança não altera comportamento de runtime — não há specs com cenários GIVEN/WHEN/THEN. A validação é: os testes que estavam quebrados agora passam.

### Test: CRITICAL - test_about_view passa
**Traces**: não se aplica (mudança em testes sem spec)
- **GIVEN** a fixture `page_context` com session mockada
- **WHEN** executa-se `uv run pytest tests/test_about_view.py -v`
- **THEN** os 2 testes passam (0 failed)

### Test: CRITICAL - test_home passa
**Traces**: não se aplica
- **GIVEN** a fixture `page_context` com session mockada
- **WHEN** executa-se `uv run pytest tests/test_home.py -v`
- **THEN** os 3 testes passam (0 failed)

### Test: CRITICAL - test_login_view passa
**Traces**: não se aplica
- **GIVEN** a fixture `page_context` com session mockada
- **WHEN** executa-se `uv run pytest tests/test_login_view.py -v`
- **THEN** todos os testes passam (0 failed)

### Test: CRITICAL - test_register_view passa
**Traces**: não se aplica
- **GIVEN** a fixture `page_context` com session mockada
- **WHEN** executa-se `uv run pytest tests/test_register_view.py -v`
- **THEN** todos os testes passam (0 failed)

### Test: CRITICAL - make lint passa
**Traces**: não se aplica
- **GIVEN** os arquivos de teste modificados
- **WHEN** executa-se `make lint`
- **THEN** o output contém "All checks passed!"

### Test: EDGE - nenhum arquivo app/ foi modificado
**Traces**: não se aplica
- **GIVEN** o repositório após as alterações
- **WHEN** executa-se `git diff --name-only main...HEAD`
- **THEN** apenas arquivos em `tests/` aparecem

## Edge Cases

- **Teste que chama `ctx.open_session()` no callback**: Se algum teste de login ou register acionar o submit (que abre sessão), o `AsyncMock` de `session` precisa ter `__aenter__` e `__aexit__` configurados.

## Integration Points

Nenhum — mudança isolada em 5 arquivos de teste, sem acoplamento entre si.

## Review Notes

Nenhuma ambiguidade ou cenário não-testável identificado. A mudança é verificável executando os próprios testes corrigidos.
