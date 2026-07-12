## Context

Mudança puramente sintática/cosmética em 6 arquivos. Nenhuma lógica de negócio, modelo de dados, dependência externa ou arquitetura é alterada. O proposal detalha o escopo completo.

## Goals / Non-Goals

**Goals:**
- `make security` passa limpo (exit 0)
- Todas as APIs assíncronas e de navegação seguem o padrão único do codebase
- Nenhuma mudança de comportamento em runtime

**Non-Goals:**
- Nenhuma alteração de lógica, modelo de dados, dependências, testes ou configuração de ferramentas

## Decisions

Cada substituição tem equivalência funcional direta:

| Padrão antigo | Novo padrão | Equivalência |
|---|---|---|
| `# noseq` | `# nosec` | Basta ler a doc do bandit: a diretiva correta é `nosec` |
| `page.launch_url(uri)` | `ft.UrlLauncher().launch_url(uri)` | `page.launch_url` é deprecated no Flet desde 2024; `UrlLauncher` é a API canônica |
| `page.go("/login")` | `page.push_route("/login")` | Ambos navegam para `/login`; `push_route` adiciona ao histórico (padrão usado nos outros 11 locais do codebase) |
| `asyncio.ensure_future(coro)` | `asyncio.create_task(coro)` | `ensure_future` é legado (Python 3.4); `create_task` é a API moderna desde 3.7, preferida para corrotinas |

Nenhuma alternativa foi considerada porque não há trade-off real — em cada caso uma API é estritamente superior (moderna, não deprecated, consistente com o resto do projeto).

## Risks / Trade-offs

Nenhum risco real. Mudanças são 100% sintáticas, sem alteração de fluxo runtime. Em caso de regressão, `git diff` mostra exatamente 6 arquivos com 1 linha cada — revertível em segundos.
