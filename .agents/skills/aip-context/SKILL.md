---
name: aip-context
version: "0.1.0"
description: Momento context do ciclo — mantém viva a base do elefante. CONTEXT.md (glossário/linguagem ubíqua), AGENTS.md e editor/AST.md (memória do código).
disable-model-invocation: true
---

# aip-context

Leia `.agents/skills/aip/REGRAS.md` (1× por sessão). Atualiza os docs vivos do projeto com o que o explore revelou. Não cria plano, não toca código.

## Pré-condição

`.agents/skills/aip/scripts/state.sh status` → esperado `fase=context`. `EXPLORE.md` do ciclo deve existir.

## O que atualizar (e por quê)

| Arquivo | quando mexer |
|---|---|
| `CONTEXT.md` | todo termo novo do domínio (AIP, produto, livro) entra com definição e origem; termos vagos que o explore matou saem ou são corrigidos |
| `AGENTS.md` | só regra de engajamento nova (sandbox, segredo, convenção) — mudanças aqui são caras, proponha e passe pelo gate |
| `README.md` | se a intenção do produto mudou: requisito novo/removido, com link para o EXPLORE que originou |
| `editor/AST.md` | mapa do código existente: se o ciclo anterior gerou código novo, registre (estrutura por pasta → 1 linha por arquivo); se não existe código, crie só o esqueleto com o que o EXPLORE garante |

## Protocolo

1. Liste os termos e decisões novos extraídos do `EXPLORE.md`.
2. Proponha as edições, arquivo por arquivo, em diffs claros (linha nova, linha removida com motivo).
3. Gate: escreva só após `aprovo`|`confirmo`|`sim` por arquivo.
4. **Goldfish-lite** (opcional, recomendado no ciclo 1): peça uma sessão nova que leia `CONTEXT.md`+`AST.md` e resuma o projeto; corrija a base pelo que ela entendeu errado. Custo/benefício registrado em DECISOES se pular.

## Estado e próximo passo

```bash
.agents/skills/aip/scripts/state.sh advance plan
```

Instrua: "Base atualizada. Invoque `aip-plan` para estruturar o ciclo."
