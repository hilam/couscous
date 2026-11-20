---
name: aip-history
version: "0.2.0"
description: "Momento history em 2 níveis: history(Ei) fecha a entrega e avança para plan(Ei+1) ou history(Ciclo); history(Ciclo) fecha o círculo com HISTORY.md, LICOES.md, replan e improve."
disable-model-invocation: true
---

# aip-history

Leia `.agents/skills/aip/REGRAS.md` (1× por sessão). É o momento em que o processo aprende — código não basta; o que se aprende vira documento, e o que se aprendeu sobre o processo vira skill. **Não bloqueie**: apresenta, o humano decide.

## Pré-condição

`.agents/skills/aip/scripts/state.sh status` → esperado `fase=history` (`nivel=entrega` ou `nivel=ciclo`).

---

## Modo A — `nivel=entrega`: `history(Ei)`

1. **Verify da entrega:** confirme suíte + lint verdes, cobertura vs `qa-plan.md`, `EXECUCAO/<id>/relatorio-verificacao.md` completo e docs vivos sincronizados.
2. **Learn / Improve rápido (se houver):** se a entrega revelou uma lição urgente de processo ou arquitetura, proponha registro rápido em `aip/LICOES.md` (ou ajuste de skill/REGRAS com gate e commit antes de prosseguir).
3. **Próximo passo (com gate explícito):**
   - Ainda há entrega pendente no `PLANO-CICLO.md` → avance para o planejamento JIT da próxima entrega:
     ```bash
     .agents/skills/aip/scripts/state.sh advance plan <NN-proxima-entrega>
     ```
     Instrua: "Entrega `<id>` fechada. Invoque `aip-plan` para detalhar `<NN-proxima-entrega>`."
   - Todas as entregas do ciclo terminaram → promova para `history(Ciclo)`:
     ```bash
     .agents/skills/aip/scripts/state.sh advance history
     ```
     E execute o **Modo B** abaixo (ou instrua invocar `aip-history` no nível ciclo).

---

## Modo B — `nivel=ciclo`: `history(Ciclo)`

### 1. Verify (nível ciclo)
- Suíte completa + lint, uma vez, com saída registrada.
- Para cada `### Test:` de cada `qa-plan.md` do ciclo: o teste existe e passou? (liste nomes com `grep -n '^### Test:'`, extraia bloco a bloco.)
- Docs vivos batem com o código? `editor/AST.md`, `DESIGN.md`/`API.md`/`DATA.md` sem contradição com a realidade.
- Criticidade: **alta** = `CRITICAL` falhou ou suíte vermelha · **média** = `EDGE` falhou ou gaps de cobertura · **baixa** = estilo.

### 2. Learn
Escreva `aip/<slug>/HISTORY.md` (template `.agents/skills/aip-history/templates/HISTORY.md`): o que o ciclo provou, o que doeu, o que o plano errou. Acrescente **uma seção** ao final de `aip/LICOES.md` (append-only; nunca sobrescreva).

### 3. Replan
- Revise `aip/PLANO-FULL.md`: sequência de ciclos ainda faz sentido? Intenção mudou? (mudança de intenção → gate novo.)
- Escreva as **candidatas ao próximo ciclo** em `HISTORY.md` (≥2, com critério) — viram a semente do `aip-explore` seguinte.

### 4. Improve (o círculo explícito)
- Alguma lição é sobre o **processo** (skill confusa, gate faltando, REGRAS ambígua)? Proponha o delta concreto na skill/template/REGRAS, com bump de `version` na skill afetada.
- Gate: nada muda sem `aprovo`. Aprovado o delta, **edite efetivamente os arquivos das skills/templates/REGRAS e faça o commit dessas alterações** antes de avançar para o próximo ciclo. Provas do aprendizado: linha em `LICOES.md` apontando a skill e a versão.

### 5. Fecha ciclo, abre o próximo

```bash
.agents/skills/aip/scripts/state.sh advance explore <NN-proximo-ciclo>
# ou, se explore/context forem dispensados no novo ciclo:
.agents/skills/aip/scripts/state.sh advance plan <NN-proximo-ciclo>
```

Gate: só com decisão explícita do usuário (próximo ciclo agora, ou pausa com ciclo congelado — `aip/<slug>/` é diário, não se mexe mais). Mostre `HISTORY.md` resumido e o `next=` devolvido.
