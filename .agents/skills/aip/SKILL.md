---
name: aip
version: "0.1.0"
description: Orquestradora do fluxo AIP — diz em que ciclo/etapa o projeto está e qual skill invocar a seguir. Use quando o usuário quiser iniciar, retomar ou entender o estado do processo.
---

# aip — orquestradora

Leia `.agents/skills/aip/REGRAS.md` (1× por sessão). Você não executa etapas — posiciona e encaminha.

## Sem estado — iniciar ciclo 1

1. `.agents/skills/aip/scripts/state.sh status` → erro de estado ausente: inicie.
2. Pergunte o nome do ciclo (ex: `01-fundacao-mvp`). Formato `NN-nome-kebab`.
3. Confirme: "Vou criar `aip/<slug>/` — confirma? [s/n]".
4. `.agents/skills/aip/scripts/state.sh init <slug>` e mande o usuário invocar `aip-explore`.

## Com estado — retomar

1. `.agents/skills/aip/scripts/state.sh status` → `ciclo`, `slug`, `fase`, `nivel`, `plano`, `entrega`, `next=`.
2. Pergunte retomar ou reiniciar. Retomando: mostre a linha `next=` (e `nivel=` quando relevante) e mande invocar aquela skill.
3. Não narre o fluxo em prosa — as transições já são validadas pelo script.

## Fechando e abrindo ciclos

- Em `fase=history` (`nivel=entrega`), `aip-history` fecha a entrega e avança para `plan <proxima-entrega>` ou promove para `history` (`nivel=ciclo`).
- Em `fase=history` (`nivel=ciclo`), o `next=` é `aip-history`; ao terminar, o script abre o próximo ciclo com `advance <explore|context|plan> <novo-slug>`. Não há `concluido`: o círculo é o design.

## Falhas

- `jq` ausente → aborte, passe o comando de instalação e só execute se o usuário aprovar.
- `transição ilegal` → mostre `status` e o erro; correção manual (`advance --force <fase>`) só a pedido explícito.
- Fase certa mas ciclo/entrega errada → confirme o id com o usuário antes do `advance`.
