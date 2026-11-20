---
name: aip-explore
version: "0.1.0"
description: Momento explore do ciclo — thinking partner sem código, uma pergunta por vez, até a descrição do problema cristalizar em EXPLORE.md.
disable-model-invocation: true
---

# aip-explore

Leia `.agents/skills/aip/REGRAS.md` (1× por sessão). Produz `aip/<slug>/EXPLORE.md`. **Regra de ouro: nenhuma linha de código, nenhum artefato de planejamento aqui.**

## Pré-condição

`.agents/skills/aip/scripts/state.sh status` → esperado `fase=explore slug=<slug>`. Fora disso, aborte e oriente `aip`.

## Stance (não é checklist cego)

- **Curioso, não prescritivo** — siga o que emerge; o ciclo anterior já deu o contexto.
- **UMA PERGUNTA POR VEZ** com recomendação e alternativas — Q2 depende de Q1.
- **Visual** — diagramas ASCII para fluxos, bordas e trade-offs.
- **Grounded** — leia `CONTEXT.md`, `README.md`, `aip/PLANO-FULL.md`, `aip/LICOES.md`, `editor/AST.md` se existirem; cite `file:line` em vez de perguntar o que a base já responde.
- **Contra o bajulador** — se você começar a concordar demais, volta: "quando concordo, não ajudo; meu melhor uso é challenge".

## Protocolo

1. Leia o estado e os artefatos do ciclo anterior (se houver): `HISTORY.md`, `DECISOES.md`, `LICOES.md` — o explore de um ciclo nasce dos replans do anterior.
2. Pergunte a intenção do ciclo ao usuário (1 frase dele é suficiente para começar).
3. Sabatine: suposições ocultas, linguagem vaga, bordas, casos que quebram. Elimine o "mais ou menos".
4. Alternativas: quando houver dúvida real, tabela X vs Y com critério — não escolha em silêncio, recomende.
5. Cristalização: quando usuário e você disserem "cristalizou", escreva `EXPLORE.md` (template `templates/EXPLORE.md`): problema em prosa, bordas, alternativas consideradas, o que fica FORA do ciclo, perguntas que ficam para o plan.

## Estado e próximo passo

```bash
.agents/skills/aip/scripts/state.sh advance context
# ou, se não houver termos/regras novos para context:
.agents/skills/aip/scripts/state.sh advance plan
```

Gate: só avance com `aprovo`|`confirmo`|`sim` do usuário sobre o EXPLORE.md gravado.
