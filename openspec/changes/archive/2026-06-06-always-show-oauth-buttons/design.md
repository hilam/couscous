## Context

Atualmente os botões OAuth (Google e GitHub) nas telas de `/login` e `/register` são renderizados condicionalmente: só aparecem se as credenciais do provider estiverem configuradas via variáveis de ambiente. Sem credenciais, o botão simplesmente não é renderizado, sem nenhum feedback ao usuário.

A lógica de criação desses botões está duplicada em dois arquivos: `login_view.py:11-40` e `register_view.py:11-40` — exatamente o mesmo código de 37 linhas.

## Goals / Non-Goals

**Goals:**
- Botões OAuth sempre visíveis no `/login` e `/register`, independentemente da configuração
- Ao clicar em provider não configurado, exibir mensagem de erro (já existe a lógica)
- Extrair código duplicado para um controle compartilhado em `app/controls/`

**Non-Goals:**
- Alterar o fluxo OAuth em si (callback, token, user creation)
- Adicionar novos providers OAuth
- Alterar `.env.sample`
- Extrair a configuração OAuth do módulo `database/service/config.py`

## Decisions

### 1. Remover a guarda `is_provider_available()` em vez de modificá-la

**Escolha:** Simplesmente remover o `if not oauth_service.is_provider_available(provider): continue` da função `_oauth_buttons()`.

**Alternativa considerada:** Mudar `is_provider_available()` para retornar sempre `True`, mantendo a chamada. Rejeitada porque a função ainda é usada em outros contextos e manter uma chamada que não filtra nada é enganoso.

**Fundamento:** A função `get_authorization_url()` já levanta `ValueError` quando o provider não está configurado. O `_oauth_click()` já captura essa exceção e exibe a mensagem no `error_text`. Basta deixar o fluxo seguir naturalmente.

### 2. Função compartilhada, não classe

**Escolha:** Criar uma função `get_oauth_buttons(page, error_text) -> list[ft.Control]` em `app/controls/oauth_buttons.py`, seguindo o padrão existente de outras funções utilitárias no projeto.

**Alternativa considerada:** Criar uma classe `OAuthButtons(ft.UserControl)` ou `OAuthButtons(ft.Container)`. Rejeitada porque overkill: o controle é uma lista simples de botões, não precisa de estado interno ou ciclo de vida. O `_oauth_click` pode ser uma função privada no mesmo módulo.

**Fundamento:** Manter simplicidade. As views usam o retorno como `form_controls.extend(get_oauth_buttons(...))`, exatamente como já fazem hoje.

### 3. Mensagem de erro já existe, sem nova lógica

**Escolha:** Nenhuma alteração na lógica de erro. O `ValueError("OAuth provider 'X' is not configured")` levantado por `get_authorization_url()` já é capturado e exibido.

**Fundamento:** Mudança mínima. A mensagem "OAuth provider 'google' is not configured" é suficientemente informativa para o usuário saber que precisa configurar.

## Risks / Trade-offs

- **Baixo risco**: Mudança apenas na camada de apresentação. Nenhuma alteração em modelo de dados, banco, ou fluxo OAuth.
- **Trade-off UX**: A mensagem de erro atual está em inglês ("OAuth provider 'google' is not configured") enquanto o resto da UI está em português. Isso é aceitável por ora — trocar a mensagem pode ser feito em mudança futura.
- **Trade-off duplicação de configuração**: O `oauth_service` ainda lê config via `from database.service.config import ...` como atributos de módulo, o que acopla testes. Isso está documentado como débito técnico a ser resolvido separadamente.
