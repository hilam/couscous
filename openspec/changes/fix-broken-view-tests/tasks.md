## 1. Git Setup

- [ ] 1.1 Criar branch de funcionalidade (`git checkout -b advisor/002-fix-broken-view-tests`)
- [ ] 1.2 Fazer commit dos artefatos de planejamento gerados (`git add openspec/changes/fix-broken-view-tests/ && git commit -m "docs(planning): gera artifacts da change fix-broken-view-tests"`)

## 2. Correção dos Testes

- [ ] 2.1 Adicionar fixture `page_context` em `tests/conftest.py` com `session` e `_session_factory` mockados
- [ ] 2.2 Atualizar `tests/test_about_view.py`: substituir `PageContext(page=page, state=state)` por fixture `page_context`; remover imports de `PageContext` e `State`
- [ ] 2.3 Atualizar `tests/test_home.py`: mesmo padrão — usar fixture `page_context`
- [ ] 2.4 Atualizar `tests/test_login_view.py`: mesmo padrão — usar fixture `page_context`; verificar se `page.overlay` precisa de mock extra
- [ ] 2.5 Atualizar `tests/test_register_view.py`: mesmo padrão — usar fixture `page_context`
- [ ] 2.6 Fazer commit incremental das correções (`git add tests/ && git commit -m "fix(tests): corrige 12 testes de view quebrados apos ADR-0003"`)

## 3. Validação

- [ ] 3.1 Verificar testes corrigidos: `uv run pytest tests/test_about_view.py tests/test_home.py tests/test_login_view.py tests/test_register_view.py -v` — 0 failed
- [ ] 3.2 Executar `make lint` — "All checks passed!"
- [ ] 3.3 Verificar que nenhum arquivo em `app/` foi modificado (`git diff --name-only main...HEAD | grep app/` → vazio)
- [ ] 3.4 Executar `make test` completo — 0 failed (ou pelo menos 12 falhas a menos que antes)
