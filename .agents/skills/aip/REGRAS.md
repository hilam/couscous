# REGRAS AIP — invariantes compartilhados

Leia **1× por sessão**. Cada `SKILL.md` traz só o delta do seu momento; o que vale para todas está aqui. Teoria em `../../../draft/PROCESSO-AIP.md`.

## Estado (cópia única do script)

`.agents/skills/aip/scripts/state.sh` — sempre invocado a partir da raiz do projeto (CWD), onde o bash roda (não do diretório da skill).

- `status` responde "onde estou / o que vem agora" (`ciclo`, `slug`, `fase`, `nivel`, `plano`, `entrega`, `next=`). **Nunca** faça `cat aip/.state.json`.
- `advance <fase> [id]` valida a transição em 2 níveis (`ciclo` e `entrega`) — o fluxo é `explore(opc) → context(opc) → plan(ciclo) → [plan(Ei) → decide(Ei) → execute(Ei) → history(Ei)]×N → history(ciclo) → próximo ciclo`.
  - Em `plan(ciclo)` ou `history(entrega)`, `advance plan <entrega-id>` entra em `plan(entrega)` para `<entrega-id>`.
  - Em `execute(entrega)`, `advance execute <entrega-id>` registra a entrega ativa; `advance history` vai para `history(entrega)`.
  - Em `history(entrega)`, `advance history` promove para `history(ciclo)`; `--force` só para correção manual pedida pelo usuário. **Não existe estado terminal**.
- `finish <entrega-id>` marca entrega concluída. `set-plano rascunho|aprovado` só em `plan`/`decide` (`aprovado` só em `decide`, após gate).
- Skills são invocadas explicitamente pelo usuário por seu nome canônico (`aip-*`; o prefixo `/` ou `@` depende do *harness*); nenhuma se auto-carrega.

## Layout

```
aip/
  .state.json                    # estado — só via state.sh
  PLANO-FULL.md                  # visão de projeto (único, vivo)
  LICOES.md                      # append-only, projeto inteiro
  <ciclo-slug>/                   # ex: 01-fundacao-mvp
    EXPLORE.md  PLANO-CICLO.md  DECISOES.md  HISTORY.md
    entregas/<id>/                # id = NN-nome-kebab
      proposal.md  design.md  qa-plan.md  tasks.md
      specs/<cap>/spec.md        # plural — um por capability
    EXECUCAO/<id>/relatorio-verificacao.md
```

Docs vivos do projeto ficam **fora** de `aip/`: `AGENTS.md`, `CONTEXT.md`, `README.md` na raiz; `DESIGN.md`, `DATA.md`, `API.md`, `AST.md` em `editor/`. `aip/<ciclo>/` congela no fim do ciclo (é diário); os docs vivos não. Atenção à caixa: `DESIGN.md` maiúsculo é o doc vivo do produto; `design.md` minúsculo é artefato de entrega em `entregas/<id>/`.

## Gate humano

Nunca avance de momento nem grave decisão sem o usuário digitar `aprovo` | `confirmo` | `sim` (ou equivalente claro). Skills de planejamento (`aip-plan`, `aip-decide`, `aip-context`) nunca editam código de `editor/frontend` ou `editor/backend`. `aip-decide` sabatina **e** aplica as edições imediatamente após cada decisão aprovada na mesma sessão — cada alteração passa pelo gate.

## Rastreabilidade canônica (fonte única por ID, sem duplicar)

`PLANO-FULL → PLANO-CICLO → proposal.md → specs/<cap>/spec.md ([S1] WHEN/THEN) → qa-plan.md (**Traces** + [S1] + GIVEN/seam/oráculo) → tasks.md (- [ ] X.Y + [S1])`

- **PLANO-CICLO** organiza o fatiamento (*Just-In-Time Planning*): entregas P/M (máx 5 dias úteis), sem G — épico é disfarce. **Não** liste `### Testes` nem `### Implementação` no plano; os artefatos detalhados de cada entrega nascem sob demanda em `plan(Ei)`.
- **spec.md** (fonte única normativa): `## ADDED|MODIFIED|REMOVED Requirements` + `### Requirement:` com `SHALL/MUST` + `#### Scenario: [S1] <nome>` (4 `#`) em `WHEN/THEN`. Cada requirement ≥1 scenario.
- **qa-plan.md**: um `### Test:` por `[S1]` + edge cases, cada um com `**Traces**: entregas/<id>/specs/<cap>/spec.md → [S1] (Requirement: <nome>)`, marca `CRITICAL`/`EDGE` e `GIVEN`/seam/oráculo — **não** repita `WHEN/THEN`.
- **design.md**: obrigatório por entrega com decisão arquitetural — Decisions (X vs Y com critério), Risks→Mitigação, Migration Plan (mesmo que N/A), Open Questions.
- **tasks.md**: `- [ ] X.Y` por fase, cada task referenciando o ID `[S1]` / `Test:` do qa-plan sem duplicar prosa do cenário.

## Disciplina de contexto

- Extraia só a seção que precisa: `sed -n '/### Test: <nome>/,/^###[^#]/p' <arquivo>`. Não leia artefato inteiro quando uma seção basta.
- Não releia o que acabou de escrever; não re-liste diretório já conhecido.
- Templates: `.agents/skills/aip-plan/templates/*.md`, `.agents/skills/aip-history/templates/*.md`. Preencha a estrutura — comentários de instrução **não** vão para o artefato final.
- Escreva sempre em caminho concreto (glob já expandido), nunca em padrão glob.
- Suite poliglota: `npm test` / `pytest` / `cargo test` / `make test` — descubra pelo repositório, não assuma.

## Sandbox e segredo

Modelos abertos/locais primeiro; nada sensível sai da máquina. Segredos nunca entram em artefato nem no git (`.env`, chaves). Dado de terceiros (dados de leitores, manuscritos de exemplo com nomes reais) só com permissão explícita no gate. Se uma decisão exige serviço externo, registre em `DECISOES.md` com justificativa e alternativa local descartada.

## Goldfish como escalamento

Autor==crítico na mesma sessão é o default (economia de contexto). Escale para Goldfish real (sessão nova, sem memória, lendo só o artefato) quando a decisão for cara: arquitetura, contrato de API, modelo de dados, segurança. O `aip-decide` propõe o escalamento; o humano decide se vale o custo.
