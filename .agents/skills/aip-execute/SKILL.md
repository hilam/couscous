---
name: aip-execute
version: "0.2.0"
description: "Momento execute da entrega ativa — implementa tasks.md com TDD estrito (RED→GREEN→REFACTOR, commits atômicos), verifica a entrega, atualiza docs vivos e avança para history(Ei)."
disable-model-invocation: true
---

# aip-execute

Leia `.agents/skills/aip/REGRAS.md` (1× por sessão). Implementa `aip/<slug>/entregas/<id>/tasks.md` da entrega ativa `Ei` até `history(Ei)`.

## Princípios TDD

- **Testes verificam comportamento via seams** (fronteira pública: função, rota, exports). Nunca mock de colaborador interno nem teste de método privado. Valores esperados **literais e independentes**: `expect(soma(1,1)).toBe(2)`, nunca `toBe(1+1)`.
- **Fatias verticais (tracer bullets), não camadas horizontais.** Um teste → uma implementação → repita. Comece pelo happy path ponta a ponta, depois variante/edge.
- **Nunca implemente antes de ver o teste falhar.** **Nunca refatore no vermelho.**

## Git

Branch `feat/<slug>-<id>-<nome>`. Commits atômicos por ciclo, Conventional com scope `<id>`: `test(<id>): …` → `feat(<id>): …` → (só no verde) `refactor(<id>): …` → `style: …` · `docs(planejamento): entrega <id>`. Nunca misture teste+implementação no mesmo commit; `git log --oneline` deve mostrar o ciclo.

## Pré-condição

```bash
.agents/skills/aip/scripts/state.sh status              # esperado fase=execute nivel=entrega, plano=aprovado
```

Entrega alvo: a entrega ativa em `entrega=<id>` (ou próxima não-`concluida` do `PLANO-CICLO.md`). `tasks.md`, `qa-plan.md`, `specs/` presentes. Falta artefato? Volte `aip-plan`|`aip-decide`.

Antes de editar código ou fechar a entrega com `finish <id>`, confirme o registro da entrega ativa no estado:

```bash
.agents/skills/aip/scripts/state.sh advance execute <id>
```

## Ciclo por task

Para cada `- [ ] X.Y`, em ordem:

1. **Localize** o `### Test:` (e `[S1]` em `specs/<cap>/spec.md`, se precisar do `WHEN/THEN` normativo) — extraia só a seção: `sed -n '/### Test: <nome>/,/^###[^#]/p' aip/<slug>/entregas/<id>/qa-plan.md`. Confirme a seam antes de codar.
2. **RED** — primeira task da entrega: happy path ponta a ponta. Rode a suíte: **deve FALHAR**.
3. **GREEN** — o mínimo que passa e nada mais. Copy-paste aceitável na 1ª/2ª ocorrência; extraia na 3ª.
4. **Commit atômico** — `test(<id>): …` e `feat(<id>): …` separados.
5. **REFACTOR, só no verde** — suíte verde após cada mudança pequena.
6. Marque `- [x] X.Y` e rode a suíte completa.

Task ambígua → pause e pergunte; não alucine. Descobriu decisão nova no meio? Registre em `DECISOES.md` (linha nova) e avalie custo.

## Fim de entrega

Execute a suíte completa e o lint descobertos no repositório (ex.: `pytest && ruff check`, `cargo test`, `make test` ou validador próprio da entrega — nunca assuma uma stack fixa):

```bash
<comando de suíte completa + lint do repositório> 2>&1 | tail -n 30
```

Verde → reatualize os docs vivos afetados (`editor/AST.md`, `editor/API.md`, `CONTEXT.md`, etc.) se a entrega mudou estrutura ou contratos; gere `aip/<slug>/EXECUCAO/<id>/relatorio-verificacao.md` (template em `.agents/skills/aip-history/templates/`): cobertura vs qa-plan, evidências, gaps; execute `.agents/skills/aip/scripts/state.sh finish <id>` e avance para o fechamento da entrega:

```bash
.agents/skills/aip/scripts/state.sh finish <id>
.agents/skills/aip/scripts/state.sh advance history
```

E instrua: "Entrega `<id>` concluída. Invoque `aip-history` para fechar a entrega (`history(Ei)`)."
