---
name: aip-plan
version: "0.2.0"
description: "Momento plan em 2 níveis (Just-In-Time Planning): plan(Ciclo) gera PLANO-FULL e PLANO-CICLO; plan(Ei) detalha os 5 artefatos apenas da entrega ativa."
disable-model-invocation: true
---

# aip-plan

Leia `.agents/skills/aip/REGRAS.md` (1× por sessão). Opera em dois níveis conforme `nivel=` retornado por `.agents/skills/aip/scripts/state.sh status`:

## Pré-condição

`.agents/skills/aip/scripts/state.sh status` → esperado `fase=plan` (`nivel=ciclo` ou `nivel=entrega`). `EXPLORE.md` atualizado (ou replan definido).

## Modo A — `nivel=ciclo`: `plan(Ciclo)`

1. **PLANO-FULL** (só se não existir ou intenção mudou): template `.agents/skills/aip-plan/templates/PLANO-FULL.md`. Visão do projeto inteiro em ≤1 página.
2. **PLANO-CICLO**: template `.agents/skills/aip-plan/templates/PLANO-CICLO.md`. Do `EXPLORE.md`: objetivo do ciclo, entregas P/M (máx 5 dias úteis; sem G), dependências, entregável verificável, riscos. **Não** detalhe os artefatos de todas as entregas agora (Just-In-Time) e **não** liste `### Testes`.
3. **Estado (Modo Ciclo)** — após gate (`aprovo`|`confirmo`|`sim`) sobre `PLANO-CICLO.md`:

```bash
# iniciar diretamente o detalhamento da Entrega 1:
.agents/skills/aip/scripts/state.sh advance plan <01-entrega-id>
# ou, se PLANO-CICLO exigir sabatina prévia em nível de ciclo:
.agents/skills/aip/scripts/state.sh advance decide
```

## Modo B — `nivel=entrega`: `plan(Ei)`

Para a entrega ativa `entrega=<id>` (uma por vez, em ordem de dependência), crie `aip/<slug>/entregas/<id>/` com:

1. **proposal.md** — Porquê · O que muda · Capabilities (novas/modificadas) · Impacto com arquivos reais `file:line`. 1-2 páginas.
2. **specs/<cap>/spec.md** — fonte única normativa (`#### Scenario: [S1] <nome>` em `WHEN/THEN`).
3. **design.md** — obrigatório se houver decisão arquitetural; X vs Y com critério, Riscos→Mitigação, Plano de Migração, Questões Abertas.
4. **qa-plan.md** — um `### Test:` por `[S1]` + edge cases, com `**Traces**: entregas/<id>/specs/<cap>/spec.md → [S1] (Requirement: <nome>)` e `GIVEN`/seam/oráculo (sem duplicar `WHEN/THEN`).
5. **tasks.md** — `- [ ] X.Y` agrupados referenciando `[S1]`/`Test:`, `## 1. Configuração Git`, `## N. Validação Final`.

Formatos normativos: `.agents/skills/aip/REGRAS.md` → Rastreabilidade canônica. Entrega já parcialmente proposta? Complete o que falta, não recrie. Pacotes/ferramentas externos citados em `proposal`/`design` exigem verificação empírica prévia (ex.: `pip index versions`, `npm view` ou binário local) com disponibilidade registrada — nunca proponha pacote não verificado.

## Estado (Modo Entrega)

```bash
.agents/skills/aip/scripts/state.sh set-plano rascunho
.agents/skills/aip/scripts/state.sh advance decide
```

Gate: só avance com `aprovo`|`confirmo`|`sim` sobre o conjunto da entrega. Instrua: "Artefatos da entrega `<id>` em rascunho. Invoque `aip-decide` para sabatina e reconciliação."
