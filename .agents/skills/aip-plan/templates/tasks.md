<!-- Preencha a estrutura; comentários não vão para o artefato final.
     Ciclo por task: RED → GREEN → commit atômico → REFACTOR (ver .agents/skills/aip/REGRAS.md). -->

> **Entrega:** `entregas/<id>/` — rastreia `entregas/<id>/qa-plan.md`, `entregas/<id>/specs/<cap>/spec.md` e `aip/<slug>/PLANO-CICLO.md`

## 1. Configuração Git e Planejamento

- [ ] 1.1 Criar branch `feat/<slug>-<id>-<nome>` — scope `<id>` nos commits
- [ ] 1.2 Commit dos artefatos de planejamento: `docs(planejamento): entrega <id> — <nome>`

## 2. Testes (RED → GREEN)

<!-- Tracer bullet: primeira task = happy path ponta a ponta. Um bloco por cenário do qa-plan. -->

- [ ] 2.1 Teste para `[S1]` — `<nome do teste>` (RED) (`Test: <nome do teste>`)
- [ ] 2.2 Implementação mínima para passar 2.1 (GREEN) (`Test: <nome do teste>`)
- [ ] 2.3 Commit: `test(<id>): <descrição>` → `feat(<id>): <descrição>`

## 3. Casos Limite e Robustez

<!-- Cenários EDGE do qa-plan.md -->

- [ ] 3.1 Teste para o caso limite `<nome>` (RED)
- [ ] 3.2 Implementar tratamento (GREEN)

## 4. Refatoração (apenas no GREEN)

- [ ] 4.1 Refatorar mantendo testes verdes
- [ ] 4.2 Suite completa · commit `refactor(<id>): …`

## 5. Validação Final

- [ ] 5.1 Lint e formatação (`make lint` / `npm run lint` / `ruff check`)
- [ ] 5.2 Suite completa uma última vez
- [ ] 5.3 Commit: `style: aplica lint e formatação`
