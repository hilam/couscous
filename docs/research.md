# Research Session — 2026-06-22

Revisão do entendimento do projeto CousCous com grilling + domain-modeling.

## Participantes

- Hilam (usuário/dono do produto)
- agente opencode

## Domínio

- **Feed** é o organizador primário. O usuário pensa "quero ver o que tem de novo" primeiro.
- **Entry** é a unidade de consumo.
- **Category** = pasta hierárquica para **feeds** (já implementado).
- **Tag** = rótulo textual em **entries individuais** (a implementar).
- Offline-first, single-device. PostgreSQL local via Docker.

## Decisões alinhadas

| Área | Decisão |
|------|---------|
| **Offline/sync** | Single-device. Backup via Docker volume + JSON criptografado (futuro). |
| **Navegação** | Próximo/anterior dentro do mesmo feed. Ordem: published decrescente. Próximo = mais antigo. |
| **Tags** | Atribuição manual primeiro. Extração automática via SLM depois (pós-MVP). |
| **Busca** | Global tsvector + filtro local por texto na entry_list. |
| **Tema** | Global claro/escuro, alternância no AppBar. |
| **Copiar link** | Botão no entry_view e no ArticleCard. |
| **Purge** | Automático, configurável (dias/semanas/meses). Preserva entries importantes. Gatilho: ao iniciar e após refresh. |
| **Índices** | Entry: (feed, user_id, published DESC), (user_id, read), (link, user_id). Feed: (user_id). Category: (user_id). |
| **Paginação** | Scroll infinito, 50 entries por lote. |
| **Refresh** | Paralelo com semáforo de 5 conexões simultâneas. Timeout: 30s. |
| **Backup** | Docker volume (primário) + JSON criptografado (secundário, futuramente). |

## Artefatos criados

- `CONTEXT.md` — glossário do domínio
- `docs/adr/0001-postgresql-local-single-device.md` — decisão: PostgreSQL local via Docker
- `docs/adr/0002-entry-tags-not-feed-tags.md` — decisão: tags em entries, não em feeds
- `docs/research.md` — este sumário

## Sprint mental (PLANO.md)

Os sprints foram revisados e validados. Ordens de grandeza e prioridades mantidas.
