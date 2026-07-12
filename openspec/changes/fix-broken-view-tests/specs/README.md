# Specs — fix-broken-view-tests

Esta mudança não introduz novas capacidades nem altera requisitos de capacidades existentes. Trata-se exclusivamente de corrigir 12 testes de view que quebraram porque `PageContext` agora requer `session` e `_session_factory` (ADR-0003).

Nenhuma spec adicional é necessária. Consulte `proposal.md` e `design.md` para detalhes completos.
