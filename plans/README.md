# Planos de Implementação

Gerados pela skill `/improve deep` em 2026-07-12, commit `c24a31f`.

Execute na ordem abaixo a menos que dependências digam o contrário. Cada executor: leia o plano completamente antes de começar, honre suas condições STOP, e atualize sua linha quando terminar.

## Ordem de execução & status

| Plano | Título | Prioridade | Esforço | Depende de | Status |
|-------|--------|------------|---------|------------|--------|
| 001 | Corrigir supressões do bandit e padronizar APIs assíncronas | P1 | P | — | TODO |
| 002 | Corrigir 12 testes de view quebrados | P1 | P | — | TODO |
| 003 | Testes unitários para feed_browser.py | P1 | M | — | TODO |
| 004 | Paralelizar refresh_all_feeds | P2 | P | — | TODO |
| 005 | Extrair _build_tree compartilhado | P2 | P | 003 (recomendado) | TODO |
| 006 | Extrair dialogs de category_list_view | P3 | M | 005 (recomendado) | TODO |
| 007 | Implementar purge de entries antigas | P2 | M | — | TODO |
| 008 | Adicionar toggle de tema claro/escuro | P3 | P | — | TODO |

Valores de status: TODO | IN PROGRESS | DONE | BLOCKED (com motivo) | REJECTED (com justificativa)

## Notas de dependência

- **001 e 002** são independentes e podem rodar em paralelo. Execute ambos primeiro — são quick wins que restauram a confiança nas verificações.
- **003** (feed_browser tests) não depende de 002, mas é recomendado rodar depois de 002 para ter `make test` 100% funcional como baseline.
- **005** depende de 003 porque a refatoração de `_build_tree` toca `feed_browser.py` — ter os testes de 003 como rede de segurança é ideal.
- **006** depende de 005 porque ambos tocam `category_list_view.py` — extrair `_build_tree` primeiro reduz o código a mover nos dialogs.
- **004, 007, 008** são independentes entre si e dos demais.

## Ordem recomendada de batch

```
Batch 1 (paralelizável): 001 + 002
Batch 2: 003 → 005 → 006
Batch 3 (paralelizável): 004 + 007 + 008
```

## Achados considerados e rejeitados

- **DEP-01 (starlette e msgpack como dependências mortas)**: não vale a pena fazer agora porque `starlette` é dependência transitiva do Flet (pode ser necessária em futuras versões) e `msgpack` é usada pelo `flet_web` internamente. Removê-las economiza 2 linhas no pyproject.toml mas pode causar surpresas em atualizações do Flet.
- **DIR-01 (README promete features não implementadas)**: o README é aspiracional e as features listadas (purge, backup, temas) são o roadmap. O plano 007 cobre purge e o 008 cobre temas. Backup criptografado fica para um sprint futuro.
- **TST-02 (cobertura de views 6-62%)**: não planejado como plano separado porque é um esforço G (vários dias). Os planos 002 e 003 cobrem as partes mais críticas (testes quebrados + lógica de domínio). Testar views Flet é inerentemente frágil (depende de mock pesado) e de menor ROI que testar services.
