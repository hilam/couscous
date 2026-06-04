## Context

`refresh_single_feed` envolve todo o processamento de entradas num único `try/except`. Se qualquer operação dentro do loop de entradas falhar (ex: `content` em formato inesperado, `published_parsed` ausente), a exceção propaga para o handler externo, setando `last_exception`. O feed inteiro é marcado como falho — mesmo que o HTTP e o parsing do feed tenham funcionado, e mesmo que a maioria das entradas fosse válida.

## Goals / Non-Goals

**Goals:**
- Isolar cada entrada com try/except próprio — entradas problematicas são ignoradas, não abortam o refresh
- Salvar feed metadata (título, link, updated) ANTES de processar entradas, para garantir que ao menos o cabeçalho do feed seja persistido
- Exibir a mensagem de erro real na SnackBar (não mensagem genérica)
- Logging do erro real via `print` ou `logging` para debug

**Non-Goals:**
- Não alterar o modelo de dados
- Não adicionar novas dependências
- Não modificar `refresh_all_feeds`

## Decisions

| Decisão | Opção | Alternativa | Razão |
|---------|-------|-------------|-------|
| Onde colocar try/except por entrada | Dentro do loop, em volta da criação do Entry | No `entry_data.get("content")` específico | Mais abrangente; qualquer problema em qualquer campo da entrada é isolado |
| Ordem: metadata antes ou depois das entradas | Antes (commit separado) | Depois | Garante que ao menos título/link do feed sejam salvos mesmo se todas entradas falharem |
| Como mostrar erro na SnackBar | `content=ft.Text(str(feed.last_exception))` | Mensagem fixa | Dá visibilidade real do problema ao usuário |

## Risks / Trade-offs

- [Entradas ignoradas silenciosamente] → Sem logging, o usuário não sabe que entradas foram puladas. Mitigação: print do erro de cada entrada ignorada.
- [Dois commits por feed] → Leve overhead, mas aceitável para operação única de adição.
