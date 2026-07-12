## 1. Git Setup

- [ ] 1.1 Criar branch de funcionalidade (`git checkout -b advisor/004-parallel-refresh-all-feeds`)
- [ ] 1.2 Fazer commit dos artefatos de planejamento gerados (`git add openspec/changes/parallel-refresh-all-feeds/ && git commit -m "docs(planning): gera artifacts da change parallel-refresh-all-feeds"`)

## 2. Implementação

- [ ] 2.1 Refatorar `refresh_all_feeds` em `app/services/refresh_service.py`: substituir loop `for` por `asyncio.gather` com `Semaphore(5)`, adicionar `get_db_session()` do database module, cada feed com sessão própria
- [ ] 2.2 Adicionar import `from database.service.database import get_db_session` no topo do arquivo (se não existir)
- [ ] 2.3 Fazer commit incremental (`git add app/services/refresh_service.py && git commit -m "perf: paraleliza refresh_all_feeds com Semaphore(5)"`)

## 3. Validação

- [ ] 3.1 Verificar `make typecheck` — "Success: no issues found"
- [ ] 3.2 Verificar `uv run pytest tests/test_refresh_service.py -v` — 0 failed
- [ ] 3.3 Executar `make lint` — "All checks passed!"
- [ ] 3.4 Verificar loop antigo removido: `grep -n "for feed in feeds" app/services/refresh_service.py` → vazio
