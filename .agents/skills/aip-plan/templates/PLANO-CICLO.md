# Plano do Ciclo — <NN-slug>

> **Ciclo:** `aip/<slug>/` — rastreia `aip/PLANO-FULL.md` → ciclo NN
> **Base:** `EXPLORE.md` (problema, bordas, alternativas)

## Objetivo do ciclo

<1 frase verificável: o que estará provado/entregue no fim do ciclo>

> **Planejamento progressivo (*Just-In-Time*):** este documento organiza as entregas P/M do ciclo; apenas a Entrega 1 (ou entrega ativa) tem os 5 artefatos detalhados inicialmente (`plan(Ei)` sob demanda após `history(Ei-1)`).

## Entrega 1 — <Nome> (`01-<nome>`)

**Objetivo:** <1 frase verificável>

**Decisão arquitetural (se houver):** N/A — detalhada em `entregas/01-<nome>/design.md`

**Entregável:** <critério de aceite>. Todos os testes verdes.

**Riscos desta entrega (se houver):** N/A

---

## Entrega 2 — <Nome>

<mesmo bloco>

---

## Dependências

```
01-<nome> → 02-<nome> → 03-<nome>
```

Entregas paralelizáveis: <listar>

## Ciclo TDD por entrega

**Red** (teste mínimo que falha) → **Green** (implementação mais simples) → **Refactor** (limpar no verde). Testes rodam a cada commit.

## Estimativa

| Entrega | Esforço | Dias úteis |
|---|---|---|
| 1 — <Nome> | P | 1 |

**Total:** ~X para 1 dev. (P/M máx 5 dias úteis; sem G — épico é disfarce)

## Riscos do ciclo (opcional)

| Risco | Mitigação |
|---|---|

<!-- Testes e tarefas detalhadas vivem só em entregas/<id>/. PLANO-CICLO não duplica. -->
