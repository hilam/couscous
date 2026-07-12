## 1. Git Setup e Planejamento

- [ ] 1.1 Criar branch de funcionalidade (`git checkout -b advisor/001-fix-bandit-and-async-apis`)
- [ ] 1.2 Fazer commit dos artefatos de planejamento gerados (`git add openspec/changes/fix-bandit-and-async-apis/ && git commit -m "docs(planning): gera artifacts da change fix-bandit-and-async-apis"`)

## 2. Correções — Bandit e APIs

- [ ] 2.1 Corrigir `# noseq B105` → `# nosec B105` em `app/services/oauth_service.py` (2 ocorrências: linhas 34 e 47)
- [ ] 2.2 Corrigir `# noseq B608` → `# nosec B608` em `app/services/search_service.py` (linha 57)
- [ ] 2.3 Fazer commit incremental das supressões (`git add app/services/oauth_service.py app/services/search_service.py && git commit -m "fix(bandit): corrige noseq para nosec nas supressoes"`)
- [ ] 2.4 Substituir `await page.launch_url(uri)` por `await ft.UrlLauncher().launch_url(uri)` em `app/controls/oauth_buttons.py`
- [ ] 2.5 Substituir `page.go("/login")` por `page.push_route("/login")` em `app/views/oauth_callback_view.py`
- [ ] 2.6 Substituir `asyncio.ensure_future(self.on_confirm(e))` por `asyncio.create_task(self.on_confirm(e))` em `app/controls/confirm_dialog.py`
- [ ] 2.7 Substituir `asyncio.ensure_future(self.on_submit(url, category_id))` por `asyncio.create_task(self.on_submit(url, category_id))` em `app/controls/add_feed_dialog.py`
- [ ] 2.8 Fazer commit incremental das APIs (`git add app/controls/ app/views/ && git commit -m "fix(api): padroniza chamadas async e navegacao"`)

## 3. Validação e Qualidade

- [ ] 3.1 Verificar `make security` — exit 0, sem issues
- [ ] 3.2 Verificar `make lint` — "All checks passed!"
- [ ] 3.3 Verificar `make typecheck` — "Success: no issues found"
- [ ] 3.4 Executar linting e formatação com Ruff (`ruff check --fix . && ruff format .`)
- [ ] 3.5 Se houver correções de estilo, commitar (`git add -A && git commit -m "style: aplica ruff e formata arquivos"`)
- [ ] 3.6 Verificação final com greps:
  - `grep -rn "noseq" app/` → vazio
  - `grep -rn "ensure_future" app/` → vazio
  - `grep -rn 'page\.go(' app/` → vazio
  - `grep -rn 'page\.launch_url' app/` → vazio
