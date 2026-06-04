## Context

Os formulários de login e registro em `login_view.py` e `register_view.py` usam `TextField` sem `on_submit`. Em Flet, `on_submit` é chamado quando o usuário pressiona Enter no campo. Basta adicionar o handler a cada campo.

## Goals / Non-Goals

**Goals:**
- Enter no campo de senha → submete o formulário
- Enter no campo de nome → move foco para o campo de senha
- Mesmo comportamento nos formulários de login e registro

**Non-Goals:**
- Não alterar a lógica de submissão
- Não alterar o layout ou estilo

## Decisions

| Decisão | Opção | Alternativa | Razão |
|---------|-------|-------------|-------|
| Handler do campo nome | `lambda e: password_field.focus()` | Também submeter | Foco no próximo campo é comportamento padrão de formulários |
| Handler do campo senha | `submit` (mesma função do botão) | Função separada | Reuso, consistência |

## Risks / Trade-offs

Nenhum risco significativo — mudança puramente aditiva em callbacks de UI.
