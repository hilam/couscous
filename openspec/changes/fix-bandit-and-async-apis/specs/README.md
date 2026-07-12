# Specs — fix-bandit-and-async-apis

Esta mudança não introduz novas capacidades nem altera requisitos de capacidades existentes. Trata-se exclusivamente de:

- Correção de typos em comentários de supressão do bandit (`# noseq` → `# nosec`)
- Padronização de chamadas de API equivalentes (`page.launch_url` → `UrlLauncher`, `page.go` → `push_route`, `ensure_future` → `create_task`)

Nenhuma spec adicional é necessária. Consulte `proposal.md` e `design.md` para detalhes completos.
