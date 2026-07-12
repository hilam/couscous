## Capability: database-cleanup

### Test: Botão de limpeza manual na tela de configurações
**Traces**: `specs/database-cleanup/spec.md` → Requirement: Usuário pode limpar entries antigas manualmente
- **GIVEN** o usuário está autenticado e na tela `/about` (settings)
- **WHEN** o usuário clica no botão "Limpar artigos antigos"
- **THEN** o diálogo de limpeza (`AlertDialog`) é aberto com um `Dropdown` de seleção de período

### Test: CRITICAL — Limpeza manual remove apenas entries não-importantes
**Traces**: `specs/database-cleanup/spec.md` → Requirement: Usuário pode limpar entries antigas manualmente
- **GIVEN** o usuário tem 10 entries com mais de 30 dias, sendo 3 marcadas como `important=1`
- **WHEN** o usuário executa limpeza com período de 30 dias
- **THEN** as 7 entries não-importantes são removidas
- **AND** as 3 entries importantes permanecem no banco
- **AND** as `EntryTag` das 7 entries removidas são excluídas em cascata

### Test: Limpeza sem entries elegíveis
**Traces**: `specs/database-cleanup/spec.md` → Requirement: Usuário pode limpar entries antigas manualmente
- **GIVEN** o usuário não tem entries com mais de 7 dias
- **WHEN** o usuário seleciona "7 dias" no diálogo de limpeza
- **THEN** o sistema exibe "Nenhum artigo para remover"
- **AND** a remoção não é executada

### Test: Contagem de entries ao selecionar período
**Traces**: `specs/database-cleanup/spec.md` → Requirement: Diálogo de limpeza mostra contagem antes da confirmação
- **GIVEN** o usuário tem 42 entries não-importantes com mais de 90 dias
- **WHEN** o usuário seleciona "90 dias" no dropdown
- **THEN** o diálogo exibe "42 artigos serão removidos"
- **AND** a contagem exclui entries com `important=1`

### Test: Contagem zero desabilita botão de confirmação
**Traces**: `specs/database-cleanup/spec.md` → Requirement: Diálogo de limpeza mostra contagem antes da confirmação
- **GIVEN** o usuário não tem entries elegíveis para o período selecionado
- **WHEN** a contagem retorna zero
- **THEN** o botão "Limpar" fica desabilitado

### Test: Dropdown exibe as quatro opções de período
**Traces**: `specs/database-cleanup/spec.md` → Requirement: Opções de período predefinidas
- **GIVEN** o diálogo de limpeza está aberto
- **WHEN** o usuário interage com o dropdown
- **THEN** as opções exibidas são: "7 dias", "30 dias", "90 dias", "365 dias"
- **AND** nenhuma outra opção está presente

### Test: CRITICAL — Limpeza em background recarrega lista de feeds
**Traces**: `specs/database-cleanup/spec.md` → Requirement: Limpeza em background com atualização da view
- **GIVEN** o usuário está na rota `/feeds` e uma limpeza em background é disparada
- **WHEN** a limpeza é concluída
- **THEN** a lista de entries é recarregada (`page.update()`)
- **AND** entries removidas não aparecem mais na lista

### Test: CRITICAL — Limpeza remove entry que o usuário está visualizando
**Traces**: `specs/database-cleanup/spec.md` → Requirement: Limpeza em background com atualização da view
- **GIVEN** o usuário está na rota `/entry/42` e a entry 42 é removida pela limpeza
- **WHEN** a limpeza é concluída
- **THEN** o sistema redireciona para `/feeds`

### Test: Configurar retenção automática salva no banco
**Traces**: `specs/database-cleanup/spec.md` → Requirement: Configuração de limpeza automática por usuário
- **GIVEN** o usuário está na tela de configurações com `auto_cleanup_days=None`
- **WHEN** o usuário seleciona "30 dias" no dropdown "Limpeza automática"
- **THEN** o banco é atualizado com `auto_cleanup_days=30`
- **AND** a preferência persiste entre sessões

### Test: Desligar limpeza automática
**Traces**: `specs/database-cleanup/spec.md` → Requirement: Configuração de limpeza automática por usuário
- **GIVEN** o usuário tem `auto_cleanup_days=30`
- **WHEN** o usuário seleciona "Desligado" no dropdown
- **THEN** `auto_cleanup_days` é salvo como `None`
- **AND** na próxima inicialização, nenhuma limpeza automática é executada

### Test: CRITICAL — Limpeza automática na inicialização
**Traces**: `specs/database-cleanup/spec.md` → Requirement: Configuração de limpeza automática por usuário
- **GIVEN** o usuário tem `auto_cleanup_days=30` e 15 entries elegíveis para remoção
- **WHEN** o usuário faz login
- **THEN** a limpeza é executada em background (não bloqueia o primeiro paint)
- **AND** ao concluir, um snackbar exibe "🧹 Limpeza automática: 15 artigos antigos removidos"
- **AND** a view corrente é atualizada

### Test: Limpeza automática sem entries para remover
**Traces**: `specs/database-cleanup/spec.md` → Requirement: Configuração de limpeza automática por usuário
- **GIVEN** o usuário tem `auto_cleanup_days=7` mas nenhuma entry elegível
- **WHEN** o usuário faz login e a limpeza é executada
- **THEN** nenhum snackbar é exibido

### Test: Migration remove FeedMetadata
**Traces**: `specs/database-cleanup/spec.md` → Requirement: Remoção do modelo FeedMetadata
- **GIVEN** a tabela `feed_metadata` existe no banco
- **WHEN** a migration é aplicada (`make db-migrate-up`)
- **THEN** a tabela `feed_metadata` é removida
- **AND** a classe `FeedMetadata` não existe mais em `database/models/couscous.py`
- **AND** `make typecheck` e `make lint` passam sem erros

### Test: CRITICAL — Limpeza isolada por usuário
**Traces**: `specs/database-cleanup/spec.md` → Requirement: Escopo multi-usuário na limpeza
- **GIVEN** o banco tem entries do usuário A (idas=100 dias) e do usuário B (idas=100 dias)
- **WHEN** o usuário A executa limpeza com período de 30 dias
- **THEN** as entries do usuário A com mais de 30 dias são removidas
- **AND** as entries do usuário B permanecem intactas

### Test: EDGE — Entries exatamente no limite do período (boundary)
**Traces**: `specs/database-cleanup/spec.md` → (edge case)
- **GIVEN** uma entry com `first_updated_epoch` exatamente 30 dias atrás (mesmo segundo)
- **WHEN** o usuário executa limpeza com período de 30 dias
- **THEN** a entry é removida (critério: `first_updated_epoch < cutoff`, estritamente menor)

### Test: EDGE — Double-click no botão de limpeza
**Traces**: `specs/database-cleanup/spec.md` → (edge case)
- **GIVEN** o diálogo de limpeza está aberto com período selecionado
- **WHEN** o usuário clica duas vezes rapidamente no botão "Limpar"
- **THEN** apenas uma operação de limpeza é executada
- **AND** o sistema não lança exceção de sessão concorrente

### Test: EDGE — Logout durante limpeza em background
**Traces**: `specs/database-cleanup/spec.md` → (edge case)
- **GIVEN** a limpeza automática está em execução em background
- **WHEN** o usuário faz logout
- **THEN** a operação de limpeza conclui ou é cancelada sem erro
- **AND** o app não crasha

### Test: EDGE — Volume grande de entries (performance)
**Traces**: `specs/database-cleanup/spec.md` → (edge case)
- **GIVEN** o usuário tem 10.000 entries elegíveis para remoção
- **WHEN** a limpeza é executada
- **THEN** a operação conclui em tempo razoável (< 5 segundos)
- **AND** a UI permanece responsiva durante a execução

### Test: EDGE — Entry com first_updated_epoch nulo
**Traces**: `specs/database-cleanup/spec.md` → (edge case)
- **GIVEN** uma entry com `first_updated_epoch = NULL` e `important = 0`
- **WHEN** a limpeza é executada com qualquer período
- **THEN** a entry é removida (NULL é tratado como data antiga)
- **AND** entries com `first_updated_epoch = NULL` e `important = 1` são preservadas

### Test: EDGE — Entry importante com tags não são removidas
**Traces**: `specs/database-cleanup/spec.md` → (edge case)
- **GIVEN** uma entry com `important=1` e 3 `EntryTag` associadas, com mais de 365 dias
- **WHEN** o usuário executa limpeza com período de 365 dias
- **THEN** a entry e suas tags permanecem intactas

---

## Capability: copy-link

### Test: CRITICAL — Copiar link de entry com sucesso
**Traces**: `specs/copy-link/spec.md` → Requirement: Botão de copiar link na visualização de entry
- **GIVEN** o usuário está visualizando uma entry com `link = "https://example.com/article"`
- **WHEN** o usuário clica no botão de cópia no `AppBar`
- **THEN** `navigator.clipboard.writeText("https://example.com/article")` é executado via JS
- **AND** um snackbar "Link copiado!" é exibido

### Test: Falha ao copiar link exibe banner de erro no DOM
**Traces**: `specs/copy-link/spec.md` → Requirement: Botão de copiar link na visualização de entry
- **GIVEN** o navegador bloqueia `navigator.clipboard.writeText` (ex: contexto não seguro simulado)
- **WHEN** o usuário clica no botão de cópia
- **THEN** o snackbar "Link copiado!" é exibido (comportamento Python)
- **AND** um banner vermelho com "⚠️ Erro ao copiar link — verifique as permissões do navegador" aparece no canto inferior direito
- **AND** o banner desaparece após 5 segundos

### Test: CRITICAL — Copiar link do ArticleCard
**Traces**: `specs/copy-link/spec.md` → Requirement: Botão de copiar link no ArticleCard
- **GIVEN** uma lista de entries é exibida com `ArticleCard` para cada entry
- **WHEN** o usuário clica no botão de cópia em um `ArticleCard`
- **THEN** o link da entry associada ao card é copiado
- **AND** o snackbar "Link copiado!" é exibido

### Test: Botão de cópia visível no AppBar da entry
**Traces**: `specs/copy-link/spec.md` → Requirement: Posicionamento consistente do botão
- **GIVEN** o usuário está na rota `/entry/42` com uma entry que tem link
- **WHEN** a view é renderizada
- **THEN** o `AppBar.actions` contém um `IconButton` com `ft.Icons.CONTENT_COPY`
- **AND** o botão está posicionado entre as ações existentes (estrela/importante)

### Test: Botão de cópia visível no ArticleCard
**Traces**: `specs/copy-link/spec.md` → Requirement: Posicionamento consistente do botão
- **GIVEN** o usuário está na rota `/feeds` com entries que possuem link
- **WHEN** a lista é renderizada
- **THEN** cada `ArticleCard` contém um `IconButton` com `ft.Icons.CONTENT_COPY` no `subtitle`
- **AND** o botão está dentro de uma `Row` de ações

### Test: Entry sem link não mostra botão de cópia
**Traces**: `specs/copy-link/spec.md` → Requirement: Entry sem link não exibe botão
- **GIVEN** uma entry com `link = None`
- **WHEN** a entry é exibida no `entry_view` e no `ArticleCard`
- **THEN** o botão de cópia não é renderizado em nenhum dos dois locais

### Test: EDGE — Entry com link vazio (string vazia)
**Traces**: `specs/copy-link/spec.md` → (edge case)
- **GIVEN** uma entry com `link = ""`
- **WHEN** a entry é exibida
- **THEN** o botão de cópia não é renderizado

### Test: EDGE — URL com caracteres especiais
**Traces**: `specs/copy-link/spec.md` → (edge case)
- **GIVEN** uma entry com `link = 'https://example.com/?q=hello"world&x=<script>'`
- **WHEN** o usuário clica no botão de cópia
- **THEN** a URL é copiada corretamente (escapada via `json.dumps`)
- **AND** o JS não quebra com erro de sintaxe

### Test: EDGE — Plataforma não-web (desktop nativo)
**Traces**: `specs/copy-link/spec.md` → Requirement: Entry sem link ou plataforma não-web não exibe botão
- **GIVEN** o app está rodando em plataforma nativa (`page.web = False`)
- **WHEN** qualquer view com entries é renderizada
- **THEN** o botão de copiar link não é renderizado em nenhum local (entry_view nem ArticleCard)

### Test: EDGE — Double-click no botão de cópia
**Traces**: `specs/copy-link/spec.md` → (edge case)
- **GIVEN** o usuário está visualizando uma entry
- **WHEN** o usuário clica duas vezes rapidamente no botão de cópia
- **THEN** dois snackbars "Link copiado!" podem aparecer (aceitável)
- **AND** o app não crasha

---

## Edge Cases

| # | Caso | Risco |
|---|------|-------|
| EC1 | `auto_cleanup_days` com valor inválido no banco (ex: 0, -1, "abc") | Configuração corrompida manualmente |
| EC2 | Limpeza com `first_updated_epoch = NULL` em alguma entry | Query pode ignorar ou falhar |
| EC3 | Usuário fecha o diálogo de limpeza enquanto a contagem está carregando | Task assíncrona pendente |
| EC4 | Dois diálogos de limpeza abertos simultaneamente (abrir, fechar, abrir rápido) | Referências stale |
| EC5 | `page.run_javascript` chamado quando `page` é `None` ou `page.web` é `False` | App desktop, não web |

---

## Integration Points

| # | Ponto | Validação necessária |
|---|-------|---------------------|
| IP1 | `settings_view` agora tem dropdown de tema, slider de fonte, dropdown de limpeza automática E botão de limpeza manual | Layout não quebra com os novos controles; scroll funciona se necessário |
| IP2 | Limpeza na inicialização + navegação imediata do usuário | O snackbar de limpeza não interfere na navegação; `page.update()` após limpeza não causa flicker |
| IP3 | `settings_service` estendido com `auto_cleanup_days` | Funções existentes (`get_settings`, `save_settings`) continuam funcionando; novos campos não quebram queries antigas |
| IP4 | Migration adiciona coluna `auto_cleanup_days` e remove `feed_metadata` | Rollback funciona (`make db-migrate-down`); migration é idempotente |
| IP5 | Botão de cópia coexiste com botão de estrela/importante no `AppBar` | Ambos os botões são clicáveis, sem sobreposição de eventos |

---

## Review Notes

- **RESOLVIDO**: `specs/database-cleanup/spec.md` → Scenario: Limpeza automática na inicialização — "após login bem-sucedido" DEVE cobrir tanto login por senha quanto OAuth. O `app_run` não tem ponto único pós-autenticação; a implementação precisará garantir que a limpeza dispare uma única vez após o primeiro `state.user` ser definido, independentemente do método de login.
