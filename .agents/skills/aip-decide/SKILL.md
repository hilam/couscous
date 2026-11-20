---
name: aip-decide
version: "0.2.0"
description: "Momento decide — sabatina a entrega ativa Ei (ou PLANO-CICLO se nivel=ciclo) uma pergunta por vez, aplica cada decisão aprovada imediatamente nos artefatos e fecha o plano com gate."
disable-model-invocation: true
---

# aip-decide — sabatina enxuta e edição imediata

Leia `.agents/skills/aip/REGRAS.md` (1× por sessão). `.agents/skills/aip/scripts/state.sh status` → esperado `fase=decide`.

## Princípios

- **UMA PERGUNTA POR VEZ** — Q2 depende de Q1; perguntas paralelas destroem a ordem.
- **RECOMENDE UMA RESPOSTA** com justificativa de 1 frase; o usuário confirma, substitui ou redireciona.
- **BASE ANTES DA PERGUNTA** — se `CONTEXT.md`, `EXPLORE.md` ou o código já respondem, cite `file:line` em vez de perguntar.
- **EDIÇÃO IMEDIATA POR DECISÃO** — ao receber `aprovo`|`confirmo`|`sim` numa pergunta material, aplique logo a mudança nos artefatos tocados (cascata local da entrega) e na linha de `DECISOES.md`, antes de passar à próxima pergunta ou acumular lote no fim.
- **PARE QUANDO** todo ramo material da entrega estiver resolvido ou delegado à implementação, o usuário pedir, ou a próxima pergunta não mudar materialmente o artefato.
- **Gate** — nenhuma edição sem `aprovo`|`confirmo`|`sim`. Rejeitada → arquivo como está.

## Fase 1 — Sabatina

1. **Alvo.** Se `nivel=entrega`: apenas `aip/<slug>/entregas/<id>/` + vínculo com `PLANO-CICLO.md`. Se `nivel=ciclo`: apenas `PLANO-CICLO.md` e `PLANO-FULL.md`.
2. **Mapa privado** das decisões em aberto, em ordem de dependência. Não mostre; pergunte.
3. Formato de pergunta:

```
**Q1:** <pergunta precisa>.

**Recomendação:** <sua escolha>, porque <uma frase>.

**Alternativas:**
- **A:** <nome> — <quando faz sentido>
- **B:** <nome> — <quando faz sentido>
```

4. **Gatilhos de revisão.** PLANO-CICLO: entregas P/M reais? dependências existem? entregável verificável? Entrega: todo requirement tem `#### Scenario: [S1]` em `WHEN/THEN` com `SHALL/MUST`? `qa-plan.md` referencia `[S1]` sem duplicar `WHEN/THEN`? edge cases substanciais? design com X vs Y? tasks cobrem `[S1]`/`Test:`?
5. **Escalamento Goldfish.** Ao fechar cada ramo material, classifique: barata (fecha aqui) / cara (arquitetura, API, dados, segurança) → proponha sessão nova lendo só o artefato, registre aceite/recusa do usuário.

## Fase 2 — Fechamento em `DECISOES.md` e Estado

1. Garanta `DECISOES.md` atualizado (template `.agents/skills/aip-decide/templates/DECISOES.md`): tabela `Decisão | Resolução | Impacta | Custo (barata|cara|goldfish)`. Decisão de ferramenta/pacote externo só fecha após verificação empírica de nome e disponibilidade (`pip index versions` ou equivalente) registrada na linha da decisão.
2. Conferência final da cascata de coerência na entrega ativa (`proposal ↔ spec ↔ design ↔ qa-plan ↔ tasks`). Entrega nova → `TODO: aip-plan`.
3. Só com gate explícito sobre o conjunto final:

```bash
# se nivel=entrega:
.agents/skills/aip/scripts/state.sh set-plano aprovado
.agents/skills/aip/scripts/state.sh advance execute

# se nivel=ciclo (para abrir ou revisar plan):
.agents/skills/aip/scripts/state.sh advance plan <01-entrega-id>
```

Se plano precisar de re-geração substancial na entrega: `.agents/skills/aip/scripts/state.sh advance plan`.
