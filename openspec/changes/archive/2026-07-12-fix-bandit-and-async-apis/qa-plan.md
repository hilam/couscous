## Capability: dotooling (segurança, lint, types)

Esta mudança não altera comportamento de runtime — não há specs com cenários GIVEN/WHEN/THEN. A validação é puramente por ferramentas estáticas e greps.

### Test: CRITICAL - bandit passa limpo
**Traces**: não se aplica (mudança sintática sem spec)
- **GIVEN** os arquivos modificados com `# nosec` corrigido
- **WHEN** executa-se `make security`
- **THEN** o exit code é 0 e o output não contém `>> Issue:`

### Test: CRITICAL - lint passa
**Traces**: não se aplica
- **GIVEN** os arquivos modificados
- **WHEN** executa-se `make lint`
- **THEN** o output contém "All checks passed!"

### Test: CRITICAL - typecheck passa
**Traces**: não se aplica
- **GIVEN** os arquivos modificados
- **WHEN** executa-se `make typecheck`
- **THEN** o output contém "Success: no issues found"

### Test: CRITICAL - nenhum `noseq` residual
**Traces**: não se aplica
- **GIVEN** todos os arquivos em `app/`
- **WHEN** executa-se `grep -rn "noseq" app/`
- **THEN** nenhum match é encontrado

### Test: CRITICAL - nenhum `ensure_future` residual
**Traces**: não se aplica
- **GIVEN** todos os arquivos em `app/`
- **WHEN** executa-se `grep -rn "ensure_future" app/`
- **THEN** nenhum match é encontrado

### Test: CRITICAL - nenhum `page.go(` residual
**Traces**: não se aplica
- **GIVEN** todos os arquivos em `app/`
- **WHEN** executa-se `grep -rn 'page\.go(' app/`
- **THEN** nenhum match é encontrado

### Test: CRITICAL - nenhum `page.launch_url` residual
**Traces**: não se aplica
- **GIVEN** todos os arquivos em `app/`
- **WHEN** executa-se `grep -rn 'page\.launch_url' app/`
- **THEN** nenhum match é encontrado

### Test: EDGE - apenas os 6 arquivos do escopo foram modificados
**Traces**: não se aplica
- **GIVEN** o estado do repositório após as alterações
- **WHEN** executa-se `git diff --name-only`
- **THEN** apenas arquivos da lista de escopo aparecem

## Edge Cases

Nenhum — mudança puramente sintática sem branches condicionais, dados de entrada, ou estados alternativos. Cada substituição é um find-and-replace determinístico.

## Integration Points

Nenhum — as mudanças são 6 substituições isoladas em 6 arquivos, sem acoplamento entre si.

## Review Notes

Nenhuma ambiguidade ou cenário não-testável identificado. A mudança é 100% verificável por ferramentas automatizadas (make targets e grep).
